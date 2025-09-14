#!/usr/bin/env python3
"""
Final Stealth Scraper - Optimized with corrected detection logic
Uses undetected-chromedriver with proper blocking detection
"""
import pandas as pd
import time
import json
import glob
import os
import re
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

class FinalStealthScraper:
    def __init__(self):
        self.driver = None
        self.processed_players = set()
        self.detailed_players = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.save_interval = 25  # Save every 25 players
        self.request_count = 0
        self.session_start_time = datetime.now()
        
    def setup_undetected_driver(self):
        """Setup undetected Chrome driver"""
        print("🛡️ Setting up final stealth browser...")
        
        try:
            options = uc.ChromeOptions()
            
            # Essential stealth options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-translate')
            
            # Window size
            options.add_argument('--window-size=1920,1080')
            
            # Language preferences
            options.add_experimental_option('prefs', {
                'intl.accept_languages': 'en-US,en,es,de,fr',
                'profile.default_content_setting_values': {
                    'notifications': 2,
                    'media_stream': 2,
                    'geolocation': 2
                }
            })
            
            # Create undetected driver
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Additional stealth measures
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            # Set timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            print("✅ Final stealth browser configured")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up driver: {e}")
            return False
    
    def close_driver(self):
        """Close browser driver safely"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def intelligent_delay(self):
        """Intelligent delay with human-like patterns"""
        base_delay = random.uniform(5, 12)  # Base delay 5-12 seconds
        
        # Increase delay if we've made many requests
        if self.request_count > 0:
            time_since_start = (datetime.now() - self.session_start_time).total_seconds()
            requests_per_minute = self.request_count / (time_since_start / 60)
            
            if requests_per_minute > 6:  # If more than 6 requests per minute
                base_delay *= random.uniform(2, 4)
                print(f"    🐌 Slowing down due to high request rate: {base_delay:.1f}s")
        
        # Add random micro-delays
        micro_delays = [0.3, 0.7, 1.2, 1.8, 2.5]
        base_delay += random.choice(micro_delays)
        
        # Occasionally add longer delays
        if random.random() < 0.12:  # 12% chance
            base_delay += random.uniform(10, 25)
            print(f"    ☕ Taking a longer break: {base_delay:.1f}s")
        
        time.sleep(base_delay)
    
    def simulate_human_behavior(self):
        """Simulate human browsing behavior"""
        if random.random() < 0.06:  # 6% chance
            try:
                random_pages = [
                    'https://www.transfermarkt.com/',
                    'https://www.transfermarkt.com/wettbewerbe/europa',
                    'https://www.transfermarkt.com/transfers/transferrekorde/statistik'
                ]
                
                random_page = random.choice(random_pages)
                print(f"    🎭 Simulating human behavior: visiting {random_page}")
                
                self.driver.get(random_page)
                time.sleep(random.uniform(3, 6))
                
                # Simulate scrolling
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(random.uniform(1, 3))
                
                print(f"    ✅ Human behavior simulation completed")
                
            except Exception as e:
                print(f"    ⚠️  Human behavior simulation failed: {e}")
    
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
    
    def is_page_blocked(self, page_source, player_name):
        """Check if page is blocked with improved logic"""
        try:
            # Check for obvious blocking indicators
            blocking_indicators = [
                'access denied', 'blocked', 'forbidden', 'cloudflare',
                'please enable javascript', 'security check', 'bot detection'
            ]
            
            page_lower = page_source.lower()
            for indicator in blocking_indicators:
                if indicator in page_lower:
                    return True
            
            # Check if page is too small (less than 50KB is suspicious)
            if len(page_source) < 50000:
                return True
            
            # Check if player name appears in the page (good sign)
            if player_name.lower() in page_lower:
                return False
            
            # Check if we have typical Transfermarkt elements
            transfermarkt_indicators = [
                'transfermarkt', 'market value', 'profil', 'spieler',
                'wettbewerb', 'verein', 'transfers'
            ]
            
            indicators_found = sum(1 for indicator in transfermarkt_indicators if indicator in page_lower)
            if indicators_found >= 2:
                return False
            
            # If we can't determine, assume blocked for safety
            return True
            
        except Exception:
            return True
    
    def extract_player_details(self, player_data):
        """Extract detailed player information"""
        try:
            profile_url = player_data.get('profile_url', '')
            if not profile_url:
                return None
            
            player_name = player_data.get('full_name', 'Unknown')
            print(f"    🌐 Stealth fetching: {player_name}")
            
            # Simulate human behavior occasionally
            self.simulate_human_behavior()
            
            # Navigate to player page
            try:
                self.driver.get(profile_url)
                self.request_count += 1
                
                # Wait for page to load
                time.sleep(random.uniform(3, 6))
                
                # Get page source
                page_source = self.driver.page_source
                print(f"    📊 Page loaded: {len(page_source)} characters")
                
                # Check if blocked
                if self.is_page_blocked(page_source, player_name):
                    print(f"    🚫 Page appears to be blocked")
                    return None
                
                print(f"    ✅ Page loaded successfully")
                
            except Exception as e:
                print(f"    ❌ Error loading page: {e}")
                return None
            
            # Parse page with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
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
            
            # Extract from meta description
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
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if any(social in href.lower() for social in ['instagram', 'twitter', 'facebook', 'tiktok']):
                        social_links.append(href)
                
                player_details['social_links'] = json.dumps(social_links) if social_links else "[]"
            except:
                player_details['social_links'] = "[]"
            
            print(f"    ✅ Extracted details for {player_name}")
            return player_details
            
        except Exception as e:
            print(f"    ❌ Error extracting details: {e}")
            return None
    
    def save_progress(self, players_data, count):
        """Save progress to CSV"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'players_FINAL_STEALTH_PROGRESS_{count}.csv'
            
            df = pd.DataFrame(players_data)
            df.to_csv(filename, index=False)
            
            print(f"💾 Saved progress: {filename} ({len(players_data)} players)")
            
        except Exception as e:
            print(f"❌ Error saving progress: {e}")
    
    def process_all_players(self):
        """Process all players with final stealth"""
        print("🛡️ Starting Final Stealth Scraper...")
        print("📊 Extracting detailed player information with ultimate anti-detection...")
        
        # Setup browser
        if not self.setup_undetected_driver():
            print("❌ Failed to setup browser")
            return
        
        try:
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
            
            print(f"📋 Processing {len(remaining_players)} remaining players with final stealth...")
            
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
                    
                    # Intelligent delay between requests
                    self.intelligent_delay()
                    
                except KeyboardInterrupt:
                    print("\n⏹️  Stopping final stealth scraper...")
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
            print(f"\n📊 Final Stealth Scraper Summary:")
            print(f"  ✅ Successful requests: {self.successful_requests}")
            print(f"  ❌ Failed requests: {self.failed_requests}")
            print(f"  📝 Total players processed: {len(self.processed_players)}")
            print(f"  🕐 Total session time: {datetime.now() - self.session_start_time}")
            
        finally:
            self.close_driver()

def main():
    """Main function"""
    scraper = FinalStealthScraper()
    
    try:
        scraper.process_all_players()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔚 Final stealth scraper finished")

if __name__ == "__main__":
    main()
