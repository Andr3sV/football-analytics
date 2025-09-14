#!/usr/bin/env python3
"""
Full scraper to get ALL players from ALL requested leagues
"""
import requests
import pandas as pd
import time
import random
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ALL competition codes and their URL slugs
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

class FullTransfermarktScraper:
    def __init__(self):
        self.session = self._create_session()
        self.ua = UserAgent()
        self.successful_requests = 0
        self.failed_requests = 0
        self.all_players = []
        
    def _create_session(self):
        """Create a session with advanced retry and timeout strategies"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_random_headers(self):
        """Generate random headers to avoid detection"""
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'es-ES,es;q=0.9', 'de-DE,de;q=0.9']),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Sec-GPC': '1'
        }
    
    def _random_delay(self, min_delay=3, max_delay=10):
        """Add random delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        print(f"    Waiting {delay:.1f}s...")
        time.sleep(delay)
    
    def _make_request(self, url, max_retries=3):
        """Make a request with advanced anti-detection"""
        for attempt in range(max_retries):
            try:
                headers = self._get_random_headers()
                
                if attempt > 0:
                    self._random_delay(10, 20)
                
                print(f"    Attempt {attempt + 1}: {url}")
                
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=30,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    self.successful_requests += 1
                    return response
                elif response.status_code == 403:
                    print(f"    Blocked (403) - trying different approach...")
                    self._random_delay(15, 30)
                elif response.status_code == 429:
                    print(f"    Rate limited (429) - waiting longer...")
                    self._random_delay(60, 120)
                else:
                    print(f"    Status {response.status_code}")
                    
            except Exception as e:
                print(f"    Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    self._random_delay(10, 20)
        
        self.failed_requests += 1
        return None
    
    def get_competition_teams(self, comp_code, season=2024):
        """Get teams from competition"""
        slug = COMPETITIONS.get(comp_code, comp_code.lower())
        url = f"https://www.transfermarkt.com/{slug}/startseite/wettbewerb/{comp_code}/saison_id/{season}"
        
        print(f"Trying competition URL: {url}")
        response = self._make_request(url)
        
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            teams = []
            
            # Look for team links
            team_links = soup.select('table.items tbody tr td:nth-child(2) a')
            
            if team_links:
                print(f"    Found {len(team_links)} teams")
                
                for link in team_links:
                    team_name = link.get_text(strip=True)
                    team_url = urljoin(url, link.get('href', ''))
                    
                    if team_name and team_url:
                        teams.append({
                            'name': team_name,
                            'url': team_url,
                            'competition': comp_code
                        })
                
                print(f"    Successfully found {len(teams)} teams")
                return teams
            else:
                print(f"    No teams found")
                return []
        else:
            print(f"    Failed to get competition page")
            return []
    
    def get_team_players(self, team, comp_code, season=2024):
        """Get players from team"""
        team_name = team['name']
        team_url = team['url']
        
        print(f"  Getting players from {team_name}")
        
        # Try team URL with season
        url = f"{team_url}?saison_id={season}"
        response = self._make_request(url)
        
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            players = []
            
            # Look for player links
            player_links = soup.select('table.items tbody tr td:nth-child(2) a[href*="/profil/spieler/"]')
            
            if player_links:
                print(f"      Found {len(player_links)} players")
                
                for link in player_links:
                    player_name = link.get_text(strip=True)
                    player_url = urljoin(url, link.get('href', ''))
                    
                    if player_name and player_url:
                        # Extract additional data from the row
                        row = link.find_parent('tr')
                        if row:
                            cells = row.select('td')
                            
                            player_data = {
                                'full_name': player_name,
                                'team_name': team_name,
                                'competition': comp_code,
                                'profile_url': player_url,
                                'relative_profile_url': '/' + '/'.join(player_url.split('/')[3:]),
                                'season': season
                            }
                            
                            # Try to extract position, age, nationality
                            if len(cells) >= 3:
                                player_data['position'] = cells[2].get_text(strip=True)
                            if len(cells) >= 4:
                                player_data['age'] = cells[3].get_text(strip=True)
                            if len(cells) >= 5:
                                nationality_cell = cells[4]
                                player_data['nationality'] = nationality_cell.get_text(strip=True)
                                
                                # Try to get nationality from flag
                                flag_img = nationality_cell.select_one('img')
                                if flag_img:
                                    player_data['nationality'] = flag_img.get('alt', player_data['nationality'])
                            
                            players.append(player_data)
                
                print(f"      Successfully extracted {len(players)} players")
                return players
            else:
                print(f"      No players found")
                return []
        else:
            print(f"      Failed to get team page")
            return []
    
    def scrape_competition(self, comp_code, comp_name, season=2024):
        """Scrape a single competition"""
        print(f"\n=== Processing {comp_name} ({comp_code}) ===")
        
        # Get teams from competition
        teams = self.get_competition_teams(comp_code, season)
        
        if not teams:
            print(f"No teams found for {comp_name}")
            return []
        
        competition_players = []
        
        # Get players from each team
        for i, team in enumerate(teams):
            print(f"  Team {i+1}/{len(teams)}: {team['name']}")
            players = self.get_team_players(team, comp_code, season)
            competition_players.extend(players)
            
            # Random delay between teams
            self._random_delay(5, 12)
        
        print(f"  {comp_name}: {len(competition_players)} players collected")
        return competition_players
    
    def scrape_all_competitions(self, season=2024):
        """Scrape ALL competitions"""
        print("=== FULL Transfermarkt Scraper ===")
        print(f"Season: {season}")
        print(f"Competitions: {len(COMPETITIONS)}")
        
        all_players = []
        
        for comp_code, comp_slug in COMPETITIONS.items():
            try:
                players = self.scrape_competition(comp_code, comp_slug, season)
                all_players.extend(players)
                
                # Longer delay between competitions
                print(f"  Waiting before next competition...")
                self._random_delay(20, 40)
                
            except Exception as e:
                print(f"  Error processing {comp_slug}: {e}")
                continue
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"Successful requests: {self.successful_requests}")
        print(f"Failed requests: {self.failed_requests}")
        print(f"Total players collected: {len(all_players)}")
        
        return all_players

def main():
    """Main function"""
    scraper = FullTransfermarktScraper()
    
    print("Starting FULL scraping of ALL competitions...")
    print("This will take a LONG time due to delays and all leagues...")
    print("Estimated time: 2-4 hours for all leagues")
    
    # Ask for confirmation
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled by user")
        return
    
    players = scraper.scrape_all_competitions(season=2024)
    
    if players:
        df = pd.DataFrame(players)
        csv_file = 'players_ALL_LEAGUES.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"Data saved to: {csv_file}")
        print(f"Total players: {len(players)}")
        print(f"Competitions: {df['competition'].nunique()}")
        print(f"Teams: {df['team_name'].nunique()}")
        
        print(f"\n=== Players by Competition ===")
        for comp, count in df['competition'].value_counts().items():
            print(f"{comp}: {count} players")
        
        print(f"\n=== Sample Data ===")
        sample_cols = ['full_name', 'team_name', 'competition', 'position', 'age', 'nationality']
        available_cols = [col for col in sample_cols if col in df.columns]
        if available_cols:
            print(df[available_cols].head(15).to_string())
        
        return df
    else:
        print("No players collected!")
        return None

if __name__ == "__main__":
    df = main()
