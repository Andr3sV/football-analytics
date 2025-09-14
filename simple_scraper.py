#!/usr/bin/env python3
"""
Simplified scraper that collects basic player data from club squad pages
"""
import requests
import json
import csv
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

# Competition codes and their URL slugs
COMPETITIONS = {
    "ES1": "laliga",
    "GB1": "premierleague", 
    "IT1": "seriea",
    "FR1": "ligue1",
    "L1": "bundesliga",
    "PO1": "ligaportugal",
    "BE1": "proleague",
    "PL1": "ekstraklasa",
    "KOR1": "kleague1",
    "SA1": "saudiproleague",
    "QA1": "starsleague",
    "TS1": "fortunaliga",
    "NO1": "eliteserien",
    "SC1": "premiership",
    "BRA1": "seriea",
    "COL1": "categoriaprimeraa",
    "SW1": "superleague",
    "TR1": "superlig",
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def get_competition_url(comp_code, season=None):
    """Get the correct URL for a competition"""
    slug = COMPETITIONS.get(comp_code, comp_code.lower())
    if season:
        return f"https://www.transfermarkt.com/{slug}/startseite/wettbewerb/{comp_code}/saison_id/{season}"
    else:
        return f"https://www.transfermarkt.com/{slug}/startseite/wettbewerb/{comp_code}"

def get_clubs_from_competition(comp_code, season=None):
    """Extract club URLs from competition page"""
    url = get_competition_url(comp_code, season)
    print(f"Fetching clubs from {comp_code}: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        clubs = []
        
        # Look for club links in the main table
        for row in soup.select('table.items tbody tr'):
            club_link = row.select_one('td:nth-child(2) a')
            if club_link:
                club_url = urljoin(url, club_link.get('href', ''))
                club_name = club_link.get_text(strip=True)
                clubs.append({
                    'name': club_name,
                    'url': club_url,
                    'competition': comp_code
                })
        
        print(f"Found {len(clubs)} clubs in {comp_code}")
        return clubs
        
    except Exception as e:
        print(f"Error fetching clubs from {comp_code}: {e}")
        return []

def get_players_from_club_squad(club_url, club_name, competition, season=None):
    """Extract basic player data from club squad page"""
    print(f"Fetching squad from {club_name}")
    
    try:
        # Add season parameter if provided
        if season and '?' not in club_url:
            club_url += f'?saison_id={season}'
        elif season and '?' in club_url:
            club_url += f'&saison_id={season}'
            
        response = requests.get(club_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        players = []
        
        # Look for player rows in squad table
        for row in soup.select('table.items tbody tr'):
            cells = row.select('td')
            if len(cells) >= 6:  # Ensure we have enough columns
                try:
                    # Extract basic info from table
                    player_name_cell = cells[1]  # Usually second column
                    player_link = player_name_cell.select_one('a')
                    
                    if player_link and ('/profil/spieler/' in player_link.get('href', '') or '/profil-spieler/' in player_link.get('href', '')):
                        player_name = player_link.get_text(strip=True)
                        player_url = urljoin(club_url, player_link.get('href', ''))
                        
                        # Extract additional data from other columns
                        position = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                        age = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                        nationality = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                        market_value = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                        
                        # Get nationality from flag images if available
                        nationality_flags = cells[4].select('img') if len(cells) > 4 else []
                        nationality_from_flag = [img.get('alt', '') for img in nationality_flags if img.get('alt')]
                        
                        player_data = {
                            'full_name': player_name,
                            'club_name': club_name,
                            'competition': competition,
                            'position': position,
                            'age': age,
                            'nationality': nationality,
                            'nationality_from_flag': nationality_from_flag[0] if nationality_from_flag else nationality,
                            'market_value': market_value,
                            'profile_url': player_url,
                            'relative_profile_url': '/' + '/'.join(player_url.split('/')[3:]) if player_url else "",
                            'season': season
                        }
                        
                        players.append(player_data)
                        
                except Exception as e:
                    print(f"Error parsing player row: {e}")
                    continue
        
        print(f"Found {len(players)} players in {club_name}")
        return players
        
    except Exception as e:
        print(f"Error fetching squad from {club_name}: {e}")
        return []

def main():
    """Main scraping function"""
    season = 2024
    all_players = []
    
    print("Starting player data collection...")
    print(f"Target season: {season}")
    print(f"Competitions: {list(COMPETITIONS.keys())}")
    
    for comp_code, comp_slug in COMPETITIONS.items():
        print(f"\n=== Processing {comp_slug} ({comp_code}) ===")
        
        # Get clubs from competition
        clubs = get_clubs_from_competition(comp_code, season)
        
        # Get players from each club (limit to 3 clubs per league for speed)
        for club in clubs[:3]:
            players = get_players_from_club_squad(club['url'], club['name'], comp_code, season)
            all_players.extend(players)
            
            # Be respectful with delays
            time.sleep(2)
        
        # Delay between competitions
        time.sleep(3)
    
    print(f"\n=== Collection Complete ===")
    print(f"Total players collected: {len(all_players)}")
    
    # Save to CSV
    if all_players:
        df = pd.DataFrame(all_players)
        csv_file = f'players_data_{season}.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"Data saved to {csv_file}")
        
        # Show summary
        print(f"\n=== Data Summary ===")
        print(f"Total players: {len(all_players)}")
        print(f"Competitions covered: {df['competition'].nunique()}")
        print(f"Clubs covered: {df['club_name'].nunique()}")
        print(f"Columns: {list(df.columns)}")
        
        # Show sample data
        print(f"\n=== Sample Data ===")
        print(df.head(10).to_string())
        
        # Show competition breakdown
        print(f"\n=== Players by Competition ===")
        comp_counts = df['competition'].value_counts()
        for comp, count in comp_counts.items():
            print(f"{comp}: {count} players")
        
    else:
        print("No player data collected!")

if __name__ == "__main__":
    main()
