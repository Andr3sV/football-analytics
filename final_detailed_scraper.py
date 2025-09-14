#!/usr/bin/env python3
"""
Final detailed player scraper - extracts comprehensive data from meta descriptions
Based on insights from primeplayers/data-extractor approach
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

class FinalDetailedScraper:
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
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.transfermarkt.com/'
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
            # Extract from meta description (most reliable source)
            meta_description = self._extract_from_meta_description(soup, player_data)
            
            # Extract additional data from page content
            self._extract_from_page_content(soup, player_data)
            
            # Extract social media links
            social_links = self._extract_social_links(soup)
            player_data['social_links'] = social_links
            
            # Extract youth clubs
            youth_clubs = self._extract_youth_clubs(soup)
            player_data['youth_clubs'] = youth_clubs
            
            print(f"    ✓ Successfully extracted data for {basic_info.get('full_name', 'Unknown')}")
            
        except Exception as e:
            print(f"    Error extracting details: {e}")
        
        return player_data
    
    def _extract_from_meta_description(self, soup, player_data):
        """Extract data from meta description - most reliable source"""
        try:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
                print(f"    Meta description: {description[:100]}...")
                
                # Parse the structured description
                # Format: "Name, age, from Country ➤ Club, since year ➤ Position ➤ Market value: €X.XXm ➤ * DD.MM.YYYY in City, Country"
                
                # Extract age
                age_match = re.search(r'(\d+),', description)
                if age_match:
                    player_data['age'] = int(age_match.group(1))
                    print(f"    Age: {age_match.group(1)}")
                
                # Extract nationality
                nationality_match = re.search(r'from\s+([^➤]+)', description)
                if nationality_match:
                    player_data['nationality'] = nationality_match.group(1).strip()
                    print(f"    Nationality: {nationality_match.group(1).strip()}")
                
                # Extract current club
                club_match = re.search(r'➤\s*([^,]+),', description)
                if club_match:
                    player_data['current_club'] = club_match.group(1).strip()
                    print(f"    Current club: {club_match.group(1).strip()}")
                
                # Extract position
                position_match = re.search(r'➤\s*[^➤]*➤\s*([^➤]+)➤', description)
                if position_match:
                    player_data['position'] = position_match.group(1).strip()
                    print(f"    Position: {position_match.group(1).strip()}")
                
                # Extract market value
                value_match = re.search(r'Market value:\s*€([0-9.]+)(mio|th\.)', description)
                if value_match:
                    value = value_match.group(1)
                    unit = value_match.group(2)
                    if unit == 'mio':
                        player_data['market_value'] = f"€{value}m"
                    else:
                        player_data['market_value'] = f"€{value}k"
                    print(f"    Market value: {player_data['market_value']}")
                
                # Extract birth date and place
                birth_match = re.search(r'\*\s*(\d{2}\.\d{2}\.\d{4})\s+in\s+([^,]+),\s*([^➤]+)', description)
                if birth_match:
                    player_data['date_of_birth'] = birth_match.group(1)
                    player_data['city_of_birth'] = birth_match.group(2).strip()
                    player_data['country_of_birth'] = birth_match.group(3).strip()
                    player_data['place_of_birth'] = f"{birth_match.group(2).strip()}, {birth_match.group(3).strip()}"
                    print(f"    Birth: {birth_match.group(1)} in {birth_match.group(2).strip()}, {birth_match.group(3).strip()}")
                
                return description
        except Exception as e:
            print(f"    Error extracting from meta description: {e}")
        return ""
    
    def _extract_from_page_content(self, soup, player_data):
        """Extract additional data from page content"""
        try:
            # Look for height information
            if not player_data.get('height_cm'):
                height_patterns = [
                    r'(\d+)\s*cm',
                    r'Height:\s*(\d+)\s*cm',
                    r'(\d+)\s*centimeters'
                ]
                
                all_text = soup.get_text()
                for pattern in height_patterns:
                    match = re.search(pattern, all_text, re.IGNORECASE)
                    if match:
                        player_data['height_cm'] = match.group(1)
                        print(f"    Height: {match.group(1)} cm")
                        break
            
            # Look for dominant foot
            if not player_data.get('dominant_foot'):
                foot_patterns = [
                    r'Foot:\s*(\w+)',
                    r'Dominant foot:\s*(\w+)',
                    r'(\w+)\s*foot'
                ]
                
                all_text = soup.get_text()
                for pattern in foot_patterns:
                    match = re.search(pattern, all_text, re.IGNORECASE)
                    if match:
                        player_data['dominant_foot'] = match.group(1)
                        print(f"    Dominant foot: {match.group(1)}")
                        break
            
            # Look for agent information
            if not player_data.get('agent'):
                agent_patterns = [
                    r'Agent:\s*([^\\n]+)',
                    r'Represented by:\s*([^\\n]+)',
                    r'Berater:\s*([^\\n]+)'
                ]
                
                all_text = soup.get_text()
                for pattern in agent_patterns:
                    match = re.search(pattern, all_text, re.IGNORECASE)
                    if match:
                        player_data['agent'] = match.group(1).strip()
                        print(f"    Agent: {match.group(1).strip()}")
                        break
            
            # Look for equipment brand
            if not player_data.get('equipment_brand'):
                equipment_patterns = [
                    r'Equipment:\s*([^\\n]+)',
                    r'Brand:\s*([^\\n]+)',
                    r'Ausrüstung:\s*([^\\n]+)'
                ]
                
                all_text = soup.get_text()
                for pattern in equipment_patterns:
                    match = re.search(pattern, all_text, re.IGNORECASE)
                    if match:
                        player_data['equipment_brand'] = match.group(1).strip()
                        print(f"    Equipment: {match.group(1).strip()}")
                        break
        except Exception as e:
            print(f"    Error extracting from page content: {e}")
    
    def _extract_social_links(self, soup):
        """Extract social media links"""
        social_links = []
        try:
            social_selectors = [
                'a[href*="instagram.com"]',
                'a[href*="twitter.com"]',
                'a[href*="facebook.com"]',
                'a[href*="tiktok.com"]'
            ]
            
            for selector in social_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and 'transfermarkt' not in href:
                        social_links.append(href)
        except:
            pass
        
        return json.dumps(social_links) if social_links else ""
    
    def _extract_youth_clubs(self, soup):
        """Extract youth/training clubs"""
        youth_clubs = []
        try:
            # Look for youth clubs section
            youth_section = soup.select_one('.dataJugendvereine, .tm-player-youth-clubs')
            if youth_section:
                club_links = youth_section.select('a')
                for link in club_links:
                    club_name = link.get_text(strip=True)
                    if club_name:
                        youth_clubs.append(club_name)
        except:
            pass
        
        return json.dumps(youth_clubs) if youth_clubs else ""
    
    def process_players(self, players_df, max_players=10):
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
    scraper = FinalDetailedScraper()
    
    # Process first 10 players for testing
    print(f"\nProcessing first 10 players for detailed information...")
    detailed_players = scraper.process_players(players_df, max_players=10)
    
    if detailed_players:
        # Save detailed data
        df_detailed = pd.DataFrame(detailed_players)
        csv_file = 'players_FINAL_DETAILED.csv'
        df_detailed.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"Detailed data saved to: {csv_file}")
        print(f"Total players processed: {len(detailed_players)}")
        
        # Show sample of detailed data
        print(f"\n=== Sample Detailed Data ===")
        sample_cols = ['full_name', 'team_name', 'competition', 'age', 'nationality', 'position', 'market_value', 'date_of_birth', 'place_of_birth', 'height_cm']
        available_cols = [col for col in sample_cols if col in df_detailed.columns]
        if available_cols:
            print(df_detailed[available_cols].head(10).to_string())
        
        return df_detailed
    else:
        print("No detailed player data collected!")
        return None

if __name__ == "__main__":
    df = main()
