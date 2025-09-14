#!/usr/bin/env python3
"""
Optimized detailed player scraper - processes all 9,962 players efficiently
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
import concurrent.futures
from threading import Lock
import os

class OptimizedDetailedScraper:
    def __init__(self, max_workers=3, batch_size=50):
        self.session = self._create_session()
        self.ua = UserAgent()
        self.successful_requests = 0
        self.failed_requests = 0
        self.processed_count = 0
        self.total_players = 0
        self.lock = Lock()
        self.max_workers = max_workers
        self.batch_size = batch_size
        
    def _create_session(self):
        """Create a session with optimized retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=2,  # Reduced retries
            backoff_factor=0.5,  # Faster backoff
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
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
            'Referer': 'https://www.transfermarkt.com/',
            'Cache-Control': 'no-cache'
        }
    
    def _random_delay(self, min_delay=1, max_delay=3):
        """Reduced random delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _make_request(self, url, max_retries=2):
        """Optimized request with faster retry"""
        for attempt in range(max_retries):
            try:
                headers = self._get_random_headers()
                
                if attempt > 0:
                    self._random_delay(2, 5)
                
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=15,  # Reduced timeout
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    with self.lock:
                        self.successful_requests += 1
                    return response
                elif response.status_code == 403:
                    if attempt < max_retries - 1:
                        self._random_delay(5, 10)
                    continue
                else:
                    continue
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    self._random_delay(2, 5)
                continue
        
        with self.lock:
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
            # Extract from meta description (most reliable and fast)
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
                
                # Parse the structured description efficiently
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
                
                # Extract market value
                value_match = re.search(r'Market value:\s*€([0-9.]+)(mio|th\.)', description)
                if value_match:
                    value = value_match.group(1)
                    unit = value_match.group(2)
                    if unit == 'mio':
                        player_data['market_value'] = f"€{value}m"
                    else:
                        player_data['market_value'] = f"€{value}k"
                
                # Extract birth date and place
                birth_match = re.search(r'\*\s*(\d{2}\.\d{2}\.\d{4})\s+in\s+([^,]+),\s*([^➤]+)', description)
                if birth_match:
                    player_data['date_of_birth'] = birth_match.group(1)
                    player_data['city_of_birth'] = birth_match.group(2).strip()
                    player_data['country_of_birth'] = birth_match.group(3).strip()
                    player_data['place_of_birth'] = f"{birth_match.group(2).strip()}, {birth_match.group(3).strip()}"
            
            # Quick extraction of additional data from page content
            self._extract_additional_data(soup, player_data)
            
        except Exception as e:
            pass  # Continue with basic data if extraction fails
        
        return player_data
    
    def _extract_additional_data(self, soup, player_data):
        """Quick extraction of additional data"""
        try:
            # Get all text content for pattern matching
            all_text = soup.get_text()
            
            # Extract height
            if not player_data.get('height_cm'):
                height_match = re.search(r'(\d+)\s*cm', all_text, re.IGNORECASE)
                if height_match:
                    player_data['height_cm'] = height_match.group(1)
            
            # Extract dominant foot
            if not player_data.get('dominant_foot'):
                foot_match = re.search(r'Foot:\s*(\w+)|Dominant foot:\s*(\w+)|(\w+)\s*foot', all_text, re.IGNORECASE)
                if foot_match:
                    player_data['dominant_foot'] = foot_match.group(1) or foot_match.group(2) or foot_match.group(3)
            
            # Extract agent
            if not player_data.get('agent'):
                agent_match = re.search(r'Agent:\s*([^\\n]+)|Represented by:\s*([^\\n]+)|Berater:\s*([^\\n]+)', all_text, re.IGNORECASE)
                if agent_match:
                    player_data['agent'] = (agent_match.group(1) or agent_match.group(2) or agent_match.group(3)).strip()
            
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
    
    def process_batch(self, batch_players):
        """Process a batch of players"""
        batch_results = []
        
        for _, player in batch_players.iterrows():
            try:
                detailed_player = self.extract_player_details(player.to_dict())
                batch_results.append(detailed_player)
                
                with self.lock:
                    self.processed_count += 1
                    if self.processed_count % 100 == 0:
                        print(f"    Processed {self.processed_count}/{self.total_players} players...")
                
                # Small delay between players in batch
                self._random_delay(0.5, 1.5)
                
            except Exception as e:
                print(f"    Error processing {player.get('full_name', 'Unknown')}: {e}")
                batch_results.append(player.to_dict())
        
        return batch_results
    
    def process_all_players(self, players_df, save_interval=1000):
        """Process all players with progress saving"""
        self.total_players = len(players_df)
        print(f"=== Processing {self.total_players} players with optimized scraper ===")
        print(f"Max workers: {self.max_workers}, Batch size: {self.batch_size}")
        print(f"Saving progress every {save_interval} players")
        
        all_detailed_players = []
        
        # Process in batches
        for i in range(0, len(players_df), self.batch_size):
            batch = players_df.iloc[i:i + self.batch_size]
            print(f"\nProcessing batch {i//self.batch_size + 1}/{(len(players_df) + self.batch_size - 1)//self.batch_size}")
            
            # Process batch
            batch_results = self.process_batch(batch)
            all_detailed_players.extend(batch_results)
            
            # Save progress periodically
            if len(all_detailed_players) % save_interval == 0:
                self._save_progress(all_detailed_players, len(all_detailed_players))
            
            # Small delay between batches
            self._random_delay(2, 5)
        
        return all_detailed_players
    
    def _save_progress(self, players_data, count):
        """Save progress to file"""
        try:
            df = pd.DataFrame(players_data)
            progress_file = f'players_DETAILED_PROGRESS_{count}.csv'
            df.to_csv(progress_file, index=False, encoding='utf-8')
            print(f"    Progress saved: {progress_file} ({count} players)")
        except Exception as e:
            print(f"    Error saving progress: {e}")
    
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
    
    # Initialize optimized scraper
    scraper = OptimizedDetailedScraper(max_workers=3, batch_size=50)
    
    # Process all players
    print(f"\nStarting optimized processing of all {len(players_df)} players...")
    print("This will take approximately 2-4 hours depending on network conditions...")
    
    start_time = time.time()
    detailed_players = scraper.process_all_players(players_df, save_interval=500)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    if detailed_players:
        # Save final detailed data
        df_detailed = pd.DataFrame(detailed_players)
        csv_file = 'players_ALL_DETAILED_FINAL.csv'
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
        sample_cols = ['full_name', 'team_name', 'competition', 'age', 'nationality', 'position', 'market_value', 'date_of_birth']
        available_cols = [col for col in sample_cols if col in df_detailed.columns]
        if available_cols:
            print(df_detailed[available_cols].head(10).to_string())
        
        return df_detailed
    else:
        print("No detailed player data collected!")
        return None

if __name__ == "__main__":
    df = main()
