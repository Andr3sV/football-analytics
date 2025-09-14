#!/usr/bin/env python3
"""
Transfers-Based Solidarity Contribution Scraper
Extracts transfer history and calculates solidarity contributions based on player age
"""
import pandas as pd
import time
import json
import glob
import os
import re
import random
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class TransfersSolidarityScraper:
    def __init__(self):
        self.driver = None
        self.processed_players = set()
        self.solidarity_data = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
    def setup_driver(self):
        """Setup Chrome driver with stealth configuration"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Anti-detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        chrome_options.add_argument(f'--user-agent={user_agent}')
        
        # Disable automation indicators
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Disable notifications
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "media_stream": 2,
                "geolocation": 2
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Hide automation
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.implicitly_wait(10)
        
    def close_driver(self):
        """Close the browser driver safely"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def get_new_players(self):
        """Get new players from main scraper progress files"""
        progress_files = glob.glob('players_FAST_EXACT_PROGRESS_*.csv')
        if not progress_files:
            return []
        
        latest_file = max(progress_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        
        new_players = []
        for _, player in df.iterrows():
            player_name = player.get('full_name', '')
            if player_name and player_name not in self.processed_players:
                new_players.append(player)
                self.processed_players.add(player_name)
        
        return new_players
    
    def extract_player_id_from_url(self, profile_url):
        """Extract player ID from Transfermarkt profile URL"""
        try:
            # Pattern: /spieler/123456
            match = re.search(r'/spieler/(\d+)', profile_url)
            if match:
                return match.group(1)
            return None
        except:
            return None
    
    def calculate_age_at_transfer(self, birth_date_str, transfer_date_str):
        """Calculate player age at the time of transfer"""
        try:
            # Parse birth date
            if '/' in birth_date_str:
                birth_date = datetime.strptime(birth_date_str, '%d/%m/%Y').date()
            else:
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            
            # Parse transfer date
            if '/' in transfer_date_str:
                transfer_date = datetime.strptime(transfer_date_str, '%d/%m/%Y').date()
            else:
                transfer_date = datetime.strptime(transfer_date_str, '%Y-%m-%d').date()
            
            # Calculate age
            age = transfer_date.year - birth_date.year
            if transfer_date.month < birth_date.month or (transfer_date.month == birth_date.month and transfer_date.day < birth_date.day):
                age -= 1
            
            return age
        except:
            return None
    
    def extract_transfer_history(self, player_name, profile_url):
        """Extract transfer history for a player"""
        try:
            # Extract player ID
            player_id = self.extract_player_id_from_url(profile_url)
            if not player_id:
                print(f"    ❌ Could not extract player ID from URL: {profile_url}")
                return []
            
            # Construct transfers URL
            transfers_url = f"https://www.transfermarkt.com/{player_name.lower().replace(' ', '-')}/transfers/spieler/{player_id}"
            print(f"    🌐 Navigating to transfers: {transfers_url}")
            
            self.driver.get(transfers_url)
            time.sleep(3)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 15)
            
            # Look for transfer history table
            try:
                # Try to find the transfer history table
                transfer_table = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'table.items'))
                )
                print(f"    ✅ Found transfer history table")
                
                # Extract transfer data
                transfers = []
                rows = transfer_table.find_elements(By.TAG_NAME, 'tr')[1:]  # Skip header
                
                for row in rows:
                    try:
                        cells = row.find_elements(By.TAG_NAME, 'td')
                        if len(cells) >= 6:  # Season, Date, Left, Joined, MV, Fee
                            season = cells[0].text.strip()
                            date_str = cells[1].text.strip()
                            left_club = cells[2].text.strip()
                            joined_club = cells[3].text.strip()
                            market_value = cells[4].text.strip()
                            transfer_fee = cells[5].text.strip()
                            
                            if date_str and date_str != '-':
                                transfers.append({
                                    'season': season,
                                    'date': date_str,
                                    'left_club': left_club,
                                    'joined_club': joined_club,
                                    'market_value': market_value,
                                    'transfer_fee': transfer_fee
                                })
                    except Exception as e:
                        print(f"    ⚠️  Error parsing transfer row: {e}")
                        continue
                
                print(f"    ✅ Extracted {len(transfers)} transfers")
                return transfers
                
            except TimeoutException:
                print(f"    ❌ No transfer history table found")
                return []
                
        except Exception as e:
            print(f"    ❌ Error extracting transfer history for {player_name}: {e}")
            return []
    
    def extract_birth_date(self, player_name, profile_url):
        """Extract player birth date from profile"""
        try:
            self.driver.get(profile_url)
            time.sleep(3)
            
            wait = WebDriverWait(self.driver, 10)
            
            # Look for birth date in player info
            try:
                # Try different selectors for birth date
                birth_selectors = [
                    'span[data-testid="birth-date"]',
                    '.info-table .info-table__content',
                    '.tm-player-transfer-history-grid .tm-player-transfer-history-grid__date',
                    '[class*="birth"]',
                    '[class*="date"]'
                ]
                
                for selector in birth_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            text = element.text.strip()
                            # Look for date patterns
                            if re.search(r'\d{1,2}[/.]\d{1,2}[/.]\d{4}', text):
                                return text
                    except:
                        continue
                
                # Fallback: look in page source for birth date patterns
                page_source = self.driver.page_source
                birth_patterns = [
                    r'Date of birth/Age:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                    r'Birth date:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                    r'Born:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                    r'(\d{1,2}[/.]\d{1,2}[/.]\d{4})\s*\([0-9]+\)'  # Date (Age)
                ]
                
                for pattern in birth_patterns:
                    match = re.search(pattern, page_source)
                    if match:
                        return match.group(1)
                
                print(f"    ⚠️  Could not find birth date for {player_name}")
                return None
                
            except Exception as e:
                print(f"    ⚠️  Error extracting birth date: {e}")
                return None
                
        except Exception as e:
            print(f"    ❌ Error extracting birth date for {player_name}: {e}")
            return None
    
    def calculate_solidarity_contributions(self, player_name, birth_date, transfers):
        """Calculate solidarity contributions based on transfer history"""
        try:
            if not birth_date or not transfers:
                return []
            
            solidarity_contributions = []
            
            for transfer in transfers:
                try:
                    # Calculate age at transfer
                    age = self.calculate_age_at_transfer(birth_date, transfer['date'])
                    
                    if age is None:
                        continue
                    
                    # Check if player was between 12-23 years old
                    if 12 <= age <= 23:
                        # This transfer is eligible for solidarity contribution
                        club = transfer['left_club'] if transfer['left_club'] != '-' else transfer['joined_club']
                        
                        if club and club != '-' and club.lower() not in ['without club', 'free agent']:
                            # Calculate solidarity contribution (5% of transfer fee)
                            transfer_fee = transfer['transfer_fee']
                            contribution = self.calculate_contribution_amount(transfer_fee)
                            
                            solidarity_contributions.append({
                                'player_name': player_name,
                                'club': club,
                                'transfer_date': transfer['date'],
                                'player_age_at_transfer': age,
                                'transfer_fee': transfer_fee,
                                'solidarity_contribution': contribution,
                                'season': transfer['season'],
                                'extracted_at': datetime.now().isoformat()
                            })
                            
                except Exception as e:
                    print(f"    ⚠️  Error processing transfer: {e}")
                    continue
            
            return solidarity_contributions
            
        except Exception as e:
            print(f"    ❌ Error calculating solidarity contributions: {e}")
            return []
    
    def calculate_contribution_amount(self, transfer_fee):
        """Calculate solidarity contribution amount (5% of transfer fee)"""
        try:
            # Clean transfer fee string
            fee_str = transfer_fee.lower().replace('€', '').replace(',', '').strip()
            
            # Handle different fee formats
            if 'free transfer' in fee_str or fee_str == '-' or fee_str == '':
                return '€0'
            
            # Extract numeric value
            if 'm' in fee_str:
                # Millions
                value = float(re.search(r'(\d+\.?\d*)', fee_str).group(1))
                contribution = value * 0.05  # 5%
                return f"€{contribution:.2f}m"
            elif 'k' in fee_str:
                # Thousands
                value = float(re.search(r'(\d+\.?\d*)', fee_str).group(1))
                contribution = value * 0.05  # 5%
                return f"€{contribution:.0f}k"
            else:
                # Try to extract number
                match = re.search(r'(\d+\.?\d*)', fee_str)
                if match:
                    value = float(match.group(1))
                    contribution = value * 0.05  # 5%
                    return f"€{contribution:.2f}"
            
            return '€0'
            
        except:
            return '€0'
    
    def extract_solidarity_data(self, player):
        """Extract solidarity contribution data for a player"""
        try:
            player_name = player.get('full_name', '')
            profile_url = player.get('profile_url', '')
            
            if not player_name or not profile_url:
                return []
            
            print(f"  🔍 Processing: {player_name}")
            
            # Extract birth date
            print(f"    📅 Extracting birth date...")
            birth_date = self.extract_birth_date(player_name, profile_url)
            if not birth_date:
                print(f"    ❌ No birth date found")
                return []
            
            print(f"    ✅ Birth date: {birth_date}")
            
            # Extract transfer history
            print(f"    📊 Extracting transfer history...")
            transfers = self.extract_transfer_history(player_name, profile_url)
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
    
    def save_solidarity_data(self, data):
        """Save solidarity data to CSV"""
        if data:
            df = pd.DataFrame(data)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'transfers_solidarity_data_{timestamp}.csv'
            
            # Append to existing data if file exists
            if os.path.exists('transfers_solidarity_contributions.csv'):
                df.to_csv('transfers_solidarity_contributions.csv', mode='a', header=False, index=False)
            else:
                df.to_csv('transfers_solidarity_contributions.csv', index=False)
            
            print(f"    💾 Saved {len(data)} solidarity records")
    
    def process_players(self, max_players=None):
        """Process players for solidarity data extraction"""
        print("🔍 Starting Transfers-Based Solidarity Contribution Scraper...")
        print("📊 Extracting transfer history and calculating solidarity contributions...")
        
        processed_count = 0
        
        while True:
            try:
                new_players = self.get_new_players()
                
                if new_players:
                    print(f"\n🆕 Found {len(new_players)} new players to process")
                    
                    for player in new_players:
                        solidarity_data = self.extract_solidarity_data(player)
                        if solidarity_data:
                            self.solidarity_data.extend(solidarity_data)
                            self.save_solidarity_data(solidarity_data)
                            print(f"    ✅ Found {len(solidarity_data)} solidarity contributions")
                        else:
                            print(f"    ❌ No solidarity data found")
                        
                        processed_count += 1
                        
                        # Check if we've reached the limit
                        if max_players and processed_count >= max_players:
                            print(f"🎯 Reached limit of {max_players} players")
                            return
                        
                        # Delay between requests
                        time.sleep(3)
                
                else:
                    print(".", end="", flush=True)
                    time.sleep(30)
                    
            except KeyboardInterrupt:
                print("\n⏹️  Stopping transfers solidarity scraper...")
                break
            except Exception as e:
                print(f"\n❌ Error in main loop: {e}")
                time.sleep(60)
        
        # Final summary
        print(f"\n📊 Transfers Solidarity Scraper Summary:")
        print(f"  ✅ Successful requests: {self.successful_requests}")
        print(f"  ❌ Failed requests: {self.failed_requests}")
        print(f"  📝 Total solidarity records: {len(self.solidarity_data)}")
    
    def get_stats(self):
        """Get processing statistics"""
        return {
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'total_players_processed': len(self.processed_players),
            'total_solidarity_records': len(self.solidarity_data)
        }

def main():
    """Main function"""
    scraper = TransfersSolidarityScraper()
    
    try:
        # Setup browser
        print("🌐 Setting up transfers browser...")
        scraper.setup_driver()
        
        # Process players (limit to 2 for testing)
        scraper.process_players(max_players=2)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close_driver()
        print("🔚 Transfers solidarity scraper finished")

if __name__ == "__main__":
    main()
