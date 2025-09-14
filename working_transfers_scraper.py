#!/usr/bin/env python3
"""
Working Transfers Scraper - Based on the successful transfers_solidarity_improved.py
Combines the working transfer extraction logic with better cookie handling
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

class WorkingTransfersScraper:
    def __init__(self):
        self.driver = None
        self.solidarity_data = []
        self.successful_requests = 0
        self.failed_requests = 0
        
    def setup_driver(self):
        """Setup Chrome driver with working configuration"""
        print("🛡️ Setting up working transfers browser...")
        
        try:
            # Kill any existing Chrome processes
            os.system('pkill -f chrome 2>/dev/null || true')
            time.sleep(3)
            
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            
            # Language preferences
            options.add_experimental_option('prefs', {
                'intl.accept_languages': 'en-US,en,es,de,fr',
                'profile.default_content_setting_values': {
                    'notifications': 2,
                    'media_stream': 2,
                    'geolocation': 2
                }
            })
            
            # Create driver
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Enhanced stealth measures
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            self.driver.set_page_load_timeout(45)
            self.driver.implicitly_wait(15)
            
            print("✅ Working transfers browser configured")
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
    
    def handle_cookie_consent_simple(self):
        """Simple cookie consent handling"""
        try:
            print("    🍪 Handling cookie consent...")
            time.sleep(3)
            
            # Try to find and click any accept button
            try:
                # Look for buttons with accept text
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    try:
                        button_text = button.text.lower()
                        if any(keyword in button_text for keyword in ['accept', 'continue', 'ok', 'agree', 'aceptar']):
                            if button.is_displayed():
                                self.driver.execute_script("arguments[0].click();", button)
                                print("    ✅ Cookie consent accepted")
                                time.sleep(2)
                                return True
                    except:
                        continue
            except:
                pass
            
            # Try XPath for accept buttons
            try:
                xpath = "//button[contains(text(), 'Accept') or contains(text(), 'Accept & continue') or contains(text(), 'Aceptar')]"
                buttons = self.driver.find_elements(By.XPATH, xpath)
                for button in buttons:
                    try:
                        if button.is_displayed():
                            self.driver.execute_script("arguments[0].click();", button)
                            print("    ✅ Cookie consent accepted via XPath")
                            time.sleep(2)
                            return True
                    except:
                        continue
            except:
                pass
            
            print("    ⚠️  Could not find cookie consent button - continuing anyway")
            return False
            
        except Exception as e:
            print(f"    ⚠️  Error handling cookie consent: {e}")
            return False
    
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
        """Extract player birth date from profile page - WORKING VERSION"""
        try:
            print(f"    🌐 Loading profile page...")
            self.driver.get(profile_url)
            time.sleep(5)
            
            # Handle cookie consent
            self.handle_cookie_consent_simple()
            
            # Get page source and search for birth date patterns
            page_source = self.driver.page_source
            
            # Look for birth date patterns in the page source - SAME AS WORKING VERSION
            birth_patterns = [
                r'Date of birth/Age:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                r'Birth date:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                r'Born:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                r'(\d{1,2}[/.]\d{1,2}[/.]\d{4})\s*\([0-9]+\)',  # Date (Age)
                r'Geburtsdatum:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',  # German
                r'Fecha de nacimiento:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})'  # Spanish
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
        """Extract transfer history from transfers URL - WORKING VERSION"""
        try:
            # Construct transfers URL
            transfers_url = f"https://www.transfermarkt.com/{player_name.lower().replace(' ', '-')}/transfers/spieler/{player_id}"
            print(f"    🌐 Loading transfers page: {transfers_url}")
            
            self.driver.get(transfers_url)
            time.sleep(8)  # Longer wait for page to load
            
            # Handle cookie consent
            self.handle_cookie_consent_simple()
            
            # Get page source and parse transfers
            page_source = self.driver.page_source
            
            # Check if page loaded properly
            if len(page_source) < 50000:
                print(f"    ⚠️  Page too small: {len(page_source)} chars")
                return []
            
            print(f"    ✅ Page loaded successfully: {len(page_source)} chars")
            
            # Look for transfer table data in HTML - SAME LOGIC AS WORKING VERSION
            transfers = []
            
            # Try to find transfer rows using regex patterns - WORKING VERSION
            lines = page_source.split('\n')
            current_transfer = {}
            
            for line in lines:
                line = line.strip()
                
                # Look for date patterns
                date_match = re.search(r'(\d{2}[/.]\d{2}[/.]\d{4})', line)
                if date_match:
                    current_transfer['date'] = date_match.group(1)
                
                # Look for club names (simplified approach)
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
            
            # Fallback: try to find any table with transfer-like data - WORKING VERSION
            if not transfers:
                print(f"    🔍 Trying fallback method to extract transfers...")
                
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
                if transfer.get('date') and len(transfer['date']) > 5:  # Valid date
                    valid_transfers.append(transfer)
            
            print(f"    ✅ Extracted {len(valid_transfers)} transfers")
            return valid_transfers
            
        except Exception as e:
            print(f"    ❌ Error extracting transfer history: {e}")
            return []
    
    def calculate_age_at_transfer(self, birth_date_str, transfer_date_str):
        """Calculate player age at the time of transfer - WORKING VERSION"""
        try:
            # Parse birth date - handle different formats
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
        """Calculate solidarity contribution amount (5% of transfer fee) - WORKING VERSION"""
        try:
            # Clean transfer fee string
            fee_str = transfer_fee.lower().replace('€', '').replace(',', '').strip()
            
            # Handle different fee formats
            if 'free transfer' in fee_str or fee_str == '-' or fee_str == '' or 'loan' in fee_str:
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
    
    def calculate_solidarity_contributions(self, player_name, birth_date, transfers):
        """Calculate solidarity contributions based on transfer history - WORKING VERSION"""
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
                        club = transfer.get('left_club', '') or transfer.get('joined_club', '')
                        
                        if club and club.lower() not in ['without club', 'free agent', '-', '']:
                            # Calculate solidarity contribution (5% of transfer fee)
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
                    print(f"    ⚠️  Error processing transfer: {e}")
                    continue
            
            return solidarity_contributions
            
        except Exception as e:
            print(f"    ❌ Error calculating solidarity contributions: {e}")
            return []
    
    def extract_solidarity_data(self, player):
        """Extract solidarity contribution data for a player - WORKING VERSION"""
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
    
    def test_with_first_players(self, num_players=2):
        """Test with first N players"""
        print("🧪 Testing Working Transfers Scraper...")
        print(f"📊 Testing with first {num_players} players")
        
        # Setup browser
        if not self.setup_driver():
            print("❌ Failed to setup browser")
            return False
        
        try:
            # Load first N players
            df = pd.read_csv('players_ALL_LEAGUES.csv')
            test_players = df.head(num_players)
            
            print(f"📋 Processing {len(test_players)} test players...")
            
            for i, player in test_players.iterrows():
                try:
                    print(f"\n🔍 Processing {i + 1}/{num_players}: {player['full_name']}")
                    
                    solidarity_data = self.extract_solidarity_data(player)
                    
                    if solidarity_data:
                        self.solidarity_data.extend(solidarity_data)
                        print(f"    ✅ Found {len(solidarity_data)} solidarity contributions")
                    else:
                        print(f"    ❌ No solidarity data found")
                    
                    # Delay between requests
                    time.sleep(random.uniform(10, 15))
                    
                except Exception as e:
                    print(f"❌ Error processing player: {e}")
                    continue
            
            # Save test results
            if self.solidarity_data:
                df_results = pd.DataFrame(self.solidarity_data)
                df_results.to_csv('working_transfers_results.csv', index=False)
                print(f"\n💾 Saved test results: working_transfers_results.csv")
                
                # Show sample results
                print(f"\n📊 Sample Results:")
                print(df_results[['player_name', 'club', 'player_age_at_transfer', 'solidarity_contribution']].head().to_string(index=False))
            
            # Summary
            print(f"\n📊 Test Results Summary:")
            print(f"  ✅ Successful requests: {self.successful_requests}")
            print(f"  ❌ Failed requests: {self.failed_requests}")
            print(f"  📝 Total solidarity records: {len(self.solidarity_data)}")
            
            if self.successful_requests >= 1:
                print(f"\n🎉 TEST SUCCESSFUL! Working transfers extraction confirmed!")
                return True
            else:
                print(f"\n⚠️  TEST NEEDS IMPROVEMENT. Low success rate.")
                return False
                
        finally:
            self.close_driver()

def main():
    """Main function"""
    scraper = WorkingTransfersScraper()
    
    try:
        success = scraper.test_with_first_players(2)
        if success:
            print("\n🚀 Ready to launch working transfers scraper for all players!")
        else:
            print("\n⚠️  Need to improve working approach.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔚 Test completed")

if __name__ == "__main__":
    main()
