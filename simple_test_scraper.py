#!/usr/bin/env python3
"""
Simple Test Scraper to verify connectivity and basic functionality
"""
import pandas as pd
import requests
import time
from fake_useragent import UserAgent
import cloudscraper

def test_scraper():
    """Test basic scraping functionality"""
    print("🧪 Testing basic scraping functionality...")
    
    # Setup
    session = cloudscraper.create_scraper()
    ua = UserAgent()
    
    # Test with a known player
    test_url = "https://www.transfermarkt.com/thibaut-courtois/profil/spieler/108390"
    
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print(f"🌐 Testing URL: {test_url}")
    
    try:
        response = session.get(test_url, headers=headers, timeout=30)
        print(f"📊 Response status: {response.status_code}")
        print(f"📏 Content length: {len(response.content)}")
        
        if response.status_code == 200:
            print("✅ Successfully fetched page")
            
            # Check if we got blocked
            if "blocked" in response.text.lower() or "access denied" in response.text.lower():
                print("❌ Page indicates we're blocked")
                return False
            
            # Look for player data
            if "thibaut courtois" in response.text.lower():
                print("✅ Player data found in response")
                return True
            else:
                print("⚠️  Player data not found in response")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_multiple_players():
    """Test with multiple players from our dataset"""
    print("\n🔄 Testing with multiple players...")
    
    # Load our players data
    try:
        df = pd.read_csv('players_ALL_LEAGUES.csv')
        print(f"📊 Loaded {len(df)} players")
        
        # Test first 5 players
        test_players = df.head(5)
        
        session = cloudscraper.create_scraper()
        ua = UserAgent()
        
        success_count = 0
        
        for i, player in test_players.iterrows():
            player_name = player['full_name']
            profile_url = player['profile_url']
            
            print(f"\n🔍 Testing {i+1}/5: {player_name}")
            
            headers = {
                'User-Agent': ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            try:
                response = session.get(profile_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    print(f"  ✅ HTTP {response.status_code} - {len(response.content)} bytes")
                    success_count += 1
                else:
                    print(f"  ❌ HTTP {response.status_code}")
                
                # Delay between requests
                time.sleep(2)
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print(f"\n📊 Results: {success_count}/5 successful requests")
        return success_count >= 3
        
    except Exception as e:
        print(f"❌ Error loading players: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 SIMPLE SCRAPER TEST")
    print("=" * 50)
    
    # Test 1: Single player
    test1_result = test_scraper()
    
    # Test 2: Multiple players
    test2_result = test_multiple_players()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"  Single player test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"  Multiple players test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! Scraping should work.")
    else:
        print("\n⚠️  Some tests failed. There may be connectivity issues.")
    
    print("\n🔚 Test completed")

if __name__ == "__main__":
    main()
