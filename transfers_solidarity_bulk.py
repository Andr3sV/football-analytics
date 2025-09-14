#!/usr/bin/env python3
"""
Bulk Transfers Solidarity Scraper
Extracts transfer history for all 9,962 players and calculates solidarity contributions
"""
import pandas as pd
import time
import json
import glob
import os
import re
import random
from datetime import datetime, date
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

class BulkTransfersSolidarityScraper:
    def __init__(self):
        self.driver = None
        self.processed_players = set()
        self.solidarity_data = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.save_interval = 50  # Save every 50 players
        self.request_count = 0
        self.session_start_time = datetime.now()
        
    def setup_undetected_driver(self):
        """Setup undetected Chrome driver for transfers pages"""
        print("🛡️ Setting up bulk transfers browser...")
        
        try:
            options = uc.ChromeOptions()
            
            # Essential options for speed and stealth
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Faster loading
            options.add_argument('--disable-javascript')  # Reduce fingerprinting
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
            
            print("✅ Bulk transfers browser configured")
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
        base_delay = random.uniform(4, 8)  # Base delay 4-8 seconds
        
        # Increase delay if we've made many requests
        if self.request_count > 0:
            time_since_start = (datetime.now() - self.session_start_time).total_seconds()
            requests_per_minute = self.request_count / (time_since_start / 60)
            
            if requests_per_minute > 10:  # If more than 10 requests per minute
                base_delay *= random.uniform(2, 4)
                print(f"    🐌 Slowing down due to high request rate: {base_delay:.1f}s")
        
        # Add random micro-delays
        micro_delays = [0.2, 0.5, 0.8, 1.2, 1.8]
        base_delay += random.choice(micro_delays)
        
        # Occasionally add longer delays
        if random.random() < 0.08:  # 8% chance
            base_delay += random.uniform(8, 15)
            print(f"    ☕ Taking a longer break: {base_delay:.1f}s")
        
        time.sleep(base_delay)
    
    def simulate_human_behavior(self):
        """Simulate human browsing behavior"""
        if random.random() < 0.05:  # 5% chance
            try:
                random_pages = [
                    'https://www.transfermarkt.com/',
                    'https://www.transfermarkt.com/wettbewerbe/europa',
                    'https://www.transfermarkt.com/transfers/transferrekorde/statistik'
                ]
                
                random_page = random.choice(random_pages)
                print(f"    🎭 Simulating human behavior: visiting {random_page}")
                
                self.driver.get(random_page)
                time.sleep(random.uniform(2, 5))
                
                print(f"    ✅ Human behavior simulation completed")
                
            except Exception as e:
                print(f"    ⚠️  Human behavior simulation failed: {e}")
    
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
    
    def extract_birth_date_from_profile(self, player_name, profile_url):
        """Extract player birth date from profile page"""
        try:
            print(f"    📅 Extracting birth date...")
            self.driver.get(profile_url)
            time.sleep(random.uniform(2, 4))
            
            # Get page source and search for birth date patterns
            page_source = self.driver.page_source
            
            # Look for birth date patterns in the page source
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
            
            print(f"    ❌ No birth date found")
            return None
            
        except Exception as e:
            print(f"    ❌ Error extracting birth date: {e}")
            return None
    
    def extract_transfer_history_from_url(self, player_name, player_id):
        """Extract transfer history from transfers URL"""
        try:
            # Construct transfers URL
            transfers_url = f"https://www.transfermarkt.com/{player_name.lower().replace(' ', '-')}/transfers/spieler/{player_id}"
            print(f"    📊 Loading transfers: {transfers_url}")
            
            self.driver.get(transfers_url)
            time.sleep(random.uniform(3, 5))
            
            # Get page source
            page_source = self.driver.page_source
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for transfer table
            transfers = []
            
            # Try to find transfer table
            transfer_table = soup.find('table', class_='items')
            if not transfer_table:
                # Try alternative selectors
                transfer_table = soup.find('table', {'data-testid': 'transfer-history'})
            
            if transfer_table:
                print(f"    ✅ Found transfer table")
                
                # Extract transfer data
                rows = transfer_table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 6:  # Season, Date, Left, Joined, MV, Fee
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
                        print(f"    ⚠️  Error parsing transfer row: {e}")
                        continue
            
            else:
                print(f"    🔍 Trying fallback method...")
                
                # Fallback: look for any table with transfer-like data
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) > 1:  # Has header and data
                        for row in rows[1:]:  # Skip header
                            cells = row.find_all('td')
                            if len(cells) >= 4:
                                # Clean up cell content
                                clean_cells = []
                                for cell in cells:
                                    clean_cell = cell.get_text(strip=True)
                                    clean_cells.append(clean_cell)
                                
                                if len(clean_cells) >= 4:
                                    # Look for date patterns
                                    if re.search(r'\d{2}[/.]\d{2}[/.]\d{4}', clean_cells[1]):
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
                if transfer.get('date') and len(transfer['date']) > 5 and re.search(r'\d{2}[/.]\d{2}[/.]\d{4}', transfer['date']):
                    valid_transfers.append(transfer)
            
            print(f"    ✅ Extracted {len(valid_transfers)} transfers")
            return valid_transfers
            
        except Exception as e:
            print(f"    ❌ Error extracting transfer history: {e}")
            return []
    
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
                        club = transfer.get('left_club', '') or transfer.get('joined_club', '')
                        
                        if club and club != '-' and club.lower() not in ['without club', 'free agent', '']:
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
    
    def calculate_contribution_amount(self, transfer_fee):
        """Calculate solidarity contribution amount (5% of transfer fee)"""
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
    
    def save_solidarity_data(self, data):
        """Save solidarity data to CSV"""
        if data:
            df = pd.DataFrame(data)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'bulk_transfers_solidarity_{timestamp}.csv'
            
            # Append to existing data if file exists
            if os.path.exists('bulk_transfers_solidarity_contributions.csv'):
                df.to_csv('bulk_transfers_solidarity_contributions.csv', mode='a', header=False, index=False)
            else:
                df.to_csv('bulk_transfers_solidarity_contributions.csv', index=False)
            
            print(f"    💾 Saved {len(data)} solidarity records")
    
    def process_all_players(self):
        """Process all 9,962 players for solidarity data extraction"""
        print("🔍 Starting Bulk Transfers Solidarity Scraper...")
        print("📊 Processing all 9,962 players for transfer history and solidarity contributions...")
        
        # Setup browser
        if not self.setup_undetected_driver():
            print("❌ Failed to setup browser")
            return
        
        try:
            # Load all players from main CSV
            try:
                all_players_df = pd.read_csv('players_ALL_LEAGUES.csv')
                total_players = len(all_players_df)
                print(f"📊 Total players to process: {total_players}")
                
            except Exception as e:
                print(f"❌ Error loading players: {e}")
                return
            
            # Process all players
            players_list = all_players_df.to_dict('records')
            
            print(f"📋 Processing {len(players_list)} players for solidarity contributions...")
            
            for i, player in enumerate(players_list):
                try:
                    player_name = player.get('full_name', '')
                    
                    if not player_name or player_name in self.processed_players:
                        continue
                    
                    print(f"\n🔍 Processing {i + 1}/{total_players}: {player_name}")
                    
                    # Extract solidarity data
                    solidarity_data = self.extract_solidarity_data(player)
                    
                    if solidarity_data:
                        self.solidarity_data.extend(solidarity_data)
                        self.save_solidarity_data(solidarity_data)
                        print(f"    ✅ Found {len(solidarity_data)} solidarity contributions")
                    else:
                        print(f"    ❌ No solidarity data found")
                    
                    self.processed_players.add(player_name)
                    
                    # Save progress periodically
                    if (i + 1) % self.save_interval == 0:
                        print(f"💾 Progress checkpoint: {i + 1}/{total_players} players processed")
                    
                    # Intelligent delay between requests
                    self.intelligent_delay()
                    
                except KeyboardInterrupt:
                    print("\n⏹️  Stopping bulk transfers scraper...")
                    break
                except Exception as e:
                    print(f"❌ Error processing player: {e}")
                    self.failed_requests += 1
                    continue
            
            # Final summary
            print(f"\n📊 Bulk Transfers Solidarity Scraper Summary:")
            print(f"  ✅ Successful requests: {self.successful_requests}")
            print(f"  ❌ Failed requests: {self.failed_requests}")
            print(f"  📝 Total solidarity records: {len(self.solidarity_data)}")
            print(f"  🕐 Total session time: {datetime.now() - self.session_start_time}")
            
        finally:
            self.close_driver()

def main():
    """Main function"""
    scraper = BulkTransfersSolidarityScraper()
    
    try:
        scraper.process_all_players()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔚 Bulk transfers solidarity scraper finished")

if __name__ == "__main__":
    main()
