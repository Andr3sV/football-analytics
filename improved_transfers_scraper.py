#!/usr/bin/env python3
"""
Improved Transfers Scraper - Enhanced table extraction with better cookie handling
Based on best practices from existing Transfermarkt scrapers
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
from selenium.webdriver.common.action_chains import ActionChains

class ImprovedTransfersScraper:
    def __init__(self):
        self.driver = None
        self.solidarity_data = []
        self.successful_requests = 0
        self.failed_requests = 0
        
    def setup_driver(self):
        """Setup Chrome driver with enhanced configuration"""
        print("🛡️ Setting up improved transfers browser...")
        
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
            
            print("✅ Improved transfers browser configured")
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
    
    def handle_cookie_consent_enhanced(self):
        """Enhanced cookie consent handling with multiple strategies"""
        try:
            print("    🍪 Handling cookie consent popup...")
            
            # Wait for page to fully load
            time.sleep(3)
            
            wait = WebDriverWait(self.driver, 15)
            
            # Strategy 1: Look for specific Transfermarkt cookie consent buttons
            consent_selectors = [
                "button:contains('Accept')",
                "button:contains('Accept & continue')",
                "button[class*='accept']",
                ".accept-all",
                "#accept-all",
                "[data-testid='accept-all']",
                "button[class*='cookie']",
                "button[class*='consent']"
            ]
            
            for selector in consent_selectors:
                try:
                    if ":contains" in selector:
                        # Use XPath for text-based selectors
                        xpath = f"//button[contains(text(), 'Accept') or contains(text(), 'Accept & continue')]"
                        buttons = self.driver.find_elements(By.XPATH, xpath)
                        
                        for button in buttons:
                            try:
                                if button.is_displayed() and button.is_enabled():
                                    # Scroll to button if needed
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                    time.sleep(1)
                                    
                                    # Try different click methods
                                    try:
                                        button.click()
                                    except:
                                        self.driver.execute_script("arguments[0].click();", button)
                                    
                                    print("    ✅ Cookie consent accepted via XPath")
                                    time.sleep(3)
                                    return True
                            except:
                                continue
                    else:
                        try:
                            button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                            if button.is_displayed():
                                self.driver.execute_script("arguments[0].click();", button)
                                print(f"    ✅ Cookie consent accepted via {selector}")
                                time.sleep(3)
                                return True
                        except:
                            continue
                            
                except Exception as e:
                    continue
            
            # Strategy 2: Look for any button in the visible area
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    try:
                        button_text = button.text.lower()
                        if any(keyword in button_text for keyword in ['accept', 'continue', 'ok', 'agree']):
                            if button.is_displayed() and button.is_enabled():
                                self.driver.execute_script("arguments[0].click();", button)
                                print("    ✅ Cookie consent accepted via button text")
                                time.sleep(3)
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
            time.sleep(5)
            
            # Handle cookie consent
            self.handle_cookie_consent_enhanced()
            
            # Wait for page to load completely
            time.sleep(3)
            
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
    
    def extract_transfer_history_enhanced(self, player_name, player_id):
        """Enhanced transfer history extraction with multiple strategies"""
        try:
            transfers_url = f"https://www.transfermarkt.com/{player_name.lower().replace(' ', '-')}/transfers/spieler/{player_id}"
            print(f"    📊 Loading transfers: {transfers_url}")
            
            self.driver.get(transfers_url)
            time.sleep(6)
            
            # Handle cookie consent
            self.handle_cookie_consent_enhanced()
            
            # Wait for page to load completely
            time.sleep(4)
            
            page_source = self.driver.page_source
            
            # Check if page loaded properly
            if len(page_source) < 100000:
                print(f"    ⚠️  Page still small after cookie handling: {len(page_source)} chars")
                return []
            
            print(f"    ✅ Page loaded successfully: {len(page_source)} chars")
            
            soup = BeautifulSoup(page_source, 'html.parser')
            transfers = []
            
            # Strategy 1: Look for standard transfer table with class 'items'
            transfer_table = soup.find('table', class_='items')
            if transfer_table:
                print(f"    ✅ Found standard transfer table")
                transfers = self.extract_transfers_from_table(transfer_table)
            
            # Strategy 2: Look for any table with transfer-like data
            if not transfers:
                print(f"    🔍 Looking for alternative tables...")
                tables = soup.find_all('table')
                
                for table in tables:
                    if self.looks_like_transfer_table(table):
                        print(f"    ✅ Found alternative transfer table")
                        transfers = self.extract_transfers_from_table(table)
                        if transfers:
                            break
            
            # Strategy 3: Look for transfer data in divs or other elements
            if not transfers:
                print(f"    🔍 Looking for transfer data in divs...")
                transfers = self.extract_transfers_from_divs(soup)
            
            # Filter and validate transfers
            valid_transfers = []
            for transfer in transfers:
                if self.is_valid_transfer(transfer):
                    valid_transfers.append(transfer)
            
            print(f"    ✅ Extracted {len(valid_transfers)} valid transfers")
            return valid_transfers
            
        except Exception as e:
            print(f"    ❌ Error extracting transfer history: {e}")
            return []
    
    def looks_like_transfer_table(self, table):
        """Check if a table looks like it contains transfer data"""
        try:
            # Look for typical transfer table headers
            headers = table.find_all('th')
            header_texts = [th.get_text(strip=True).lower() for th in headers]
            
            transfer_keywords = ['season', 'date', 'left', 'joined', 'mv', 'fee', 'market value']
            matches = sum(1 for keyword in transfer_keywords for header in header_texts if keyword in header)
            
            return matches >= 3
        except:
            return False
    
    def extract_transfers_from_table(self, table):
        """Extract transfers from a table element"""
        transfers = []
        try:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                try:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        # Extract data from cells
                        transfer_data = {
                            'season': cells[0].get_text(strip=True) if len(cells) > 0 else '',
                            'date': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                            'left_club': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                            'joined_club': cells[3].get_text(strip=True) if len(cells) > 3 else '',
                            'market_value': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                            'transfer_fee': cells[5].get_text(strip=True) if len(cells) > 5 else ''
                        }
                        transfers.append(transfer_data)
                except Exception as e:
                    continue
            
            return transfers
            
        except Exception as e:
            print(f"    ⚠️  Error extracting from table: {e}")
            return []
    
    def extract_transfers_from_divs(self, soup):
        """Extract transfer data from div elements as fallback"""
        transfers = []
        try:
            # Look for transfer-like data in page source
            page_text = soup.get_text()
            
            # Find date patterns and extract surrounding context
            date_pattern = r'(\d{2}[/.]\d{2}[/.]\d{4})'
            dates = re.findall(date_pattern, page_text)
            
            for date in dates:
                # Look for context around the date
                date_index = page_text.find(date)
                context_start = max(0, date_index - 200)
                context_end = min(len(page_text), date_index + 200)
                context = page_text[context_start:context_end]
                
                # Try to extract club names and fees from context
                club_patterns = [
                    r'([A-Z][a-zA-Z\s]+)\s*→\s*([A-Z][a-zA-Z\s]+)',
                    r'([A-Z][a-zA-Z\s]+)\s*to\s*([A-Z][a-zA-Z\s]+)',
                    r'([A-Z][a-zA-Z\s]+)\s*-[>\s]*([A-Z][a-zA-Z\s]+)'
                ]
                
                for pattern in club_patterns:
                    match = re.search(pattern, context)
                    if match:
                        transfer_data = {
                            'season': '',
                            'date': date,
                            'left_club': match.group(1).strip(),
                            'joined_club': match.group(2).strip(),
                            'market_value': '',
                            'transfer_fee': ''
                        }
                        transfers.append(transfer_data)
                        break
            
            return transfers
            
        except Exception as e:
            print(f"    ⚠️  Error extracting from divs: {e}")
            return []
    
    def is_valid_transfer(self, transfer):
        """Validate if a transfer record is valid"""
        try:
            # Check if date is valid
            date_str = transfer.get('date', '')
            if not date_str or len(date_str) < 8:
                return False
            
            # Check if date matches expected format
            if not re.search(r'\d{2}[/.]\d{2}[/.]\d{4}', date_str):
                return False
            
            # Check if at least one club is present
            left_club = transfer.get('left_club', '').strip()
            joined_club = transfer.get('joined_club', '').strip()
            
            if not left_club and not joined_club:
                return False
            
            return True
            
        except:
            return False
    
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
            transfers = self.extract_transfer_history_enhanced(player_name, player_id)
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
        print("🧪 Testing Improved Transfers Scraper...")
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
                df_results.to_csv('improved_transfers_results.csv', index=False)
                print(f"\n💾 Saved test results: improved_transfers_results.csv")
                
                # Show sample results
                print(f"\n📊 Sample Results:")
                print(df_results[['player_name', 'club', 'player_age_at_transfer', 'solidarity_contribution']].head().to_string(index=False))
            
            # Summary
            print(f"\n📊 Test Results Summary:")
            print(f"  ✅ Successful requests: {self.successful_requests}")
            print(f"  ❌ Failed requests: {self.failed_requests}")
            print(f"  📝 Total solidarity records: {len(self.solidarity_data)}")
            
            if self.successful_requests >= 1:
                print(f"\n🎉 TEST SUCCESSFUL! Enhanced table extraction works!")
                return True
            else:
                print(f"\n⚠️  TEST NEEDS IMPROVEMENT. Low success rate.")
                return False
                
        finally:
            self.close_driver()

def main():
    """Main function"""
    scraper = ImprovedTransfersScraper()
    
    try:
        success = scraper.test_with_first_players(2)
        if success:
            print("\n🚀 Ready to launch improved transfers scraper for all players!")
        else:
            print("\n⚠️  Need to improve table extraction.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔚 Test completed")

if __name__ == "__main__":
    main()
