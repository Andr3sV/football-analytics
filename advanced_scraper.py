#!/usr/bin/env python3
"""
Advanced scraper with anti-detection techniques for Transfermarkt
"""
import requests
import pandas as pd
import time
import random
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import itertools
from fake_useragent import UserAgent
import cloudscraper
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

class AdvancedTransfermarktScraper:
    def __init__(self):
        self.session = self._create_session()
        self.ua = UserAgent()
        self.successful_requests = 0
        self.failed_requests = 0
        
    def _create_session(self):
        """Create a session with advanced retry and timeout strategies"""
        session = requests.Session()
        
        # Retry strategy
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
    
    def _random_delay(self, min_delay=2, max_delay=8):
        """Add random delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        print(f"    Waiting {delay:.1f}s...")
        time.sleep(delay)
    
    def _make_request(self, url, max_retries=3):
        """Make a request with advanced anti-detection"""
        for attempt in range(max_retries):
            try:
                headers = self._get_random_headers()
                
                # Add random delay before request
                if attempt > 0:
                    self._random_delay(5, 15)
                
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
                    self._random_delay(10, 20)
                elif response.status_code == 429:
                    print(f"    Rate limited (429) - waiting longer...")
                    self._random_delay(30, 60)
                else:
                    print(f"    Status {response.status_code}")
                    
            except Exception as e:
                print(f"    Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    self._random_delay(5, 15)
        
        self.failed_requests += 1
        return None
    
    def get_competition_teams(self, comp_code, season=2024):
        """Get teams from competition with advanced techniques"""
        slug = COMPETITIONS.get(comp_code, comp_code.lower())
        
        # Try multiple URL patterns
        url_patterns = [
            f"https://www.transfermarkt.com/{slug}/startseite/wettbewerb/{comp_code}/saison_id/{season}",
            f"https://www.transfermarkt.com/{slug}/startseite/wettbewerb/{comp_code}",
            f"https://www.transfermarkt.com/wettbewerb/{comp_code}",
        ]
        
        for url in url_patterns:
            print(f"Trying competition URL: {url}")
            response = self._make_request(url)
            
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                teams = []
                
                # Look for team links in different table structures
                selectors = [
                    'table.items tbody tr td:nth-child(2) a',
                    'table.items tbody tr td a[href*="/verein/"]',
                    '.responsive-table tbody tr td:nth-child(2) a',
                    'table tbody tr td a[href*="/verein/"]'
                ]
                
                for selector in selectors:
                    team_links = soup.select(selector)
                    if team_links:
                        print(f"    Found {len(team_links)} teams with selector: {selector}")
                        
                        for link in team_links[:5]:  # Limit to first 5 teams
                            team_name = link.get_text(strip=True)
                            team_url = urljoin(url, link.get('href', ''))
                            
                            if team_name and team_url:
                                teams.append({
                                    'name': team_name,
                                    'url': team_url,
                                    'competition': comp_code
                                })
                        
                        if teams:
                            break
                
                if teams:
                    print(f"    Successfully found {len(teams)} teams")
                    return teams
                else:
                    print(f"    No teams found, trying next URL pattern...")
            
            self._random_delay(3, 8)
        
        print(f"    Failed to get teams for {comp_code}")
        return []
    
    def get_team_players(self, team, comp_code, season=2024):
        """Get players from team with advanced techniques"""
        team_name = team['name']
        team_url = team['url']
        
        print(f"  Getting players from {team_name}")
        
        # Try multiple URL patterns for team squad
        url_patterns = [
            f"{team_url}?saison_id={season}",
            f"{team_url}/kader?saison_id={season}",
            f"{team_url}/kader",
            team_url
        ]
        
        for url in url_patterns:
            print(f"    Trying team URL: {url}")
            response = self._make_request(url)
            
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                players = []
                
                # Look for player links in different table structures
                selectors = [
                    'table.items tbody tr td:nth-child(2) a[href*="/profil/spieler/"]',
                    'table.items tbody tr td:nth-child(2) a[href*="/profil-spieler/"]',
                    'table tbody tr td a[href*="/profil/spieler/"]',
                    '.responsive-table tbody tr td a[href*="/profil/spieler/"]'
                ]
                
                for selector in selectors:
                    player_links = soup.select(selector)
                    if player_links:
                        print(f"      Found {len(player_links)} players with selector: {selector}")
                        
                        for link in player_links[:10]:  # Limit to first 10 players
                            player_name = link.get_text(strip=True)
                            player_url = urljoin(url, link.get('href', ''))
                            
                            if player_name and player_url and ('/profil/spieler/' in player_url or '/profil-spieler/' in player_url):
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
                                    
                                    # Try to extract position, age, nationality, etc.
                                    if len(cells) >= 3:
                                        player_data['position'] = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                                    if len(cells) >= 4:
                                        player_data['age'] = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                                    if len(cells) >= 5:
                                        nationality_cell = cells[4]
                                        player_data['nationality'] = nationality_cell.get_text(strip=True)
                                        
                                        # Try to get nationality from flag
                                        flag_img = nationality_cell.select_one('img')
                                        if flag_img:
                                            player_data['nationality'] = flag_img.get('alt', player_data['nationality'])
                                    
                                    players.append(player_data)
                        
                        if players:
                            print(f"      Successfully extracted {len(players)} players")
                            return players
                        else:
                            print(f"      No valid players found with selector: {selector}")
                
                if not players:
                    print(f"      No players found, trying next URL pattern...")
            
            self._random_delay(2, 5)
        
        print(f"      Failed to get players from {team_name}")
        return []
    
    def scrape_all_competitions(self, season=2024, max_teams_per_comp=2):
        """Scrape all competitions with advanced techniques"""
        all_players = []
        
        print("=== Advanced Transfermarkt Scraper ===")
        print(f"Season: {season}")
        print(f"Max teams per competition: {max_teams_per_comp}")
        
        for comp_code, comp_slug in COMPETITIONS.items():
            print(f"\n=== Processing {comp_slug} ({comp_code}) ===")
            
            # Get teams from competition
            teams = self.get_competition_teams(comp_code, season)
            
            if not teams:
                print(f"No teams found for {comp_slug}")
                continue
            
            # Get players from each team (limited for speed)
            for team in teams[:max_teams_per_comp]:
                players = self.get_team_players(team, comp_code, season)
                all_players.extend(players)
                
                # Random delay between teams
                self._random_delay(3, 8)
            
            # Longer delay between competitions
            self._random_delay(10, 20)
        
        print(f"\n=== Scraping Complete ===")
        print(f"Successful requests: {self.successful_requests}")
        print(f"Failed requests: {self.failed_requests}")
        print(f"Total players collected: {len(all_players)}")
        
        return all_players

def main():
    """Main function"""
    scraper = AdvancedTransfermarktScraper()
    
    # Start with just a few competitions for testing
    test_competitions = {
        "ES1": "laliga",
        "GB1": "premierleague", 
        "L1": "bundesliga"
    }
    
    # Temporarily override competitions for testing
    global COMPETITIONS
    COMPETITIONS = test_competitions
    
    print("Starting advanced scraping with anti-detection techniques...")
    print("This may take a while due to delays and retries...")
    
    players = scraper.scrape_all_competitions(season=2024, max_teams_per_comp=2)
    
    if players:
        df = pd.DataFrame(players)
        csv_file = 'players_advanced_scraping.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"\n=== Results ===")
        print(f"Data saved to: {csv_file}")
        print(f"Total players: {len(players)}")
        print(f"Competitions: {df['competition'].nunique()}")
        print(f"Teams: {df['team_name'].nunique()}")
        
        print(f"\n=== Sample Data ===")
        sample_cols = ['full_name', 'team_name', 'competition', 'position', 'age', 'nationality']
        available_cols = [col for col in sample_cols if col in df.columns]
        if available_cols:
            print(df[available_cols].head(10).to_string())
        
        return df
    else:
        print("No players collected!")
        return None

if __name__ == "__main__":
    df = main()
