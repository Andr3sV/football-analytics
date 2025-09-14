#!/usr/bin/env python3
"""
Cookie Handler Scraper - Handles Transfermarkt cookie consent popups
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

class CookieHandlerScraper:
    def __init__(self):
        self.driver = None
        self.solidarity_data = []
        self.successful_requests = 0
        self.failed_requests = 0
        
    def setup_driver(self):
        """Setup Chrome driver with cookie handling"""
        print("🛡️ Setting up cookie handler browser...")
        
        try:
            # Kill any existing Chrome processes
            os.system('pkill -f chrome 2>/dev/null || true')
            time.sleep(2)
            
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # Create driver
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Simple stealth measures
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            print("✅ Cookie handler browser configured")
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
    
    def handle_cookie_consent(self):
        """Handle cookie consent popup"""
        try:
            print("    🍪 Handling cookie consent popup...")
            
            # Wait for cookie popup to appear
            wait = WebDriverWait(self.driver, 10)
            
            # Try different selectors for the accept button
            accept_selectors = [
                "button[class*='accept']",
                "button:contains('Accept')",
                "button:contains('Accept & continue')",
                "[class*='accept']",
                ".accept-all",
                "#accept-all",
                "button[data-testid='accept-all']"
            ]
            
            for selector in accept_selectors:
                try:
                    if ":contains" in selector:
                        # Use XPath for text-based selectors
                        xpath = f"//button[contains(text(), 'Accept')]"
                        accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    else:
                        accept_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    accept_button.click()
                    print("    ✅ Cookie consent accepted")
                    time.sleep(2)
                    return True
                    
                except:
                    continue
            
            # If no accept button found, try to find any button in the popup
            try:
                popup_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
                for button in popup_buttons:
                    button_text = button.text.lower()
                    if 'accept' in button_text or 'continue' in button_text:
                        button.click()
                        print("    ✅ Cookie consent accepted (fallback)")
                        time.sleep(2)
                        return True
            except:
                pass
            
            print("    ⚠️  Could not find cookie consent button")
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
    
    def calculate_age_at_transfer(self, birth_date_str, transfer_date_str):
        """Calculate player age at the time of transfer"""
        try:
            # Parse birth date
            birth_date = None
            for fmt in ['%d/%m/%Y', '%d.%m.%Y', '%Y-%m-%d']:
                try:
                    birth_date = datetime.strptime(birth_date_str, fmt).date()
                    break
                except:
                    continue
            
            if not birth_date:
                return None
            
            # Parse transfer date
            transfer_date = None
            for fmt in ['%d/%m/%Y', '%d.%m.%Y', '%Y-%m-%d']:
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
    
    def extract_birth_date_from_profile(self, player_name, profile_url):
        """Extract player birth date from profile page"""
        try:
            print(f"    📅 Extracting birth date...")
            self.driver.get(profile_url)
            time.sleep(4)
            
            # Handle cookie consent
            self.handle_cookie_consent()
            
            page_source = self.driver.page_source
            
            # Look for birth date patterns
            birth_patterns = [
                r'Date of birth/Age:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                r'Birth date:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                r'Born:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
                r'(\d{1,2}[/.]\d{1,2}[/.]\d{4})\s*\([0-9]+\)'
            ]
            
            for pattern in birth_patterns:
                match = re.search(pattern, page_source, re.IGNORECASE)
                if match:
                    birth_date = match.group(1)
                    print(f"    ✅ Found birth date: {birth_date}")
                    return birth_date
            
            print(f"    ❌ No birth date found")
            return None
            
        except Exception as e:
            print(f"    ❌ Error extracting birth date: {e}")
            return None
    
    def extract_transfer_history_with_cookies(self, player_name, player_id):
        """Extract transfer history handling cookie consent"""
        try:
            transfers_url = f"https://www.transfermarkt.com/{player_name.lower().replace(' ', '-')}/transfers/spieler/{player_id}"
            print(f"    📊 Loading transfers: {transfers_url}")
            
            self.driver.get(transfers_url)
            time.sleep(5)
            
            # Handle cookie consent
            self.handle_cookie_consent()
            
            page_source = self.driver.page_source
            
            # Check if page loaded properly (should be much larger now)
            if len(page_source) < 100000:
                print(f"    ⚠️  Page still small after cookie handling: {len(page_source)} chars")
                return []
            
            print(f"    ✅ Page loaded successfully: {len(page_source)} chars")
            
            soup = BeautifulSoup(page_source, 'html.parser')
            transfers = []
            
            # Look for transfer table
            transfer_table = soup.find('table', class_='items')
            if transfer_table:
                print(f"    ✅ Found transfer table")
                rows = transfer_table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 6:
                            season = cells[0].get_text(strip=True)
                            date_str = cells[1].get_text(strip=True)
                            left_club = cells[2].get_text(strip=True)
                            joined_club = cells[3].get_text(strip=True)
                            market_value = cells[4].get_text(strip=True)
                            transfer_fee = cells[5].get_text(strip=True)
                            
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
                        continue
            
            # Filter valid transfers
            valid_transfers = []
            for transfer in transfers:
                if transfer.get('date') and len(transfer['date']) > 5 and re.search(r'\d{2}[/.]\d{2}[/.]\d{4}', transfer['date']):
                    valid_transfers.append(transfer)
            
            print(f"    ✅ Extracted {len(valid_transfers)} transfers")
            return valid_transfers
            
        except Exception as e:
            print(f"    ❌ Error extracting transfer history: {e}")
            return []
    
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
                        
                        if club and club != '-' and club.lower() not in ['without club', 'free agent', '']:
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
            birth_date = self.extract_birth_date_from_profile(player_name, profile_url)
            if not birth_date:
                print(f"    ❌ No birth date found")
                return []
            
            # Extract transfer history
            transfers = self.extract_transfer_history_with_cookies(player_name, player_id)
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
        print("🧪 Testing Cookie Handler Scraper...")
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
                    time.sleep(random.uniform(8, 12))
                    
                except Exception as e:
                    print(f"❌ Error processing player: {e}")
                    continue
            
            # Save test results
            if self.solidarity_data:
                df_results = pd.DataFrame(self.solidarity_data)
                df_results.to_csv('cookie_handler_results.csv', index=False)
                print(f"\n💾 Saved test results: cookie_handler_results.csv")
                
                # Show sample results
                print(f"\n📊 Sample Results:")
                print(df_results[['player_name', 'club', 'player_age_at_transfer', 'solidarity_contribution']].head().to_string(index=False))
            
            # Summary
            print(f"\n📊 Test Results Summary:")
            print(f"  ✅ Successful requests: {self.successful_requests}")
            print(f"  ❌ Failed requests: {self.failed_requests}")
            print(f"  📝 Total solidarity records: {len(self.solidarity_data)}")
            
            if self.successful_requests >= 1:
                print(f"\n🎉 TEST SUCCESSFUL! Cookie handling works!")
                return True
            else:
                print(f"\n⚠️  TEST NEEDS IMPROVEMENT. Low success rate.")
                return False
                
        finally:
            self.close_driver()

def main():
    """Main function"""
    scraper = CookieHandlerScraper()
    
    try:
        success = scraper.test_with_first_players(2)
        if success:
            print("\n🚀 Ready to launch cookie handler scraper for all players!")
        else:
            print("\n⚠️  Need to improve cookie handling.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔚 Test completed")

if __name__ == "__main__":
    main()
