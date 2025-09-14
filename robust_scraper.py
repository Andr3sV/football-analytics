#!/usr/bin/env python3
"""
Robust scraper that uses multiple strategies to collect player data
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random

# Different user agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
]

def get_headers():
    """Get random headers to avoid detection"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

def get_competition_data():
    """Get data from multiple competitions using different approaches"""
    competitions = {
        "ES1": "https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1/saison_id/2024",
        "GB1": "https://www.transfermarkt.com/premierleague/startseite/wettbewerb/GB1/saison_id/2024", 
        "IT1": "https://www.transfermarkt.com/seriea/startseite/wettbewerb/IT1/saison_id/2024",
        "FR1": "https://www.transfermarkt.com/ligue1/startseite/wettbewerb/FR1/saison_id/2024",
        "L1": "https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/L1/saison_id/2024"
    }
    
    all_players = []
    
    for comp_code, url in competitions.items():
        print(f"\n=== Processing {comp_code} ===")
        print(f"URL: {url}")
        
        try:
            # Try to get competition page
            response = requests.get(url, headers=get_headers(), timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Get clubs from competition table
                clubs = []
                for row in soup.select('table.items tbody tr')[:5]:  # Limit to 5 clubs
                    club_link = row.select_one('td:nth-child(2) a')
                    if club_link:
                        club_name = club_link.get_text(strip=True)
                        club_url = urljoin(url, club_link.get('href', ''))
                        clubs.append({'name': club_name, 'url': club_url})
                        print(f"  Found club: {club_name}")
                
                # Get players from each club
                for club in clubs:
                    print(f"  Getting players from {club['name']}...")
                    players = get_players_from_club(club, comp_code)
                    all_players.extend(players)
                    
                    # Random delay to avoid being blocked
                    time.sleep(random.uniform(2, 5))
                    
            else:
                print(f"  Failed to get competition page: {response.status_code}")
                
        except Exception as e:
            print(f"  Error processing {comp_code}: {e}")
            continue
        
        # Delay between competitions
        time.sleep(random.uniform(3, 7))
    
    return all_players

def get_players_from_club(club, competition):
    """Get players from a club page"""
    players = []
    
    try:
        # Try different URL patterns
        club_urls = [
            club['url'],
            club['url'].replace('/startseite/', '/kader/'),
            club['url'] + '/kader'
        ]
        
        for club_url in club_urls:
            try:
                print(f"    Trying: {club_url}")
                response = requests.get(club_url, headers=get_headers(), timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for player table
                    player_table = soup.select_one('table.items')
                    if player_table:
                        print(f"    Found player table with {len(player_table.select('tbody tr'))} rows")
                        
                        for row in player_table.select('tbody tr')[:15]:  # Limit to 15 players per club
                            try:
                                cells = row.select('td')
                                if len(cells) >= 4:
                                    # Extract player data
                                    player_name = ""
                                    position = ""
                                    age = ""
                                    nationality = ""
                                    market_value = ""
                                    
                                    # Try to find player name and link
                                    name_cell = cells[1] if len(cells) > 1 else cells[0]
                                    player_link = name_cell.select_one('a')
                                    
                                    if player_link and ('/profil/spieler/' in player_link.get('href', '') or '/profil-spieler/' in player_link.get('href', '')):
                                        player_name = player_link.get_text(strip=True)
                                        
                                        # Extract other data
                                        if len(cells) > 2:
                                            position = cells[2].get_text(strip=True)
                                        if len(cells) > 3:
                                            age = cells[3].get_text(strip=True)
                                        if len(cells) > 4:
                                            nationality = cells[4].get_text(strip=True)
                                        if len(cells) > 5:
                                            market_value = cells[5].get_text(strip=True)
                                        
                                        # Get nationality from flag if available
                                        nationality_flags = cells[4].select('img') if len(cells) > 4 else []
                                        if nationality_flags:
                                            nationality = nationality_flags[0].get('alt', nationality)
                                        
                                        if player_name:
                                            player_data = {
                                                'full_name': player_name,
                                                'club_name': club['name'],
                                                'competition': competition,
                                                'position': position,
                                                'age': age,
                                                'nationality': nationality,
                                                'market_value': market_value,
                                                'season': 2024
                                            }
                                            
                                            players.append(player_data)
                                            print(f"      - {player_name} ({position})")
                                            
                            except Exception as e:
                                print(f"      Error parsing player row: {e}")
                                continue
                        
                        break  # Success, no need to try other URLs
                    else:
                        print(f"    No player table found")
                        
                elif response.status_code == 403:
                    print(f"    Access forbidden (403)")
                    break
                else:
                    print(f"    Status: {response.status_code}")
                    
            except Exception as e:
                print(f"    Error with URL {club_url}: {e}")
                continue
                
    except Exception as e:
        print(f"  Error getting players from {club['name']}: {e}")
    
    return players

def main():
    print("=== Robust Player Data Collection ===")
    print("Collecting from: LaLiga, Premier League, Serie A, Ligue 1, Bundesliga")
    
    all_players = get_competition_data()
    
    if all_players:
        df = pd.DataFrame(all_players)
        csv_file = 'players_complete_data.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"Total players collected: {len(all_players)}")
        print(f"Competitions: {df['competition'].value_counts().to_dict()}")
        print(f"Clubs: {df['club_name'].nunique()}")
        print(f"Data saved to: {csv_file}")
        
        print(f"\n=== Sample Data ===")
        print(df.head(15).to_string())
        
        print(f"\n=== Players by Competition ===")
        for comp, count in df['competition'].value_counts().items():
            print(f"{comp}: {count} players")
            
    else:
        print("No players collected!")

if __name__ == "__main__":
    main()
