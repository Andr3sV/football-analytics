#!/usr/bin/env python3
"""
Automated detailed player profile scraper - extracts comprehensive data from individual player pages
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
import re
from datetime import datetime

class AutoDetailedPlayerScraper:
    def __init__(self):
        self.session = self._create_session()
        self.ua = UserAgent()
        self.successful_requests = 0
        self.failed_requests = 0
        self.detailed_players = []
        
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
                
                if attempt > 0:
                    self._random_delay(5, 15)
                
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
                    self._random_delay(10, 25)
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
    
    def extract_player_details(self, player_url, basic_info):
        """Extract detailed information from player profile page"""
        print(f"  Extracting details for: {basic_info.get('full_name', 'Unknown')}")
        
        response = self._make_request(player_url)
        if not response:
            print(f"    Failed to fetch player profile")
            return basic_info
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Initialize with basic info
        player_data = basic_info.copy()
        
        try:
            # Market value (current)
            market_value = self._extract_market_value(soup)
            player_data['market_value'] = market_value
            
            # Date of birth
            date_of_birth = self._extract_date_of_birth(soup)
            player_data['date_of_birth'] = date_of_birth
            
            # Age calculation
            if date_of_birth:
                age = self._calculate_age(date_of_birth)
                player_data['age'] = age
            
            # Place of birth
            place_of_birth = self._extract_place_of_birth(soup)
            player_data['place_of_birth'] = place_of_birth
            player_data['city_of_birth'] = place_of_birth.split(',')[0].strip() if place_of_birth else ""
            player_data['country_of_birth'] = place_of_birth.split(',')[-1].strip() if place_of_birth and ',' in place_of_birth else ""
            
            # Height
            height = self._extract_height(soup)
            player_data['height_cm'] = height
            
            # Nationality
            nationality = self._extract_nationality(soup)
            player_data['nationality'] = nationality
            
            # Position
            position = self._extract_position(soup)
            player_data['position'] = position
            
            # Dominant foot
            dominant_foot = self._extract_dominant_foot(soup)
            player_data['dominant_foot'] = dominant_foot
            
            # Current club
            current_club = self._extract_current_club(soup)
            player_data['current_club'] = current_club
            
            # Contract information
            contract_info = self._extract_contract_info(soup)
            player_data.update(contract_info)
            
            # Agent/Agency
            agent = self._extract_agent(soup)
            player_data['agent'] = agent
            
            # Equipment brand
            equipment = self._extract_equipment(soup)
            player_data['equipment_brand'] = equipment
            
            # Social media links
            social_links = self._extract_social_links(soup)
            player_data['social_links'] = social_links
            
            # Youth clubs
            youth_clubs = self._extract_youth_clubs(soup)
            player_data['youth_clubs'] = youth_clubs
            
            # Season statistics
            season_stats = self._extract_season_stats(soup)
            player_data['season_stats'] = season_stats
            
            print(f"    ✓ Extracted detailed info for {basic_info.get('full_name', 'Unknown')}")
            
        except Exception as e:
            print(f"    Error extracting details: {e}")
        
        return player_data
    
    def _extract_market_value(self, soup):
        """Extract current market value"""
        try:
            # Look for market value in different possible locations
            value_selectors = [
                '.dataMarktwert a',
                '.dataMarktwert',
                '[data-testid="market-value"]',
                '.tm-player-market-value-development__current-value',
                '.dataMarktwert .dataValue'
            ]
            
            for selector in value_selectors:
                value_elem = soup.select_one(selector)
                if value_elem:
                    value_text = value_elem.get_text(strip=True)
                    # Extract numeric value and currency
                    if '€' in value_text or 'mio' in value_text.lower() or 'th.' in value_text.lower():
                        return value_text
        except:
            pass
        return ""
    
    def _extract_date_of_birth(self, soup):
        """Extract date of birth"""
        try:
            # Look for date of birth in different possible locations
            dob_selectors = [
                '.dataGeburtsdatum',
                '[data-testid="birth-date"]',
                '.tm-player-header__birth-date',
                '.dataGeburtsdatum .dataValue'
            ]
            
            for selector in dob_selectors:
                dob_elem = soup.select_one(selector)
                if dob_elem:
                    dob_text = dob_elem.get_text(strip=True)
                    if dob_text and len(dob_text) > 5:  # Basic validation
                        return dob_text
        except:
            pass
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
    
    def _extract_place_of_birth(self, soup):
        """Extract place of birth"""
        try:
            place_selectors = [
                '.dataGeburtsort',
                '[data-testid="birth-place"]',
                '.tm-player-header__birth-place',
                '.dataGeburtsort .dataValue'
            ]
            
            for selector in place_selectors:
                place_elem = soup.select_one(selector)
                if place_elem:
                    place_text = place_elem.get_text(strip=True)
                    if place_text:
                        return place_text
        except:
            pass
        return ""
    
    def _extract_height(self, soup):
        """Extract height in cm"""
        try:
            height_selectors = [
                '.dataGroesse',
                '[data-testid="height"]',
                '.tm-player-header__height',
                '.dataGroesse .dataValue'
            ]
            
            for selector in height_selectors:
                height_elem = soup.select_one(selector)
                if height_elem:
                    height_text = height_elem.get_text(strip=True)
                    # Extract numeric value
                    height_match = re.search(r'(\d+)', height_text)
                    if height_match:
                        return height_match.group(1)
        except:
            pass
        return ""
    
    def _extract_nationality(self, soup):
        """Extract nationality"""
        try:
            # Look for nationality flags or text
            nationality_selectors = [
                '.dataNationalitaet img',
                '.dataNationalitaet',
                '[data-testid="nationality"]',
                '.tm-player-header__nationality img',
                '.dataNationalitaet .dataValue'
            ]
            
            for selector in nationality_selectors:
                nat_elem = soup.select_one(selector)
                if nat_elem:
                    if nat_elem.name == 'img':
                        return nat_elem.get('alt', '')
                    else:
                        return nat_elem.get_text(strip=True)
        except:
            pass
        return ""
    
    def _extract_position(self, soup):
        """Extract position"""
        try:
            position_selectors = [
                '.dataRueckennummer',
                '[data-testid="position"]',
                '.tm-player-header__position',
                '.dataRueckennummer .dataValue'
            ]
            
            for selector in position_selectors:
                pos_elem = soup.select_one(selector)
                if pos_elem:
                    pos_text = pos_elem.get_text(strip=True)
                    if pos_text:
                        return pos_text
        except:
            pass
        return ""
    
    def _extract_dominant_foot(self, soup):
        """Extract dominant foot"""
        try:
            foot_selectors = [
                '.dataFuss',
                '[data-testid="dominant-foot"]',
                '.tm-player-header__dominant-foot',
                '.dataFuss .dataValue'
            ]
            
            for selector in foot_selectors:
                foot_elem = soup.select_one(selector)
                if foot_elem:
                    foot_text = foot_elem.get_text(strip=True)
                    if foot_text:
                        return foot_text
        except:
            pass
        return ""
    
    def _extract_current_club(self, soup):
        """Extract current club"""
        try:
            club_selectors = [
                '.dataZugehoerigkeit a',
                '.dataZugehoerigkeit',
                '[data-testid="current-club"]',
                '.tm-player-header__current-club',
                '.dataZugehoerigkeit .dataValue'
            ]
            
            for selector in club_selectors:
                club_elem = soup.select_one(selector)
                if club_elem:
                    club_text = club_elem.get_text(strip=True)
                    if club_text:
                        return club_text
        except:
            pass
        return ""
    
    def _extract_contract_info(self, soup):
        """Extract contract information"""
        contract_info = {
            'club_joined_date': '',
            'contract_expires': '',
            'last_contract_extension': ''
        }
        
        try:
            # Look for contract information in various sections
            contract_sections = soup.select('.dataZugehoerigkeit, .dataVertrag, .tm-player-contract')
            
            for section in contract_sections:
                text = section.get_text(strip=True)
                
                # Look for dates in various formats
                date_patterns = [
                    r'(\d{1,2}\.\d{1,2}\.\d{4})',
                    r'(\d{4}-\d{2}-\d{2})',
                    r'(\w+ \d{1,2}, \d{4})'
                ]
                
                for pattern in date_patterns:
                    dates = re.findall(pattern, text)
                    if dates:
                        if not contract_info['club_joined_date']:
                            contract_info['club_joined_date'] = dates[0]
                        elif not contract_info['contract_expires']:
                            contract_info['contract_expires'] = dates[0]
        except:
            pass
        
        return contract_info
    
    def _extract_agent(self, soup):
        """Extract agent/agency information"""
        try:
            agent_selectors = [
                '.dataBerater',
                '[data-testid="agent"]',
                '.tm-player-agent',
                '.dataBerater .dataValue'
            ]
            
            for selector in agent_selectors:
                agent_elem = soup.select_one(selector)
                if agent_elem:
                    agent_text = agent_elem.get_text(strip=True)
                    if agent_text:
                        return agent_text
        except:
            pass
        return ""
    
    def _extract_equipment(self, soup):
        """Extract equipment brand"""
        try:
            equipment_selectors = [
                '.dataAusrüstung',
                '[data-testid="equipment"]',
                '.tm-player-equipment',
                '.dataAusrüstung .dataValue'
            ]
            
            for selector in equipment_selectors:
                equip_elem = soup.select_one(selector)
                if equip_elem:
                    equip_text = equip_elem.get_text(strip=True)
                    if equip_text:
                        return equip_text
        except:
            pass
        return ""
    
    def _extract_social_links(self, soup):
        """Extract social media links"""
        social_links = []
        try:
            # Look for social media links
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
                    if href:
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
    
    def _extract_season_stats(self, soup):
        """Extract season statistics"""
        season_stats = {}
        try:
            # Look for statistics tables
            stats_tables = soup.select('.responsive-table, .items')
            
            for table in stats_tables:
                rows = table.select('tr')
                for row in rows:
                    cells = row.select('td')
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            season_stats[key] = value
        except:
            pass
        
        return json.dumps(season_stats) if season_stats else ""
    
    def process_players(self, players_df, max_players=50):
        """Process players to extract detailed information"""
        print(f"=== Processing {min(max_players, len(players_df))} players for detailed information ===")
        
        players_to_process = players_df.head(max_players)
        detailed_players = []
        
        for idx, player in players_to_process.iterrows():
            print(f"\nPlayer {idx + 1}/{len(players_to_process)}: {player.get('full_name', 'Unknown')}")
            
            # Extract detailed information
            detailed_player = self.extract_player_details(
                player.get('profile_url', ''), 
                player.to_dict()
            )
            
            detailed_players.append(detailed_player)
            
            # Random delay between players
            self._random_delay(3, 8)
        
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
    scraper = AutoDetailedPlayerScraper()
    
    # Process first 50 players for testing
    print(f"\nProcessing first 50 players for detailed information...")
    detailed_players = scraper.process_players(players_df, max_players=50)
    
    if detailed_players:
        # Save detailed data
        df_detailed = pd.DataFrame(detailed_players)
        csv_file = 'players_DETAILED_SAMPLE.csv'
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
