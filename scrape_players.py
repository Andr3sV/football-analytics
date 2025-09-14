#!/usr/bin/env python3
"""
Direct scraper for Transfermarkt player data using requests and BeautifulSoup
"""
import requests
import json
import csv
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd

# Competition codes and their URL slugs
COMPETITIONS = {
    "ES1": "laliga",
    "PO1": "ligaportugal", 
    "FR1": "ligue1",
    "L1": "bundesliga",
    "SE1": "allsvenskan",
    "BE1": "proleague",
    "PL1": "ekstraklasa",
    "KOR1": "kleague1",
    "SA1": "saudiproleague",
    "QA1": "starsleague",
    "IT1": "seriea",
    "TS1": "fortunaliga",
    "NO1": "eliteserien",
    "GB1": "premierleague",
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

def get_players_from_club(club_url, club_name, competition, season=None):
    """Extract player data from club page"""
    print(f"Fetching players from {club_name}")
    
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
        
        # Look for player links in squad table
        for row in soup.select('table.items tbody tr'):
            player_link = row.select_one('td:nth-child(2) a')
            if player_link and ('/profil/spieler/' in player_link.get('href', '') or '/profil-spieler/' in player_link.get('href', '')):
                player_url = urljoin(club_url, player_link.get('href', ''))
                player_name = player_link.get_text(strip=True)
                
                # Get additional player data
                player_data = get_player_details(player_url, player_name, club_name, competition)
                if player_data:
                    players.append(player_data)
        
        print(f"Found {len(players)} players in {club_name}")
        return players
        
    except Exception as e:
        print(f"Error fetching players from {club_name}: {e}")
        return []

def get_player_details(player_url, player_name, club_name, competition):
    """Extract detailed player information"""
    try:
        response = requests.get(player_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        player_data = {
            'full_name': player_name,
            'club_name': club_name,
            'competition': competition,
            'profile_url': player_url,
            'relative_profile_url': '/' + '/'.join(player_url.split('/')[3:]),
        }
        
        # Extract data from info table
        info_table = soup.select_one('.info-table, .data-header__details')
        if info_table:
            rows = info_table.select('tr')
            for row in rows:
                cells = row.select('td, th')
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    if 'date of birth' in label or 'born' in label:
                        player_data['date_of_birth'] = value
                        # Extract age if in parentheses
                        age_match = re.search(r'\((\d+)\)', value)
                        if age_match:
                            player_data['age'] = age_match.group(1)
                    
                    elif 'place of birth' in label:
                        player_data['place_of_birth'] = value
                        if ',' in value:
                            parts = value.split(',', 1)
                            player_data['city_of_birth'] = parts[0].strip()
                            player_data['country_of_birth'] = parts[1].strip()
                    
                    elif 'height' in label:
                        height_match = re.search(r'(\d+\.?\d*)\s*m', value)
                        if height_match:
                            player_data['height_cm'] = int(float(height_match.group(1)) * 100)
                    
                    elif 'citizenship' in label or 'nationality' in label:
                        # Get nationality from flag images
                        flags = row.select('img')
                        nationalities = [img.get('alt', '') for img in flags if img.get('alt')]
                        player_data['nationalities'] = nationalities
                    
                    elif 'position' in label:
                        player_data['position'] = value
                    
                    elif 'agent' in label:
                        player_data['agency'] = value
                    
                    elif 'current club' in label:
                        player_data['current_club'] = value
                    
                    elif 'foot' in label:
                        player_data['dominant_foot'] = value
                    
                    elif 'joined' in label:
                        player_data['club_joined_date'] = value
                    
                    elif 'contract' in label and 'expires' in label:
                        player_data['contract_expires'] = value
                    
                    elif 'contract' in label and 'extension' in label:
                        player_data['last_contract_extension'] = value
                    
                    elif 'outfitter' in label or 'kit' in label:
                        player_data['equipment_brand'] = value
        
        # Get social media links
        social_links = []
        for link in soup.select('a[href*="twitter"], a[href*="instagram"], a[href*="facebook"]'):
            social_links.append(link.get('href'))
        player_data['social_links'] = social_links
        
        # Get youth clubs/training clubs
        youth_section = soup.select_one('th:contains("Youth clubs"), span:contains("Youth clubs")')
        if youth_section:
            parent = youth_section.find_parent()
            if parent:
                youth_text = parent.get_text(strip=True)
                youth_clubs = [club.strip() for club in youth_text.split(',') if club.strip()]
                player_data['training_clubs'] = youth_clubs
        
        return player_data
        
    except Exception as e:
        print(f"Error fetching details for {player_name}: {e}")
        return None

def main():
    """Main scraping function"""
    season = 2024
    all_players = []
    
    # Start with just a few major leagues for testing
    test_competitions = {
        "ES1": "laliga",
        "GB1": "premierleague", 
        "IT1": "seriea",
        "FR1": "ligue1",
        "L1": "bundesliga"
    }
    
    print("Starting player data collection...")
    print(f"Target season: {season}")
    print(f"Competitions: {list(test_competitions.keys())}")
    
    for comp_code, comp_slug in test_competitions.items():
        print(f"\n=== Processing {comp_slug} ({comp_code}) ===")
        
        # Get clubs from competition
        clubs = get_clubs_from_competition(comp_code, season)
        
        # Get players from each club (limit to 2 clubs per league for speed)
        for club in clubs[:2]:
            players = get_players_from_club(club['url'], club['name'], comp_code, season)
            all_players.extend(players)
            
            # Be respectful with delays
            time.sleep(3)
        
        # Delay between competitions
        time.sleep(5)
    
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
        print(df.head().to_string())
        
    else:
        print("No player data collected!")

if __name__ == "__main__":
    main()
