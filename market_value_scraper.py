#!/usr/bin/env python3
"""
Market Value Scraper - Extract only current market value from player profiles
Focused scraper to avoid Transfermarkt blocking by only getting market value
"""
import pandas as pd
import time
import json
import os
import re
import random
from datetime import datetime
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MarketValueScraper:
    def __init__(self):
        self.driver = None
        self.market_values = []
        self.successful_requests = 0
        self.failed_requests = 0
        self.blocked_requests = 0
        
    def setup_driver(self):
        """Setup Chrome driver with maximum stealth for market value extraction"""
        print("🛡️ Setting up market value browser...")
        
        try:
            # Kill any existing Chrome processes
            os.system('pkill -f chrome 2>/dev/null || true')
            time.sleep(3)
            
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
                }
            })
            
            # Create driver
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Enhanced stealth measures
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            # Randomize viewport
            self.driver.set_window_size(1920 + random.randint(-100, 100), 1080 + random.randint(-100, 100))
            
            self.driver.set_page_load_timeout(45)
            self.driver.implicitly_wait(15)
            
            print("✅ Market value browser configured")
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
        print(f"    ⏱️  Delay: {delay:.1f} seconds...")
        time.sleep(delay)
    
    def handle_cookie_consent_simple(self):
        """Simple cookie consent handling"""
        try:
            print("    🍪 Handling cookie consent...")
            time.sleep(3)
            
            # Try to find and click any accept button
            try:
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
            
            print("    ⚠️  Could not find cookie consent button - continuing anyway")
            return False
            
        except Exception as e:
            print(f"    ⚠️  Error handling cookie consent: {e}")
            return False
    
    def is_page_blocked(self, page_source):
        """Check if page is blocked by Transfermarkt"""
        try:
            # Check for common block indicators
            block_indicators = [
                'access denied',
                'blocked',
                'bot detected',
                'too many requests',
                'rate limit',
                'captcha',
                'verification required'
            ]
            
            page_lower = page_source.lower()
            for indicator in block_indicators:
                if indicator in page_lower:
                    return True
            
            # Check page size (too small usually means blocked)
            if len(page_source) < 10000:
                return True
            
            return False
            
        except:
            return True
    
    def extract_market_value_from_profile(self, player_name, player_id):
        """Extract only the current market value from player profile"""
        try:
            # Construct profile URL
            profile_url = f"https://www.transfermarkt.com/{player_name.lower().replace(' ', '-')}/profil/spieler/{player_id}"
            print(f"    🌐 Loading profile: {profile_url}")
            
            self.driver.get(profile_url)
            
            # Long delay
            self.long_delay(20, 40)
            
            # Handle cookie consent
            self.handle_cookie_consent_simple()
            
            # Additional delay
            time.sleep(random.uniform(3, 6))
            
            # Get page source
            page_source = self.driver.page_source
            
            # Check if page loaded properly
            if self.is_page_blocked(page_source):
                print(f"    ❌ Profile page blocked by Transfermarkt")
                self.blocked_requests += 1
                return None
            
            print(f"    ✅ Profile page loaded: {len(page_source)} chars")
            
            # Look for market value patterns
            market_value_patterns = [
                r'Market value:\s*€([0-9,.]+[mk]?)',
                r'Current market value:\s*€([0-9,.]+[mk]?)',
                r'Value:\s*€([0-9,.]+[mk]?)',
                r'€([0-9,.]+[mk]?)\s*last update',
                r'€([0-9,.]+[mk]?)\s*aktualisiert',
                r'€([0-9,.]+[mk]?)\s*actualizado'
            ]
            
            for pattern in market_value_patterns:
                match = re.search(pattern, page_source, re.IGNORECASE)
                if match:
                    market_value = f"€{match.group(1)}"
                    print(f"    ✅ Found market value: {market_value}")
                    return market_value
            
            # Try to find market value in meta tags or specific elements
            try:
                # Look for market value in specific div elements
                market_value_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "div[class*='markt'], span[class*='wert'], div[class*='value']")
                
                for element in market_value_elements:
                    text = element.text
                    if '€' in text and any(char.isdigit() for char in text):
                        # Extract the value
                        value_match = re.search(r'€([0-9,.]+[mk]?)', text)
                        if value_match:
                            market_value = f"€{value_match.group(1)}"
                            print(f"    ✅ Found market value in element: {market_value}")
                            return market_value
            except:
                pass
            
            print(f"    ❌ No market value found")
            return None
            
        except Exception as e:
            print(f"    ❌ Error extracting market value: {e}")
            return None
    
    def extract_market_values_batch(self, players_df, start_index=0, batch_size=10):
        """Extract market values for a batch of players"""
        print(f"🔄 Processing batch starting at index {start_index}")
        
        batch_results = []
        end_index = min(start_index + batch_size, len(players_df))
        
        for i in range(start_index, end_index):
            player = players_df.iloc[i]
            
            try:
                player_name = player['full_name']
                player_id = str(int(player['player_id']))  # Convert to int then string to remove decimals
                
                print(f"\n🔍 Processing {i + 1}/{len(players_df)}: {player_name} (ID: {player_id})")
                
                market_value = self.extract_market_value_from_profile(player_name, player_id)
                
                if market_value:
                    batch_results.append({
                        'player_id': player_id,
                        'full_name': player_name,
                        'current_market_value': market_value,
                        'extracted_at': datetime.now().isoformat()
                    })
                    self.successful_requests += 1
                    print(f"    ✅ Market value: {market_value}")
                else:
                    self.failed_requests += 1
                    print(f"    ❌ No market value found")
                
                # Very long delay between players
                if i < end_index - 1:  # Don't delay after last player
                    self.long_delay(60, 120)  # 1-2 minutes between players
                
            except Exception as e:
                print(f"❌ Error processing player: {e}")
                self.failed_requests += 1
                continue
        
        return batch_results
    
    def test_with_few_players(self, num_players=3):
        """Test with a few players first"""
        print("🧪 Testing Market Value Scraper...")
        print(f"📊 Testing with first {num_players} players")
        
        # Setup browser
        if not self.setup_driver():
            print("❌ Failed to setup browser")
            return False
        
        try:
            # Load players from cleaned dataset
            df = pd.read_csv('merged_players_databases_cleaned.csv')
            test_players = df.head(num_players)
            
            print(f"📋 Processing {len(test_players)} test players...")
            
            batch_results = self.extract_market_values_batch(test_players, 0, num_players)
            
            if batch_results:
                # Save test results
                df_results = pd.DataFrame(batch_results)
                df_results.to_csv('market_values_test_results.csv', index=False)
                print(f"\n💾 Saved test results: market_values_test_results.csv")
                
                # Show results
                print(f"\n📊 Test Results:")
                print(df_results.to_string(index=False))
            
            # Summary
            print(f"\n📊 Test Results Summary:")
            print(f"  ✅ Successful requests: {self.successful_requests}")
            print(f"  ❌ Failed requests: {self.failed_requests}")
            print(f"  🚫 Blocked requests: {self.blocked_requests}")
            print(f"  📝 Total market values extracted: {len(batch_results)}")
            
            if self.successful_requests >= 1:
                print(f"\n🎉 TEST SUCCESSFUL! Market value extraction works!")
                return True
            else:
                print(f"\n⚠️  TEST FAILED. Need to improve approach.")
                return False
                
        finally:
            self.close_driver()

def main():
    """Main function"""
    scraper = MarketValueScraper()
    
    try:
        success = scraper.test_with_few_players(3)
        if success:
            print("\n🚀 Ready to extract market values for all players!")
            print("⚠️  Note: This will take a VERY long time due to delays (1-2 minutes per player)")
        else:
            print("\n⚠️  Need to improve market value extraction.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("🔚 Test completed")

if __name__ == "__main__":
    main()
