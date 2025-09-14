#!/usr/bin/env python3
"""
Hybrid Transfers Scraper - Combines API calls with direct scraping
Uses transfermarkt-api.fly.dev when available, falls back to direct scraping
"""
import pandas as pd
import requests
import time
import json
import os
import re
import random
from datetime import datetime, date
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

class HybridTransfersScraper:
    def __init__(self):
        self.driver = None
        self.solidarity_data = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.api_base_url = "https://transfermarkt-api.fly.dev"
        
    def setup_driver(self):
        """Setup Chrome driver only when needed"""
        print("🛡️ Setting up browser for fallback scraping...")
        
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless')  # Run in background
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = uc.Chrome(options=options, version_main=None)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            print("✅ Browser configured for fallback")
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
    
    def test_api_connection(self):
        """Test if the transfermarkt API is available"""
        try:
            print("🌐 Testing transfermarkt API connection...")
            response = requests.get(f"{self.api_base_url}/", timeout=10)
            
            if response.status_code == 200:
                print("✅ API is available")
                return True
            else:
                print(f"⚠️  API returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API connection failed: {e}")
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
    
    def get_player_data_from_api(self, player_id):
        """Get player data from transfermarkt API"""
        try:
            print(f"    🌐 Fetching from API: {player_id}")
            
            # Try different API endpoints
            endpoints = [
                f"/players/{player_id}",
                f"/player/{player_id}",
                f"/players/{player_id}/transfers",
                f"/player/{player_id}/transfers"
            ]
            
            for endpoint in endpoints:
                try:
                    url = f"{self.api_base_url}{endpoint}"
                    response = requests.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✅ API data retrieved from {endpoint}")
                        return data
                    else:
                        print(f"    ⚠️  API endpoint {endpoint} returned {response.status_code}")
                        
                except Exception as e:
                    print(f"    ⚠️  API endpoint {endpoint} failed: {e}")
                    continue
            
            print(f"    ❌ All API endpoints failed")
            return None
            
        except Exception as e:
            print(f"    ❌ Error calling API: {e}")
            return None
    
    def extract_transfers_from_api_data(self, api_data):
        """Extract transfers from API response"""
        try:
            transfers = []
            
            # Try different data structures that the API might return
            if isinstance(api_data, dict):
                # Look for transfers in different possible keys
                transfer_keys = ['transfers', 'transfer_history', 'career', 'transfers_history']
                
                for key in transfer_keys:
                    if key in api_data:
                        transfer_data = api_data[key]
                        if isinstance(transfer_data, list):
                            for transfer in transfer_data:
                                if isinstance(transfer, dict):
                                    transfers.append({
                                        'season': transfer.get('season', ''),
                                        'date': transfer.get('date', ''),
                                        'left_club': transfer.get('from_club', transfer.get('left_club', '')),
                                        'joined_club': transfer.get('to_club', transfer.get('joined_club', '')),
                                        'market_value': transfer.get('market_value', ''),
                                        'transfer_fee': transfer.get('transfer_fee', transfer.get('fee', ''))
                                    })
                            break
            
            print(f"    ✅ Extracted {len(transfers)} transfers from API")
            return transfers
            
        except Exception as e:
            print(f"    ❌ Error extracting transfers from API: {e}")
            return []
    
    def extract_transfers_direct_scraping(self, player_name, player_id):
        """Direct scraping fallback when API fails"""
        try:
            print(f"    🔍 Direct scraping fallback...")
            
            if not self.driver:
                if not self.setup_driver():
                    return []
            
            transfers_url = f"https://www.transfermarkt.com/{player_name.lower().replace(' ', '-')}/transfers/spieler/{player_id}"
            print(f"    📊 Loading: {transfers_url}")
            
            self.driver.get(transfers_url)
            time.sleep(8)  # Longer wait
            
            page_source = self.driver.page_source
            
            # Check if page loaded properly
            if len(page_source) < 50000:
                print(f"    ⚠️  Page too small: {len(page_source)} chars")
                return []
            
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
                        if len(cells) >= 4:
                            transfers.append({
                                'season': cells[0].get_text(strip=True) if len(cells) > 0 else '',
                                'date': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                                'left_club': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                                'joined_club': cells[3].get_text(strip=True) if len(cells) > 3 else '',
                                'market_value': cells[4].get_text(strip=True) if len(cells) > 4 else '',
                                'transfer_fee': cells[5].get_text(strip=True) if len(cells) > 5 else ''
                            })
                    except:
                        continue
            
            print(f"    ✅ Extracted {len(transfers)} transfers via direct scraping")
            return transfers
            
        except Exception as e:
            print(f"    ❌ Error in direct scraping: {e}")
            return []
    
    def extract_birth_date_simple(self, player_name, profile_url):
        """Simple birth date extraction"""
        try:
            print(f"    📅 Extracting birth date...")
            
            if not self.driver:
                if not self.setup_driver():
                    return None
            
            self.driver.get(profile_url)
            time.sleep(6)
            
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
            
            # Try API first
            api_data = self.get_player_data_from_api(player_id)
            transfers = []
            
            if api_data:
                transfers = self.extract_transfers_from_api_data(api_data)
            
            # Fallback to direct scraping if API fails
            if not transfers:
                print(f"    🔄 API failed, trying direct scraping...")
                transfers = self.extract_transfers_direct_scraping(player_name, player_id)
            
            if not transfers:
                print(f"    ❌ No transfers found via any method")
                return []
            
            # Extract birth date (always via direct scraping for now)
            birth_date = self.extract_birth_date_simple(player_name, profile_url)
            if not birth_date:
                print(f"    ❌ No birth date found")
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
    
    def test_with_first_players(self, num_players=3):
        """Test with first N players"""
        print("🧪 Testing Hybrid Transfers Scraper...")
        print(f"📊 Testing with first {num_players} players")
        
        # Test API connection first
        api_available = self.test_api_connection()
        
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
                df_results.to_csv('hybrid_transfers_results.csv', index=False)
                print(f"\n💾 Saved test results: hybrid_transfers_results.csv")
                
                # Show sample results
                print(f"\n📊 Sample Results:")
                print(df_results[['player_name', 'club', 'player_age_at_transfer', 'solidarity_contribution']].head().to_string(index=False))
            
            # Summary
            print(f"\n📊 Test Results Summary:")
            print(f"  🌐 API available: {'✅ Yes' if api_available else '❌ No'}")
            print(f"  ✅ Successful requests: {self.successful_requests}")
            print(f"  ❌ Failed requests: {self.failed_requests}")
            print(f"  📝 Total solidarity records: {len(self.solidarity_data)}")
            
            if self.successful_requests >= 1:
                print(f"\n🎉 TEST SUCCESSFUL! Hybrid approach works!")
                return True
            else:
                print(f"\n⚠️  TEST NEEDS IMPROVEMENT. Low success rate.")
                return False
                
        finally:
            self.close_driver()

def main():
    """Main function"""
    scraper = HybridTransfersScraper()
    
    try:
        success = scraper.test_with_first_players(3)
        if success:
            print("\n🚀 Ready to launch hybrid transfers scraper for all players!")
        else:
            print("\n⚠️  Need to improve hybrid approach.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔚 Test completed")

if __name__ == "__main__":
    main()
