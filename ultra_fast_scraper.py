#!/usr/bin/env python3
"""
Ultra-fast scraper with advanced anti-detection techniques
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
import cloudscraper

class UltraFastScraper:
    def __init__(self, max_workers=5, batch_size=100):
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
        """Create a session with cloudscraper for better anti-detection"""
        session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        # Add retry strategy
        retry_strategy = Retry(
            total=1,  # Only 1 retry for speed
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=50)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_random_headers(self):
        """Generate random headers"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def _random_delay(self, min_delay=0.5, max_delay=2):
        """Very short random delay"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _make_request(self, url, max_retries=1):
        """Ultra-fast request with minimal retry"""
        for attempt in range(max_retries):
            try:
                headers = self._get_random_headers()
                
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=10,  # Very short timeout
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    with self.lock:
                        self.successful_requests += 1
                    return response
                elif response.status_code == 403:
                    if attempt < max_retries - 1:
                        self._random_delay(1, 3)
                    continue
                else:
                    continue
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    self._random_delay(1, 2)
                continue
        
        with self.lock:
            self.failed_requests += 1
        return None
    
    def extract_player_details_fast(self, player_data):
        """Ultra-fast extraction focusing on meta description only"""
        player_url = player_data.get('profile_url', '')
        
        response = self._make_request(player_url)
        if not response:
            return player_data
        
        try:
            # Only parse meta description for speed
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            
            if meta_desc:
                description = meta_desc.get('content', '')
                
                # Fast regex parsing
                patterns = {
                    'age': r'(\d+),',
                    'nationality': r'from\s+([^➤]+)',
                    'current_club': r'➤\s*([^,]+),',
                    'position': r'➤\s*[^➤]*➤\s*([^➤]+)➤',
                    'market_value': r'Market value:\s*€([0-9.]+)(mio|th\.)',
                    'birth_info': r'\*\s*(\d{2}\.\d{2}\.\d{4})\s+in\s+([^,]+),\s*([^➤]+)'
                }
                
                for field, pattern in patterns.items():
                    match = re.search(pattern, description)
                    if match:
                        if field == 'age':
                            player_data['age'] = int(match.group(1))
                        elif field == 'nationality':
                            player_data['nationality'] = match.group(1).strip()
                        elif field == 'current_club':
                            player_data['current_club'] = match.group(1).strip()
                        elif field == 'position':
                            player_data['position'] = match.group(1).strip()
                        elif field == 'market_value':
                            value = match.group(1)
                            unit = match.group(2)
                            if unit == 'mio':
                                player_data['market_value'] = f"€{value}m"
                            else:
                                player_data['market_value'] = f"€{value}k"
                        elif field == 'birth_info':
                            player_data['date_of_birth'] = match.group(1)
                            player_data['city_of_birth'] = match.group(2).strip()
                            player_data['country_of_birth'] = match.group(3).strip()
                            player_data['place_of_birth'] = f"{match.group(2).strip()}, {match.group(3).strip()}"
            
        except Exception as e:
            pass  # Continue with basic data if extraction fails
        
        return player_data
    
    def process_batch_fast(self, batch_players):
        """Ultra-fast batch processing"""
        batch_results = []
        
        for _, player in batch_players.iterrows():
            try:
                detailed_player = self.extract_player_details_fast(player.to_dict())
                batch_results.append(detailed_player)
                
                with self.lock:
                    self.processed_count += 1
                    if self.processed_count % 50 == 0:
                        print(f"    ⚡ Processed {self.processed_count}/{self.total_players} players...")
                
                # Very short delay
                self._random_delay(0.2, 0.8)
                
            except Exception as e:
                print(f"    ❌ Error processing {player.get('full_name', 'Unknown')}: {e}")
                batch_results.append(player.to_dict())
        
        return batch_results
    
    def process_all_players_fast(self, players_df, save_interval=200):
        """Ultra-fast processing with frequent saves"""
        self.total_players = len(players_df)
        print(f"🚀 ULTRA-FAST PROCESSING: {self.total_players} players")
        print(f"⚡ Max workers: {self.max_workers}, Batch size: {self.batch_size}")
        print(f"💾 Saving every {save_interval} players")
        
        all_detailed_players = []
        
        # Process in smaller batches for speed
        for i in range(0, len(players_df), self.batch_size):
            batch = players_df.iloc[i:i + self.batch_size]
            batch_num = i//self.batch_size + 1
            total_batches = (len(players_df) + self.batch_size - 1)//self.batch_size
            
            print(f"\n⚡ Processing batch {batch_num}/{total_batches} ({len(batch)} players)")
            
            # Process batch
            batch_results = self.process_batch_fast(batch)
            all_detailed_players.extend(batch_results)
            
            # Save progress frequently
            if len(all_detailed_players) % save_interval == 0:
                self._save_progress(all_detailed_players, len(all_detailed_players))
            
            # Very short delay between batches
            self._random_delay(1, 2)
        
        return all_detailed_players
    
    def _save_progress(self, players_data, count):
        """Save progress to file"""
        try:
            df = pd.DataFrame(players_data)
            progress_file = f'players_ULTRA_FAST_{count}.csv'
            df.to_csv(progress_file, index=False, encoding='utf-8')
            print(f"    💾 Progress saved: {progress_file} ({count} players)")
        except Exception as e:
            print(f"    ❌ Error saving progress: {e}")
    
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
        print(f"📊 Loaded {len(players_df)} players from players_ALL_LEAGUES.csv")
    except FileNotFoundError:
        print("❌ Error: players_ALL_LEAGUES.csv not found!")
        return
    
    # Initialize ultra-fast scraper
    scraper = UltraFastScraper(max_workers=5, batch_size=100)
    
    # Process all players
    print(f"\n🚀 Starting ULTRA-FAST processing of all {len(players_df)} players...")
    print("⚡ This should take approximately 1-2 hours...")
    
    start_time = time.time()
    detailed_players = scraper.process_all_players_fast(players_df, save_interval=200)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    if detailed_players:
        # Save final detailed data
        df_detailed = pd.DataFrame(detailed_players)
        csv_file = 'players_ULTRA_FAST_FINAL.csv'
        df_detailed.to_csv(csv_file, index=False, encoding='utf-8')
        
        # Get statistics
        stats = scraper.get_stats()
        
        print(f"\n🎉 ULTRA-FAST RESULTS")
        print(f"📁 Final data: {csv_file}")
        print(f"👥 Total players: {len(detailed_players)}")
        print(f"⏱️  Processing time: {processing_time/3600:.2f} hours")
        print(f"✅ Successful requests: {stats['successful_requests']}")
        print(f"❌ Failed requests: {stats['failed_requests']}")
        print(f"📈 Success rate: {stats['success_rate']:.1f}%")
        
        # Show sample of detailed data
        print(f"\n📋 Sample Detailed Data")
        sample_cols = ['full_name', 'team_name', 'competition', 'age', 'nationality', 'position', 'market_value']
        available_cols = [col for col in sample_cols if col in df_detailed.columns]
        if available_cols:
            print(df_detailed[available_cols].head(10).to_string())
        
        return df_detailed
    else:
        print("❌ No detailed player data collected!")
        return None

if __name__ == "__main__":
    df = main()
