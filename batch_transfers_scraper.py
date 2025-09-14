#!/usr/bin/env python3
"""
Batch Transfers Scraper - Process players in small batches with long delays
Strategy to avoid Transfermarkt's aggressive bot detection
"""
import pandas as pd
import time
import json
import os
import re
import random
from datetime import datetime, date
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BatchTransfersScraper:
    def __init__(self):
        self.driver = None
        self.solidarity_data = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.blocked_requests = 0
        self.processed_count = 0
        
    def setup_driver(self):
        """Setup Chrome driver with maximum stealth"""
        print("🛡️ Setting up batch transfers browser...")
        
        try:
            # Kill any existing Chrome processes
            os.system('pkill -f chrome 2>/dev/null || true')
            time.sleep(5)
            
            options = uc.ChromeOptions()
            
            # Basic options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # Maximum anti-detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-breakpad')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-prompt-on-repost')
            options.add_argument('--disable-domain-reliability')
            options.add_argument('--disable-component-extensions-with-background-pages')
            
            # Random user agent
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # Language preferences
            options.add_experimental_option('prefs', {
                'intl.accept_languages': 'en-US,en,es,de,fr',
                'profile.default_content_setting_values': {
                    'notifications': 2,
                    'media_stream': 2,
                    'geolocation': 2,
                    'cookies': 1
                },
                'profile.managed_default_content_settings': {
                    'images': 1
                }
            })
            
            # Create driver
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Enhanced stealth measures
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            self.driver.execute_script("Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})")
            
            # Randomize viewport
            self.driver.set_window_size(1920 + random.randint(-100, 100), 1080 + random.randint(-100, 100))
            
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(20)
            
            print("✅ Batch transfers browser configured")
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
    
    def long_delay(self, min_seconds=30, max_seconds=60):
        """Long delay to avoid detection"""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"    ⏱️  Long delay: {delay:.1f} seconds...")
        time.sleep(delay)
    
    def extract_player_id_from_url(self, profile_url):
        """Extract player ID from Transfermarkt profile URL"""
        try:
            match = re.search(r'/spieler/(\d+)', profile_url)
            if match:
                return match.group(1)
            return None
        except:
            return None
    
    def extract_birth_date_from_profile(self, player_name, profile_url):
        """Extract player birth date from profile page with maximum stealth"""
        try:
            print(f"    🌐 Loading profile page...")
            self.driver.get(profile_url)
            
            # Very long delay
            self.long_delay(20, 40)
            
            # Get page source
            page_source = self.driver.page_source
            
            # Check if page loaded properly
            if len(page_source) < 10000:
                print(f"    ❌ Profile page too small: {len(page_source)} chars")
                self.blocked_requests += 1
                return None
            
            print(f"    ✅ Profile page loaded: {len(page_source)} chars")
            
            # Look for birth date patterns
            birth_patterns = [
                r'Date of birth/Age:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                r'Birth date:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                r'Born:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                r'(\d{1,2}[/.]\d{1,2}[/.]\d{4})\s*\([0-9]+\)',
                r'Geburtsdatum:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                r'Fecha de nacimiento:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})'
            ]
            
            for pattern in birth_patterns:
                match = re.search(pattern, page_source, re.IGNORECASE)
                if match:
                    birth_date = match.group(1)
                    print(f"    ✅ Found birth date: {birth_date}")
                    return birth_date
            
            print(f"    ❌ No birth date found in profile")
            return None
            
        except Exception as e:
            print(f"    ❌ Error extracting birth date: {e}")
            return None
    
    def extract_transfer_history_from_url(self, player_name, player_id):
        """Extract transfer history from transfers URL with maximum stealth"""
        try:
            # Construct transfers URL
            transfers_url = f"https://www.transfermarkt.com/{player_name.lower().replace(' ', '-')}/transfers/spieler/{player_id}"
            print(f"    🌐 Loading transfers page: {transfers_url}")
            
            self.driver.get(transfers_url)
            
            # Very long delay
            self.long_delay(25, 50)
            
            # Get page source
            page_source = self.driver.page_source
            
            # Check if page loaded properly
            if len(page_source) < 50000:
                print(f"    ❌ Transfers page too small: {len(page_source)} chars")
                self.blocked_requests += 1
                return []
            
            print(f"    ✅ Transfers page loaded: {len(page_source)} chars")
            
            # Look for transfer table data
            transfers = []
            
            # Try to find transfer rows using regex patterns
            lines = page_source.split('\n')
            current_transfer = {}
            
            for line in lines:
                line = line.strip()
                
                # Look for date patterns
                date_match = re.search(r'(\d{2}[/.]\d{2}[/.]\d{4})', line)
                if date_match:
                    current_transfer['date'] = date_match.group(1)
                
                # Look for club names
                if 'href="/' in line and ('verein/' in line or 'club/' in line):
                    club_match = re.search(r'title="([^"]*)"', line)
                    if club_match:
                        club_name = club_match.group(1)
                        if 'left_club' not in current_transfer:
                            current_transfer['left_club'] = club_name
                        else:
                            current_transfer['joined_club'] = club_name
                
                # Look for transfer fee
                fee_match = re.search(r'€([0-9,.]+[mk]?)', line)
                if fee_match:
                    current_transfer['transfer_fee'] = f"€{fee_match.group(1)}"
                
                # If we have enough data, save the transfer
                if len(current_transfer) >= 3:
                    if current_transfer.get('date') and current_transfer.get('left_club'):
                        transfers.append(current_transfer.copy())
                        current_transfer = {}
            
            # Fallback: try to find any table with transfer-like data
            if not transfers:
                print(f"    🔍 Trying fallback method...")
                
                # Look for any table structure
                table_matches = re.findall(r'<table[^>]*class="[^"]*items[^"]*"[^>]*>(.*?)</table>', page_source, re.DOTALL)
                
                for table_html in table_matches:
                    # Extract rows
                    row_matches = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
                    
                    for row in row_matches[1:]:  # Skip header
                        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                        if len(cells) >= 4:
                            # Clean up cell content
                            clean_cells = []
                            for cell in cells:
                                clean_cell = re.sub(r'<[^>]*>', '', cell).strip()
                                clean_cells.append(clean_cell)
                            
                            if len(clean_cells) >= 4:
                                transfers.append({
                                    'season': clean_cells[0] if len(clean_cells) > 0 else '',
                                    'date': clean_cells[1] if len(clean_cells) > 1 else '',
                                    'left_club': clean_cells[2] if len(clean_cells) > 2 else '',
                                    'joined_club': clean_cells[3] if len(clean_cells) > 3 else '',
                                    'market_value': clean_cells[4] if len(clean_cells) > 4 else '',
                                    'transfer_fee': clean_cells[5] if len(clean_cells) > 5 else ''
                                })
            
            # Filter out invalid transfers
            valid_transfers = []
            for transfer in transfers:
                if transfer.get('date') and len(transfer['date']) > 5:
                    valid_transfers.append(transfer)
            
            print(f"    ✅ Extracted {len(valid_transfers)} transfers")
            return valid_transfers
            
        except Exception as e:
            print(f"    ❌ Error extracting transfer history: {e}")
            return []
    
    def calculate_age_at_transfer(self, birth_date_str, transfer_date_str):
        """Calculate player age at the time of transfer"""
        try:
            # Parse birth date
            birth_date = None
            for fmt in ['%d/%m/%Y', '%d.%m.%Y', '%Y-%m-%d', '%m/%d/%Y']:
                try:
                    birth_date = datetime.strptime(birth_date_str, fmt).date()
                    break
                except:
                    continue
            
            if not birth_date:
                return None
            
            # Parse transfer date
            transfer_date = None
            for fmt in ['%d/%m/%Y', '%d.%m.%Y', '%Y-%m-%d', '%m/%d/%Y']:
                try:
                    transfer_date = datetime.strptime(transfer_date_str, fmt).date()
                    break
                except:
                    continue
            
            if not transfer_date:
                return None
            
            # Calculate age
            age = transfer_date.year - birth_date.year
            if transfer_date.month < birth_date.month or (transfer_date.month == birth_date.month and transfer_date.day < birth_date.day):
                age -= 1
            
            return age
        except:
            return None
    
    def calculate_contribution_amount(self, transfer_fee):
        """Calculate solidarity contribution amount (5% of transfer fee)"""
        try:
            fee_str = transfer_fee.lower().replace('€', '').replace(',', '').strip()
            
            if 'free transfer' in fee_str or fee_str == '-' or fee_str == '' or 'loan' in fee_str:
                return '€0'
            
            if 'm' in fee_str:
                value = float(re.search(r'(\d+\.?\d*)', fee_str).group(1))
                contribution = value * 0.05
                return f"€{contribution:.2f}m"
            elif 'k' in fee_str:
                value = float(re.search(r'(\d+\.?\d*)', fee_str).group(1))
                contribution = value * 0.05
                return f"€{contribution:.0f}k"
            else:
                match = re.search(r'(\d+\.?\d*)', fee_str)
                if match:
                    value = float(match.group(1))
                    contribution = value * 0.05
                    return f"€{contribution:.2f}"
            
            return '€0'
            
        except:
            return '€0'
    
    def calculate_solidarity_contributions(self, player_name, birth_date, transfers):
        """Calculate solidarity contributions based on transfer history"""
        try:
            if not birth_date or not transfers:
                return []
            
            solidarity_contributions = []
            
            for transfer in transfers:
                try:
                    age = self.calculate_age_at_transfer(birth_date, transfer['date'])
                    
                    if age is None:
                        continue
                    
                    if 12 <= age <= 23:
                        club = transfer.get('left_club', '') or transfer.get('joined_club', '')
                        
                        if club and club.lower() not in ['without club', 'free agent', '-', '']:
                            transfer_fee = transfer.get('transfer_fee', '€0')
                            contribution = self.calculate_contribution_amount(transfer_fee)
                            
                            solidarity_contributions.append({
                                'player_name': player_name,
                                'club': club,
                                'transfer_date': transfer['date'],
                                'player_age_at_transfer': age,
                                'transfer_fee': transfer_fee,
                                'solidarity_contribution': contribution,
                                'season': transfer.get('season', ''),
                                'extracted_at': datetime.now().isoformat()
                            })
                            
                            print(f"    ✅ Age {age}: {club} -> {contribution}")
                            
                except Exception as e:
                    continue
            
            return solidarity_contributions
            
        except Exception as e:
            print(f"    ❌ Error calculating solidarity contributions: {e}")
            return []
    
    def extract_solidarity_data(self, player):
        """Extract solidarity contribution data for a player"""
        try:
            player_name = player.get('full_name', '')
            profile_url = player.get('profile_url', '')
            
            if not player_name or not profile_url:
                return []
            
            print(f"  🔍 Processing: {player_name}")
            
            # Extract player ID
            player_id = self.extract_player_id_from_url(profile_url)
            if not player_id:
                print(f"    ❌ Could not extract player ID")
                return []
            
            print(f"    ✅ Player ID: {player_id}")
            
            # Extract birth date
            print(f"    📅 Extracting birth date...")
            birth_date = self.extract_birth_date_from_profile(player_name, profile_url)
            if not birth_date:
                print(f"    ❌ No birth date found")
                return []
            
            # Very long delay between profile and transfers page
            self.long_delay(30, 60)
            
            # Extract transfer history
            print(f"    📊 Extracting transfer history...")
            transfers = self.extract_transfer_history_from_url(player_name, player_id)
            if not transfers:
                print(f"    ❌ No transfers found")
                return []
            
            # Calculate solidarity contributions
            print(f"    🧮 Calculating solidarity contributions...")
            solidarity_contributions = self.calculate_solidarity_contributions(player_name, birth_date, transfers)
            
            if solidarity_contributions:
                print(f"    ✅ Found {len(solidarity_contributions)} solidarity contributions")
                self.successful_requests += 1
                return solidarity_contributions
            else:
                print(f"    ❌ No solidarity contributions found")
                self.failed_requests += 1
                return []
                
        except Exception as e:
            print(f"    ❌ Error extracting solidarity data for {player_name}: {e}")
            self.failed_requests += 1
            return []
    
    def process_batch(self, players_batch, batch_number):
        """Process a batch of players"""
        print(f"\n🔄 Processing Batch {batch_number} ({len(players_batch)} players)")
        
        batch_results = []
        
        for i, player in players_batch.iterrows():
            try:
                print(f"\n🔍 Processing {i + 1}/{len(players_batch)}: {player['full_name']}")
                
                solidarity_data = self.extract_solidarity_data(player)
                
                if solidarity_data:
                    batch_results.extend(solidarity_data)
                    self.solidarity_data.extend(solidarity_data)
                    print(f"    ✅ Found {len(solidarity_data)} solidarity contributions")
                else:
                    print(f"    ❌ No solidarity data found")
                
                self.processed_count += 1
                
                # Very long delay between players
                if i < len(players_batch) - 1:  # Don't delay after last player
                    self.long_delay(60, 120)  # 1-2 minutes between players
                
            except Exception as e:
                print(f"❌ Error processing player: {e}")
                continue
        
        # Save batch results
        if batch_results:
            df_batch = pd.DataFrame(batch_results)
            df_batch.to_csv(f'batch_{batch_number}_transfers_results.csv', index=False)
            print(f"\n💾 Saved batch {batch_number} results: {len(batch_results)} records")
        
        return batch_results
    
    def test_with_single_player(self):
        """Test with a single player to verify the approach"""
        print("🧪 Testing Batch Transfers Scraper with Single Player...")
        
        # Setup browser
        if not self.setup_driver():
            print("❌ Failed to setup browser")
            return False
        
        try:
            # Load first player
            df = pd.read_csv('players_ALL_LEAGUES.csv')
            test_player = df.head(1)
            
            print(f"📋 Testing with: {test_player.iloc[0]['full_name']}")
            
            batch_results = self.process_batch(test_player, 1)
            
            # Summary
            print(f"\n📊 Test Results Summary:")
            print(f"  ✅ Successful requests: {self.successful_requests}")
            print(f"  ❌ Failed requests: {self.failed_requests}")
            print(f"  🚫 Blocked requests: {self.blocked_requests}")
            print(f"  📝 Total solidarity records: {len(self.solidarity_data)}")
            
            if self.successful_requests >= 1:
                print(f"\n🎉 TEST SUCCESSFUL! Batch approach works!")
                return True
            else:
                print(f"\n⚠️  TEST FAILED. Need different approach.")
                return False
                
        finally:
            self.close_driver()

def main():
    """Main function"""
    scraper = BatchTransfersScraper()
    
    try:
        success = scraper.test_with_single_player()
        if success:
            print("\n🚀 Ready to launch batch transfers scraper!")
        else:
            print("\n⚠️  Need to try different approach.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔚 Test completed")

if __name__ == "__main__":
    main()
