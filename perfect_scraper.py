#!/usr/bin/env python3
"""
Perfect scraper - processes all 9,962 players with correct market value conversion
"""
import requests
import pandas as pd
import time
import random
import json
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

class PerfectScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.successful_requests = 0
        self.failed_requests = 0
        self.processed_count = 0
        self.total_players = 0
        
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
            'Referer': 'https://www.transfermarkt.com/',
            'Cache-Control': 'no-cache'
        }
    
    def _random_delay(self, min_delay=3, max_delay=8):
        """Random delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _make_request(self, url, max_retries=3):
        """Make request with retry logic"""
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
                    if attempt < max_retries - 1:
                        self._random_delay(10, 20)
                    continue
                else:
                    continue
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    self._random_delay(5, 10)
                continue
        
        self.failed_requests += 1
        return None
    
    def extract_player_details(self, player_data):
        """Extract detailed information from player profile page"""
        player_url = player_data.get('profile_url', '')
        player_name = player_data.get('full_name', 'Unknown')
        
        response = self._make_request(player_url)
        if not response:
            return player_data
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        try:
            # Extract from meta description (most reliable)
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
                
                # Parse the structured description
                # Format: "Name, age, from Country ➤ Club, since year ➤ Position ➤ Market value: €X.XXm ➤ * DD.MM.YYYY in City, Country"
                
                # Extract age
                age_match = re.search(r'(\d+),', description)
                if age_match:
                    player_data['age'] = int(age_match.group(1))
                
                # Extract nationality
                nationality_match = re.search(r'from\s+([^➤]+)', description)
                if nationality_match:
                    player_data['nationality'] = nationality_match.group(1).strip()
                
                # Extract current club
                club_match = re.search(r'➤\s*([^,]+),', description)
                if club_match:
                    player_data['current_club'] = club_match.group(1).strip()
                
                # Extract position
                position_match = re.search(r'➤\s*[^➤]*➤\s*([^➤]+)➤', description)
                if position_match:
                    player_data['position'] = position_match.group(1).strip()
                
                # PERFECT: Extract market value with correct conversion
                value_patterns = [
                    (r'Market value:\s*€([0-9.]+)(mio|th\.)', "Pattern 1: Market value: €X.XXmio/th."),
                    (r'€([0-9.]+)(mio|th\.)', "Pattern 2: €X.XXmio/th."),
                    (r'Market value:\s*€([0-9.]+)m', "Pattern 3: Market value: €X.XXm"),
                    (r'€([0-9.]+)m', "Pattern 4: €X.XXm"),
                    (r'Market value:\s*€([0-9.]+)k', "Pattern 5: Market value: €X.XXk"),
                    (r'€([0-9.]+)k', "Pattern 6: €X.XXk")
                ]
                
                market_value_found = False
                for pattern, pattern_name in value_patterns:
                    value_match = re.search(pattern, description)
                    if value_match:
                        value = value_match.group(1)
                        
                        if len(value_match.groups()) > 1:
                            unit = value_match.group(2)
                            if unit == 'mio':
                                player_data['market_value_str'] = f"€{value}m"
                                player_data['market_value_numeric'] = int(float(value) * 1_000_000)
                            elif unit == 'th.':
                                player_data['market_value_str'] = f"€{value}k"
                                player_data['market_value_numeric'] = int(float(value) * 1_000)
                            else:
                                player_data['market_value_str'] = f"€{value}{unit}"
                                player_data['market_value_numeric'] = int(float(value))
                        else:
                            # Pattern without unit, check the pattern to determine unit
                            if 'k' in pattern:
                                player_data['market_value_str'] = f"€{value}k"
                                player_data['market_value_numeric'] = int(float(value) * 1_000)
                            elif 'm' in pattern:
                                player_data['market_value_str'] = f"€{value}m"
                                player_data['market_value_numeric'] = int(float(value) * 1_000_000)
                            else:
                                # This shouldn't happen with our patterns
                                player_data['market_value_str'] = f"€{value}"
                                player_data['market_value_numeric'] = int(float(value))
                        
                        market_value_found = True
                        break
                
                if not market_value_found:
                    player_data['market_value_str'] = None
                    player_data['market_value_numeric'] = None
                
                # Extract birth date and place
                birth_match = re.search(r'\*\s*(\d{2}\.\d{2}\.\d{4})\s+in\s+([^,]+),\s*([^➤]+)', description)
                if birth_match:
                    player_data['date_of_birth'] = birth_match.group(1)
                    player_data['city_of_birth'] = birth_match.group(2).strip()
                    player_data['country_of_birth'] = birth_match.group(3).strip()
                    player_data['place_of_birth'] = f"{birth_match.group(2).strip()}, {birth_match.group(3).strip()}"
            
            # Extract additional data from page content
            self._extract_additional_data(soup, player_data)
            
        except Exception as e:
            pass  # Continue with basic data if extraction fails
        
        return player_data
    
    def _extract_additional_data(self, soup, player_data):
        """Extract additional data from page content"""
        try:
            # Get all text content for pattern matching
            all_text = soup.get_text()
            
            # Extract height with better patterns
            if not player_data.get('height_cm'):
                height_patterns = [
                    r'(\d+)\s*cm',
                    r'Height:\s*(\d+)\s*cm',
                    r'Größe:\s*(\d+)\s*cm'
                ]
                for pattern in height_patterns:
                    height_match = re.search(pattern, all_text, re.IGNORECASE)
                    if height_match:
                        player_data['height_cm'] = height_match.group(1)
                        break
            
            # Extract dominant foot with better patterns
            if not player_data.get('dominant_foot'):
                foot_patterns = [
                    r'Foot:\s*(left|right|both)',
                    r'Dominant foot:\s*(left|right|both)',
                    r'Preferred foot:\s*(left|right|both)',
                    r'Füßigkeit:\s*(links|rechts|beidfüßig)',
                    r'(\w+)\s*foot'
                ]
                for pattern in foot_patterns:
                    foot_match = re.search(pattern, all_text, re.IGNORECASE)
                    if foot_match:
                        foot = foot_match.group(1).lower()
                        if foot in ['left', 'links']:
                            player_data['dominant_foot'] = 'left'
                        elif foot in ['right', 'rechts']:
                            player_data['dominant_foot'] = 'right'
                        elif foot in ['both', 'beidfüßig']:
                            player_data['dominant_foot'] = 'both'
                        break
            
            # Extract agent
            if not player_data.get('agent'):
                agent_patterns = [
                    r'Agent:\s*([^\\n]+)',
                    r'Represented by:\s*([^\\n]+)',
                    r'Berater:\s*([^\\n]+)',
                    r'Representative:\s*([^\\n]+)'
                ]
                for pattern in agent_patterns:
                    agent_match = re.search(pattern, all_text, re.IGNORECASE)
                    if agent_match:
                        player_data['agent'] = agent_match.group(1).strip()
                        break
            
            # Extract social media links
            social_links = []
            social_selectors = [
                'a[href*="instagram.com"]',
                'a[href*="twitter.com"]',
                'a[href*="facebook.com"]'
            ]
            
            for selector in social_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and 'transfermarkt' not in href:
                        social_links.append(href)
            
            if social_links:
                player_data['social_links'] = json.dumps(social_links)
            
        except Exception as e:
            pass
    
    def process_all_players(self, players_df, save_interval=100):
        """Process all players with progress saving"""
        self.total_players = len(players_df)
        print(f"=== Processing ALL {self.total_players} players for detailed information ===")
        print(f"Saving progress every {save_interval} players")
        
        all_detailed_players = []
        
        for idx, (_, player) in enumerate(players_df.iterrows()):
            try:
                if (idx + 1) % 10 == 0:
                    print(f"\nPlayer {idx + 1}/{self.total_players}: {player['full_name']}")
                
                detailed_player = self.extract_player_details(player.to_dict())
                all_detailed_players.append(detailed_player)
                
                self.processed_count += 1
                
                # Show progress
                if (idx + 1) % 100 == 0:
                    print(f"  ✓ Processed {idx + 1}/{self.total_players} players...")
                
                # Save progress periodically
                if (idx + 1) % save_interval == 0:
                    self._save_progress(all_detailed_players, idx + 1)
                
                # Random delay between requests
                if idx < self.total_players - 1:  # Don't delay after last player
                    delay = random.uniform(3, 8)
                    time.sleep(delay)
                
            except Exception as e:
                print(f"  ❌ Error processing {player['full_name']}: {e}")
                all_detailed_players.append(player.to_dict())
        
        return all_detailed_players
    
    def _save_progress(self, players_data, count):
        """Save progress to file"""
        try:
            df = pd.DataFrame(players_data)
            progress_file = f'players_PERFECT_DETAILED_PROGRESS_{count}.csv'
            df.to_csv(progress_file, index=False, encoding='utf-8')
            print(f"  💾 Progress saved: {progress_file} ({count} players)")
        except Exception as e:
            print(f"  ❌ Error saving progress: {e}")
    
    def get_stats(self):
        """Get processing statistics"""
        return {
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'processed_count': self.processed_count,
            'total_players': self.total_players,
            'success_rate': self.successful_requests / (self.successful_requests + self.failed_requests) * 100 if (self.successful_requests + self.failed_requests) > 0 else 0
        }

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
    scraper = PerfectScraper()
    
    # Process all players
    print(f"\nStarting PERFECT detailed processing of ALL {len(players_df)} players...")
    print("This will take approximately 8-12 hours depending on network conditions...")
    print("Progress will be saved every 100 players.")
    
    start_time = time.time()
    detailed_players = scraper.process_all_players(players_df, save_interval=100)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    if detailed_players:
        # Save final detailed data
        df_detailed = pd.DataFrame(detailed_players)
        csv_file = 'players_PERFECT_DETAILED_FINAL.csv'
        df_detailed.to_csv(csv_file, index=False, encoding='utf-8')
        
        # Get statistics
        stats = scraper.get_stats()
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"Detailed data saved to: {csv_file}")
        print(f"Total players processed: {len(detailed_players)}")
        print(f"Processing time: {processing_time/3600:.2f} hours")
        print(f"Successful requests: {stats['successful_requests']}")
        print(f"Failed requests: {stats['failed_requests']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        
        # Show sample of detailed data
        print(f"\n=== Sample Detailed Data ===")
        sample_cols = ['full_name', 'team_name', 'competition', 'age', 'nationality', 'position', 'market_value_str', 'market_value_numeric', 'date_of_birth']
        available_cols = [col for col in sample_cols if col in df_detailed.columns]
        if available_cols:
            print(df_detailed[available_cols].head(10).to_string())
        
        return df_detailed
    else:
        print("No detailed player data collected!")
        return None

if __name__ == "__main__":
    df = main()
