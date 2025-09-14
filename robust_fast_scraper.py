#!/usr/bin/env python3
"""
Robust Fast Scraper with Better Error Handling and Timeouts
"""
import pandas as pd
import requests
import time
import json
import glob
import os
import re
import random
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import cloudscraper

class RobustFastScraper:
    def __init__(self):
        self.session = cloudscraper.create_scraper()
        self.ua = UserAgent()
        self.processed_players = set()
        self.detailed_players = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.save_interval = 50  # Save every 50 players
        
    def _random_delay(self, min_delay=3, max_delay=7):
        """Random delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _get_headers(self):
        """Get random headers"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def get_existing_progress(self):
        """Get existing progress and determine starting point"""
        progress_files = glob.glob('players_FAST_EXACT_PROGRESS_*.csv')
        if not progress_files:
            return [], 0
        
        latest_file = max(progress_files, key=os.path.getctime)
        print(f"📂 Loading existing progress from: {latest_file}")
        
        try:
            existing_df = pd.read_csv(latest_file)
            existing_players = existing_df.to_dict('records')
            
            # Get the last processed player index
            all_players_df = pd.read_csv('players_ALL_LEAGUES.csv')
            last_processed_name = existing_players[-1]['full_name'] if existing_players else None
            
            start_index = 0
            if last_processed_name:
                for i, player in all_players_df.iterrows():
                    if player['full_name'] == last_processed_name:
                        start_index = i + 1
                        break
            
            print(f"✅ Found {len(existing_players)} existing players")
            print(f"🚀 Resuming from player index: {start_index}")
            
            return existing_players, start_index
            
        except Exception as e:
            print(f"❌ Error loading existing progress: {e}")
            return [], 0
    
    def extract_player_details(self, player_data):
        """Extract detailed player information with robust error handling"""
        try:
            profile_url = player_data.get('profile_url', '')
            if not profile_url:
                return None
            
            print(f"    🌐 Fetching: {player_data.get('full_name', 'Unknown')}")
            
            # Make request with timeout and retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.session.get(
                        profile_url, 
                        headers=self._get_headers(),
                        timeout=30  # 30 second timeout
                    )
                    
                    if response.status_code == 200:
                        break
                    elif response.status_code == 429:  # Rate limited
                        print(f"    ⏳ Rate limited, waiting 60 seconds...")
                        time.sleep(60)
                        continue
                    else:
                        print(f"    ⚠️  HTTP {response.status_code}, attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            time.sleep(10)
                            continue
                        else:
                            return None
                            
                except requests.exceptions.Timeout:
                    print(f"    ⏱️  Timeout, attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(15)
                        continue
                    else:
                        return None
                        
                except requests.exceptions.RequestException as e:
                    print(f"    ❌ Request error: {e}, attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(15)
                        continue
                    else:
                        return None
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract player details
            player_details = player_data.copy()
            
            # Market value - exact string as it appears
            market_value = "Not found"
            try:
                market_value_elem = soup.find('a', {'title': re.compile(r'Market value', re.I)})
                if market_value_elem:
                    market_value = market_value_elem.get_text(strip=True)
                else:
                    # Alternative selectors
                    for selector in ['span[data-testid="market-value"]', '.tm-player-market-value-development__current-value']:
                        elem = soup.select_one(selector)
                        if elem:
                            market_value = elem.get_text(strip=True)
                            break
            except:
                pass
            
            player_details['market_value'] = market_value
            
            # Extract from meta description for structured data
            meta_desc = ""
            try:
                meta_elem = soup.find('meta', {'name': 'description'})
                if meta_elem:
                    meta_desc = meta_elem.get('content', '')
            except:
                pass
            
            # Age
            age = "Not found"
            try:
                age_match = re.search(r'Age:\s*(\d+)', meta_desc)
                if age_match:
                    age = float(age_match.group(1))
                else:
                    # Try alternative patterns
                    for pattern in [r'(\d+)\s*years?\s*old', r'Age\s*(\d+)', r'(\d+)\s*yo']:
                        match = re.search(pattern, meta_desc, re.I)
                        if match:
                            age = float(match.group(1))
                            break
            except:
                pass
            
            player_details['age'] = age
            
            # Nationality
            nationality = "Not found"
            try:
                nat_match = re.search(r'Nationality:\s*([^,]+)', meta_desc)
                if nat_match:
                    nationality = nat_match.group(1).strip()
                else:
                    # Try alternative patterns
                    for pattern in [r'Citizenship:\s*([^,]+)', r'Country:\s*([^,]+)']:
                        match = re.search(pattern, meta_desc, re.I)
                        if match:
                            nationality = match.group(1).strip()
                            break
            except:
                pass
            
            player_details['nationality'] = nationality
            
            # Current club
            current_club = player_data.get('team_name', 'Not found')
            player_details['current_club'] = current_club
            
            # Position
            position = "Not found"
            try:
                pos_match = re.search(r'Position:\s*([^,]+)', meta_desc)
                if pos_match:
                    position = pos_match.group(1).strip()
                else:
                    # Try alternative patterns
                    for pattern in [r'Playing position:\s*([^,]+)', r'Role:\s*([^,]+)']:
                        match = re.search(pattern, meta_desc, re.I)
                        if match:
                            position = match.group(1).strip()
                            break
            except:
                pass
            
            player_details['position'] = position
            
            # Date of birth
            date_of_birth = "Not found"
            try:
                dob_match = re.search(r'Born:\s*([^,]+)', meta_desc)
                if dob_match:
                    date_of_birth = dob_match.group(1).strip()
                else:
                    # Try alternative patterns
                    for pattern in [r'Birth date:\s*([^,]+)', r'Date of birth:\s*([^,]+)']:
                        match = re.search(pattern, meta_desc, re.I)
                        if match:
                            date_of_birth = match.group(1).strip()
                            break
            except:
                pass
            
            player_details['date_of_birth'] = date_of_birth
            
            # Place of birth
            place_of_birth = "Not found"
            try:
                pob_match = re.search(r'Place of birth:\s*([^,]+)', meta_desc)
                if pob_match:
                    place_of_birth = pob_match.group(1).strip()
                else:
                    # Try alternative patterns
                    for pattern in [r'Born in:\s*([^,]+)', r'Birth place:\s*([^,]+)']:
                        match = re.search(pattern, meta_desc, re.I)
                        if match:
                            place_of_birth = match.group(1).strip()
                            break
            except:
                pass
            
            player_details['place_of_birth'] = place_of_birth
            
            # City and country of birth
            city_of_birth = "Not found"
            country_of_birth = "Not found"
            try:
                if ',' in place_of_birth:
                    parts = place_of_birth.split(',')
                    city_of_birth = parts[0].strip()
                    country_of_birth = parts[-1].strip()
                else:
                    city_of_birth = place_of_birth
                    country_of_birth = "Not found"
            except:
                pass
            
            player_details['city_of_birth'] = city_of_birth
            player_details['country_of_birth'] = country_of_birth
            
            # Dominant foot
            dominant_foot = "Not found"
            try:
                foot_match = re.search(r'Foot:\s*([^,]+)', meta_desc)
                if foot_match:
                    dominant_foot = foot_match.group(1).strip()
                else:
                    # Try alternative patterns
                    for pattern in [r'Preferred foot:\s*([^,]+)', r'Strong foot:\s*([^,]+)']:
                        match = re.search(pattern, meta_desc, re.I)
                        if match:
                            dominant_foot = match.group(1).strip()
                            break
            except:
                pass
            
            player_details['dominant_foot'] = dominant_foot
            
            # Agent
            agent = "Not found"
            try:
                agent_match = re.search(r'Agent:\s*([^,]+)', meta_desc)
                if agent_match:
                    agent = agent_match.group(1).strip()
                else:
                    # Try alternative patterns
                    for pattern in [r'Representative:\s*([^,]+)', r'Manager:\s*([^,]+)']:
                        match = re.search(pattern, meta_desc, re.I)
                        if match:
                            agent = match.group(1).strip()
                            break
            except:
                pass
            
            player_details['agent'] = agent
            
            # Social links
            social_links = []
            try:
                # Look for social media links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if any(social in href.lower() for social in ['instagram', 'twitter', 'facebook', 'tiktok']):
                        social_links.append(href)
                
                player_details['social_links'] = json.dumps(social_links) if social_links else "[]"
            except:
                player_details['social_links'] = "[]"
            
            print(f"    ✅ Extracted details for {player_data.get('full_name', 'Unknown')}")
            return player_details
            
        except Exception as e:
            print(f"    ❌ Error extracting details: {e}")
            return None
    
    def save_progress(self, players_data, count):
        """Save progress to CSV"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'players_ROBUST_PROGRESS_{count}.csv'
            
            df = pd.DataFrame(players_data)
            df.to_csv(filename, index=False)
            
            print(f"💾 Saved progress: {filename} ({len(players_data)} players)")
            
        except Exception as e:
            print(f"❌ Error saving progress: {e}")
    
    def process_all_players(self):
        """Process all players with robust error handling"""
        print("🔍 Starting Robust Fast Scraper...")
        print("📊 Extracting detailed player information...")
        
        # Load existing progress
        existing_players, start_index = self.get_existing_progress()
        
        # Load all players
        try:
            all_players_df = pd.read_csv('players_ALL_LEAGUES.csv')
            total_players = len(all_players_df)
            print(f"📊 Total players to process: {total_players}")
            print(f"🚀 Starting from index: {start_index}")
            
        except Exception as e:
            print(f"❌ Error loading players: {e}")
            return
        
        # Process remaining players
        remaining_players = all_players_df.iloc[start_index:].to_dict('records')
        
        print(f"📋 Processing {len(remaining_players)} remaining players...")
        
        for i, player in enumerate(remaining_players):
            try:
                player_name = player.get('full_name', '')
                
                if not player_name or player_name in self.processed_players:
                    continue
                
                print(f"  🔍 Processing {start_index + i + 1}/{total_players}: {player_name}")
                
                # Extract detailed information
                detailed_player = self.extract_player_details(player)
                
                if detailed_player:
                    self.detailed_players.append(detailed_player)
                    self.successful_requests += 1
                    print(f"    ✅ Success")
                else:
                    self.failed_requests += 1
                    print(f"    ❌ Failed")
                
                self.processed_players.add(player_name)
                
                # Save progress periodically
                if (i + 1) % self.save_interval == 0:
                    current_count = start_index + i + 1
                    all_players_data = existing_players + self.detailed_players
                    self.save_progress(all_players_data, current_count)
                
                # Random delay between requests
                self._random_delay()
                
            except KeyboardInterrupt:
                print("\n⏹️  Stopping scraper...")
                break
            except Exception as e:
                print(f"❌ Error processing player: {e}")
                self.failed_requests += 1
                continue
        
        # Final save
        if self.detailed_players:
            final_count = len(existing_players) + len(self.detailed_players)
            all_players_data = existing_players + self.detailed_players
            self.save_progress(all_players_data, final_count)
        
        # Summary
        print(f"\n📊 Robust Scraper Summary:")
        print(f"  ✅ Successful requests: {self.successful_requests}")
        print(f"  ❌ Failed requests: {self.failed_requests}")
        print(f"  📝 Total players processed: {len(self.processed_players)}")

def main():
    """Main function"""
    scraper = RobustFastScraper()
    
    try:
        scraper.process_all_players()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔚 Robust scraper finished")

if __name__ == "__main__":
    main()
