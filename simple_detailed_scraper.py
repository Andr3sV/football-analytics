#!/usr/bin/env python3
"""
Simple detailed player scraper - focuses on extracting basic but essential data
"""
import requests
import pandas as pd
import time
import random
import json
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
from datetime import datetime

class SimpleDetailedScraper:
    def __init__(self):
        self.session = self._create_session()
        self.ua = UserAgent()
        self.successful_requests = 0
        self.failed_requests = 0
        
    def _create_session(self):
        """Create a session with retry strategy"""
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
        """Generate random headers"""
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def _random_delay(self, min_delay=2, max_delay=5):
        """Add random delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        print(f"    Waiting {delay:.1f}s...")
        time.sleep(delay)
    
    def _make_request(self, url, max_retries=3):
        """Make a request with anti-detection"""
        for attempt in range(max_retries):
            try:
                headers = self._get_random_headers()
                
                if attempt > 0:
                    self._random_delay(5, 10)
                
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
                else:
                    print(f"    Status {response.status_code}")
                    
            except Exception as e:
                print(f"    Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    self._random_delay(5, 10)
        
        self.failed_requests += 1
        return None
    
    def extract_player_details(self, player_url, basic_info):
        """Extract detailed information from player profile page"""
        print(f"  Extracting details for: {basic_info.get('full_name', 'Unknown')}")
        
        response = self._make_request(player_url)
        if not response:
            print(f"    Failed to fetch player profile")
            return basic_info
        
        soup = BeautifulSoup(response.content, 'html.parser')
        player_data = basic_info.copy()
        
        try:
            # Debug: Print page title to verify we're on the right page
            title = soup.find('title')
            if title:
                print(f"    Page title: {title.get_text()[:50]}...")
            
            # Look for all data tables and print their structure
            data_tables = soup.find_all('table', class_='items')
            print(f"    Found {len(data_tables)} data tables")
            
            # Try to find market value in the header area
            market_value = self._find_market_value(soup)
            player_data['market_value'] = market_value
            print(f"    Market value: {market_value}")
            
            # Try to find basic info in data rows
            data_rows = soup.find_all('tr')
            for row in data_rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    # Map common labels to our fields
                    if 'birth' in label and 'date' in label:
                        player_data['date_of_birth'] = value
                        print(f"    Date of birth: {value}")
                    elif 'birth' in label and 'place' in label:
                        player_data['place_of_birth'] = value
                        print(f"    Place of birth: {value}")
                    elif 'height' in label or 'size' in label:
                        player_data['height_cm'] = value
                        print(f"    Height: {value}")
                    elif 'nationality' in label or 'citizenship' in label:
                        player_data['nationality'] = value
                        print(f"    Nationality: {value}")
                    elif 'position' in label or 'role' in label:
                        player_data['position'] = value
                        print(f"    Position: {value}")
                    elif 'foot' in label:
                        player_data['dominant_foot'] = value
                        print(f"    Dominant foot: {value}")
                    elif 'club' in label and 'current' in label:
                        player_data['current_club'] = value
                        print(f"    Current club: {value}")
                    elif 'agent' in label:
                        player_data['agent'] = value
                        print(f"    Agent: {value}")
                    elif 'equipment' in label or 'brand' in label:
                        player_data['equipment_brand'] = value
                        print(f"    Equipment: {value}")
            
            # Calculate age if we have date of birth
            if player_data.get('date_of_birth'):
                age = self._calculate_age(player_data['date_of_birth'])
                player_data['age'] = age
                print(f"    Calculated age: {age}")
            
            print(f"    ✓ Successfully extracted data for {basic_info.get('full_name', 'Unknown')}")
            
        except Exception as e:
            print(f"    Error extracting details: {e}")
        
        return player_data
    
    def _find_market_value(self, soup):
        """Find market value in various possible locations"""
        # Look for market value in different ways
        selectors = [
            '.dataMarktwert',
            '.tm-player-market-value-development__current-value',
            '[data-testid="market-value"]',
            '.dataMarktwert a',
            '.dataMarktwert .dataValue'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if '€' in text or 'mio' in text.lower() or 'th.' in text.lower():
                    return text
        
        # Also look in all text for market value patterns
        all_text = soup.get_text()
        value_patterns = [
            r'€\s*\d+\.?\d*\s*mio',
            r'€\s*\d+\.?\d*\s*th\.',
            r'\d+\.?\d*\s*mio\s*€',
            r'\d+\.?\d*\s*th\.\s*€'
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return ""
    
    def _calculate_age(self, date_of_birth):
        """Calculate age from date of birth"""
        try:
            # Try different date formats
            date_formats = ['%b %d, %Y', '%d.%m.%Y', '%Y-%m-%d', '%B %d, %Y', '%d/%m/%Y']
            
            for fmt in date_formats:
                try:
                    dob = datetime.strptime(date_of_birth, fmt)
                    today = datetime.now()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    return age
                except:
                    continue
        except:
            pass
        return ""
    
    def process_players(self, players_df, max_players=5):
        """Process players to extract detailed information"""
        print(f"=== Processing {min(max_players, len(players_df))} players for detailed information ===")
        
        players_to_process = players_df.head(max_players)
        detailed_players = []
        
        for idx, player in players_to_process.iterrows():
            print(f"\nPlayer {idx + 1}/{len(players_to_process)}: {player.get('full_name', 'Unknown')}")
            
            detailed_player = self.extract_player_details(
                player.get('profile_url', ''), 
                player.to_dict()
            )
            
            detailed_players.append(detailed_player)
            self._random_delay(3, 6)
        
        print(f"\n=== Detailed Extraction Complete ===")
        print(f"Successful requests: {self.successful_requests}")
        print(f"Failed requests: {self.failed_requests}")
        print(f"Players processed: {len(detailed_players)}")
        
        return detailed_players

def main():
    """Main function"""
    # Load the players data
    try:
        players_df = pd.read_csv('players_ALL_LEAGUES.csv')
        print(f"Loaded {len(players_df)} players from players_ALL_LEAGUES.csv")
    except FileNotFoundError:
        print("Error: players_ALL_LEAGUES.csv not found!")
        return
    
    # Initialize scraper
    scraper = SimpleDetailedScraper()
    
    # Process first 5 players for testing
    print(f"\nProcessing first 5 players for detailed information...")
    detailed_players = scraper.process_players(players_df, max_players=5)
    
    if detailed_players:
        # Save detailed data
        df_detailed = pd.DataFrame(detailed_players)
        csv_file = 'players_SIMPLE_DETAILED.csv'
        df_detailed.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"Detailed data saved to: {csv_file}")
        print(f"Total players processed: {len(detailed_players)}")
        
        # Show sample of detailed data
        print(f"\n=== Sample Detailed Data ===")
        sample_cols = ['full_name', 'team_name', 'competition', 'market_value', 'date_of_birth', 'age', 'height_cm', 'nationality', 'position']
        available_cols = [col for col in sample_cols if col in df_detailed.columns]
        if available_cols:
            print(df_detailed[available_cols].head(10).to_string())
        
        return df_detailed
    else:
        print("No detailed player data collected!")
        return None

if __name__ == "__main__":
    df = main()
