#!/usr/bin/env python3
"""
API Client for primeplayers/transfermarkt-api
Uses the deployed API to get detailed player data
"""
import requests
import pandas as pd
import time
import json
from typing import Dict, List, Optional

class TransfermarktAPIClient:
    def __init__(self, base_url: str = "https://transfermarkt-api.fly.dev"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
    def get_api_info(self):
        """Get API information and available endpoints"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting API info: {e}")
        return None
    
    def get_player_details(self, player_id: str) -> Optional[Dict]:
        """Get detailed player information by ID"""
        try:
            # Try different possible endpoints
            endpoints = [
                f"/player/{player_id}",
                f"/players/{player_id}",
                f"/profil/spieler/{player_id}",
                f"/api/player/{player_id}"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✓ Found player data via {endpoint}")
                        return data
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        print(f"    Status {response.status_code} for {endpoint}")
                except Exception as e:
                    print(f"    Error with {endpoint}: {e}")
                    continue
            
            print(f"    No data found for player {player_id}")
            return None
            
        except Exception as e:
            print(f"    Error getting player details: {e}")
            return None
    
    def search_players(self, query: str) -> Optional[List[Dict]]:
        """Search for players by name"""
        try:
            endpoints = [
                f"/search?q={query}",
                f"/players?search={query}",
                f"/api/search?query={query}"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✓ Found search results via {endpoint}")
                        return data
                    elif response.status_code == 404:
                        continue
                except Exception as e:
                    print(f"    Error with {endpoint}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"    Error searching players: {e}")
            return None
    
    def get_team_players(self, team_id: str) -> Optional[List[Dict]]:
        """Get all players from a team"""
        try:
            endpoints = [
                f"/team/{team_id}/players",
                f"/teams/{team_id}/players",
                f"/verein/{team_id}/kader",
                f"/api/team/{team_id}/players"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"    ✓ Found team players via {endpoint}")
                        return data
                    elif response.status_code == 404:
                        continue
                except Exception as e:
                    print(f"    Error with {endpoint}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"    Error getting team players: {e}")
            return None

def test_api_connection():
    """Test the API connection and available endpoints"""
    print("=== Testing Transfermarkt API Connection ===")
    
    client = TransfermarktAPIClient()
    
    # Test API info
    print("1. Getting API information...")
    api_info = client.get_api_info()
    if api_info:
        print(f"   API Info: {api_info}")
    else:
        print("   Could not get API info")
    
    # Test player search
    print("\n2. Testing player search...")
    search_results = client.search_players("Messi")
    if search_results:
        print(f"   Found {len(search_results)} results for 'Messi'")
        if isinstance(search_results, list) and len(search_results) > 0:
            print(f"   First result: {search_results[0]}")
    else:
        print("   No search results found")
    
    # Test specific player
    print("\n3. Testing specific player...")
    player_data = client.get_player_details("28003")  # Messi's ID
    if player_data:
        print(f"   Player data keys: {list(player_data.keys())}")
    else:
        print("   No player data found")

def process_players_with_api(players_df: pd.DataFrame, max_players: int = 10):
    """Process players using the API to get detailed information"""
    print(f"=== Processing {min(max_players, len(players_df))} players using API ===")
    
    client = TransfermarktAPIClient()
    detailed_players = []
    
    for idx, player in players_df.head(max_players).iterrows():
        print(f"\nPlayer {idx + 1}/{min(max_players, len(players_df))}: {player.get('full_name', 'Unknown')}")
        
        # Extract player ID from URL
        profile_url = player.get('profile_url', '')
        player_id = None
        
        if '/profil/spieler/' in profile_url:
            player_id = profile_url.split('/profil/spieler/')[-1].split('/')[0]
        elif '/profil-spieler/' in profile_url:
            player_id = profile_url.split('/profil-spieler/')[-1].split('/')[0]
        
        if player_id:
            print(f"    Player ID: {player_id}")
            
            # Get detailed data from API
            detailed_data = client.get_player_details(player_id)
            
            if detailed_data:
                # Merge basic info with detailed data
                player_data = player.to_dict()
                player_data.update(detailed_data)
                detailed_players.append(player_data)
                print(f"    ✓ Successfully got detailed data")
            else:
                # Keep basic data if API fails
                detailed_players.append(player.to_dict())
                print(f"    ⚠ Using basic data only")
        else:
            print(f"    ⚠ Could not extract player ID from URL")
            detailed_players.append(player.to_dict())
        
        # Rate limiting
        time.sleep(1)
    
    return detailed_players

def main():
    """Main function"""
    print("=== Transfermarkt API Client ===")
    
    # Test API connection first
    test_api_connection()
    
    # Load existing players data
    try:
        players_df = pd.read_csv('players_ALL_LEAGUES.csv')
        print(f"\nLoaded {len(players_df)} players from players_ALL_LEAGUES.csv")
    except FileNotFoundError:
        print("Error: players_ALL_LEAGUES.csv not found!")
        return
    
    # Process players using API
    print(f"\nProcessing first 10 players using API...")
    detailed_players = process_players_with_api(players_df, max_players=10)
    
    if detailed_players:
        # Save detailed data
        df_detailed = pd.DataFrame(detailed_players)
        csv_file = 'players_API_DETAILED.csv'
        df_detailed.to_csv(csv_file, index=False, encoding='utf-8')
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"Detailed data saved to: {csv_file}")
        print(f"Total players processed: {len(detailed_players)}")
        
        # Show sample of detailed data
        print(f"\n=== Sample Detailed Data ===")
        sample_cols = ['full_name', 'team_name', 'competition']
        available_cols = [col for col in sample_cols if col in df_detailed.columns]
        if available_cols:
            print(df_detailed[available_cols].head(10).to_string())
        
        return df_detailed
    else:
        print("No detailed player data collected!")
        return None

if __name__ == "__main__":
    df = main()
