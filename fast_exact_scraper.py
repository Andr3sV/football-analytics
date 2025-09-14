#!/usr/bin/env python3
"""
Fast exact scraper - accelerated version with reduced delays
"""
import requests
import pandas as pd
import time
import random
import json
import os
import glob
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from datetime import datetime

class FastExactScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.successful_requests = 0
        self.failed_requests = 0
        self.processed_count = 0
        self.total_players = 0
        
    def _get_random_headers(self):
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
    
    def _random_delay(self, min_delay=2, max_delay=5):
        """FASTER: Reduced delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _make_request(self, url, max_retries=2):
        """FASTER: Reduced retries"""
        for attempt in range(max_retries):
            try:
                headers = self._get_random_headers()
                if attempt > 0:
                    self._random_delay(3, 8)
                response = self.session.get(url, headers=headers, timeout=20, allow_redirects=True)
                if response.status_code == 200:
                    self.successful_requests += 1
                    return response
                elif response.status_code == 403:
                    if attempt < max_retries - 1:
                        self._random_delay(5, 15)
                    continue
                else:
                    continue
            except Exception:
                if attempt < max_retries - 1:
                    self._random_delay(3, 8)
                continue
        self.failed_requests += 1
        return None
    
    def extract_player_details(self, player_data):
        player_url = player_data.get('profile_url', '')
        response = self._make_request(player_url)
        if not response:
            return player_data
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
                # Exact market value
                mv_exact = None
                m = re.search(r'Market value:\s*(€[^\s➤]+)', description)
                if m:
                    mv_exact = m.group(1).strip()
                else:
                    m2 = re.search(r'€([0-9.,]+)\s*(mio|th\.)', description)
                    if m2:
                        val, unit = m2.group(1), m2.group(2)
                        if unit == 'mio':
                            mv_exact = f"€{val}m"
                        elif unit == 'th.':
                            mv_exact = f"€{val}k"
                if mv_exact:
                    player_data['market_value'] = mv_exact
                # Age
                age_match = re.search(r'(\d+),', description)
                if age_match:
                    player_data['age'] = int(age_match.group(1))
                # Nationality
                nationality_match = re.search(r'from\s+([^➤]+)', description)
                if nationality_match:
                    player_data['nationality'] = nationality_match.group(1).strip()
                # Current club
                club_match = re.search(r'➤\s*([^,]+),', description)
                if club_match:
                    player_data['current_club'] = club_match.group(1).strip()
                # Position
                position_match = re.search(r'➤\s*[^➤]*➤\s*([^➤]+)➤', description)
                if position_match:
                    player_data['position'] = position_match.group(1).strip()
                # Birth
                birth_match = re.search(r'\*\s*(\d{2}\.\d{2}\.\d{4})\s+in\s+([^,]+),\s*([^➤]+)', description)
                if birth_match:
                    player_data['date_of_birth'] = birth_match.group(1)
                    player_data['city_of_birth'] = birth_match.group(2).strip()
                    player_data['country_of_birth'] = birth_match.group(3).strip()
                    player_data['place_of_birth'] = f"{birth_match.group(2).strip()}, {birth_match.group(3).strip()}"
            # Additional
            self._extract_additional_data(soup, player_data)
        except Exception:
            pass
        return player_data
    
    def _extract_additional_data(self, soup, player_data):
        try:
            all_text = soup.get_text()
            if not player_data.get('height_cm'):
                for pattern in [r'(\d+)\s*cm', r'Height:\s*(\d+)\s*cm', r'Größe:\s*(\d+)\s*cm']:
                    m = re.search(pattern, all_text, re.IGNORECASE)
                    if m:
                        player_data['height_cm'] = m.group(1)
                        break
            if not player_data.get('dominant_foot'):
                for pattern in [r'Foot:\s*(left|right|both)', r'Dominant foot:\s*(left|right|both)', r'Preferred foot:\s*(left|right|both)', r'Füßigkeit:\s*(links|rechts|beidfüßig)', r'(\w+)\s*foot']:
                    m = re.search(pattern, all_text, re.IGNORECASE)
                    if m:
                        foot = m.group(1).lower()
                        if foot in ['left', 'links']:
                            player_data['dominant_foot'] = 'left'
                        elif foot in ['right', 'rechts']:
                            player_data['dominant_foot'] = 'right'
                        elif foot in ['both', 'beidfüßig']:
                            player_data['dominant_foot'] = 'both'
                        break
            if not player_data.get('agent'):
                for pattern in [r'Agent:\s*([^\n]+)', r'Represented by:\s*([^\n]+)', r'Berater:\s*([^\n]+)', r'Representative:\s*([^\n]+)']:
                    m = re.search(pattern, all_text, re.IGNORECASE)
                    if m:
                        player_data['agent'] = m.group(1).strip()
                        break
            social_links = []
            for selector in ['a[href*="instagram.com"]','a[href*="twitter.com"]','a[href*="facebook.com"]']:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and 'transfermarkt' not in href:
                        social_links.append(href)
            if social_links:
                player_data['social_links'] = json.dumps(social_links)
        except Exception:
            pass
    
    def process_all_players(self, players_df, save_interval=50):
        """FASTER: Save progress every 50 players instead of 100"""
        self.total_players = len(players_df)
        all_detailed_players = []
        for idx, (_, player) in enumerate(players_df.iterrows()):
            try:
                detailed = self.extract_player_details(player.to_dict())
                all_detailed_players.append(detailed)
                self.processed_count += 1
                if (idx + 1) % 50 == 0:
                    print(f"✓ Processed {idx + 1}/{self.total_players}")
                if (idx + 1) % save_interval == 0:
                    self._save_progress(all_detailed_players, idx + 1)
                if idx < self.total_players - 1:
                    # FASTER: Reduced delay between requests
                    delay = random.uniform(2, 5)
                    time.sleep(delay)
            except Exception as e:
                print(f"❌ Error processing {player.get('full_name', 'Unknown')}: {e}")
                all_detailed_players.append(player.to_dict())
        return all_detailed_players
    
    def _save_progress(self, players_data, count):
        try:
            df = pd.DataFrame(players_data)
            progress_file = f'players_FAST_EXACT_PROGRESS_{count}.csv'
            df.to_csv(progress_file, index=False, encoding='utf-8')
            print(f"💾 Progress saved: {progress_file}")
        except Exception as e:
            print(f"❌ Error saving progress: {e}")


def main():
    try:
        players_df = pd.read_csv('players_ALL_LEAGUES.csv')
        print(f"Loaded {len(players_df)} players from players_ALL_LEAGUES.csv")
    except FileNotFoundError:
        print("Error: players_ALL_LEAGUES.csv not found!")
        return
    
    # Check for existing progress and continue from there
    progress_files = glob.glob('players_EXACT_DETAILED_PROGRESS_*.csv')
    if progress_files:
        latest_progress = max(progress_files, key=os.path.getctime)
        existing_df = pd.read_csv(latest_progress)
        start_index = len(existing_df)
        print(f"📁 Found existing progress: {latest_progress}")
        print(f"📊 Continuing from player {start_index + 1}")
        # Load existing data
        existing_players = existing_df.to_dict('records')
    else:
        start_index = 0
        existing_players = []
        print("🚀 Starting fresh - no existing progress found")
    
    scraper = FastExactScraper()
    print(f"Starting FAST EXACT processing from player {start_index + 1}/{len(players_df)}...")
    print("⚡ FASTER: 2-5s delays, save every 50 players, reduced retries")
    print("Progress will be saved every 50 players.")
    start = time.time()
    
    # Process remaining players
    remaining_players = players_df.iloc[start_index:]
    detailed_players = scraper.process_all_players(remaining_players, save_interval=50)
    
    # Combine with existing data
    all_detailed_players = existing_players + detailed_players
    end = time.time()
    if all_detailed_players:
        df = pd.DataFrame(all_detailed_players)
        out = 'players_FAST_EXACT_FINAL.csv'
        df.to_csv(out, index=False, encoding='utf-8')
        print(f"Saved final detailed data to: {out}")
        print(f"Total players processed: {len(all_detailed_players)}")
        print(f"New players processed this session: {len(detailed_players)}")
        print(f"Elapsed time: {(end-start)/3600:.2f} hours")
    else:
        print("No detailed player data collected!")

if __name__ == "__main__":
    main()
