#!/usr/bin/env python3
"""
Quick test scraper for LaLiga only
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def get_laliga_players():
    """Get players from LaLiga 2024"""
    url = "https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1/saison_id/2024"
    print(f"Fetching LaLiga clubs from: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        clubs = []
        
        # Get first 3 clubs
        for i, row in enumerate(soup.select('table.items tbody tr')[:3]):
            club_link = row.select_one('td:nth-child(2) a')
            if club_link:
                club_url = urljoin(url, club_link.get('href', ''))
                club_name = club_link.get_text(strip=True)
                clubs.append({'name': club_name, 'url': club_url})
                print(f"Found club {i+1}: {club_name}")
        
        all_players = []
        
        # Get players from each club
        for club in clubs:
            print(f"\nFetching players from {club['name']}...")
            
            try:
                club_response = requests.get(club['url'], headers=HEADERS, timeout=30)
                club_response.raise_for_status()
                
                club_soup = BeautifulSoup(club_response.content, 'html.parser')
                
                # Get first 10 players from squad table
                for i, row in enumerate(club_soup.select('table.items tbody tr')[:10]):
                    cells = row.select('td')
                    if len(cells) >= 6:
                        try:
                            player_link = cells[1].select_one('a')
                            if player_link and '/profil/spieler/' in player_link.get('href', ''):
                                player_name = player_link.get_text(strip=True)
                                position = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                                age = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                                nationality = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                                market_value = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                                
                                player_data = {
                                    'full_name': player_name,
                                    'club_name': club['name'],
                                    'competition': 'ES1',
                                    'position': position,
                                    'age': age,
                                    'nationality': nationality,
                                    'market_value': market_value,
                                    'season': 2024
                                }
                                
                                all_players.append(player_data)
                                print(f"  - {player_name} ({position})")
                                
                        except Exception as e:
                            print(f"  Error parsing player: {e}")
                            continue
                            
            except Exception as e:
                print(f"Error fetching players from {club['name']}: {e}")
                continue
        
        return all_players
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    print("=== Quick LaLiga Player Data Collection ===")
    players = get_laliga_players()
    
    if players:
        df = pd.DataFrame(players)
        csv_file = 'laliga_players_sample.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"\n=== Results ===")
        print(f"Total players collected: {len(players)}")
        print(f"Clubs: {df['club_name'].unique()}")
        print(f"Data saved to: {csv_file}")
        
        print(f"\n=== Sample Data ===")
        print(df.to_string())
        
    else:
        print("No players collected!")

if __name__ == "__main__":
    main()
