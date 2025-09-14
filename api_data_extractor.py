#!/usr/bin/env python3
"""
Data extractor using the Transfermarkt API from primeplayers
"""
import requests
import pandas as pd
import time
import json
from typing import List, Dict, Any

# API base URL
API_BASE_URL = "https://transfermarkt-api.fly.dev"

# Competition codes and their names
COMPETITIONS = {
    "ES1": "LaLiga",
    "GB1": "Premier League", 
    "IT1": "Serie A",
    "FR1": "Ligue 1",
    "L1": "Bundesliga",
    "PO1": "Liga Portugal",
    "BE1": "Pro League",
    "PL1": "Ekstraklasa",
    "KOR1": "K League 1",
    "SA1": "Saudi Pro League",
    "QA1": "Stars League",
    "TS1": "Fortuna Liga",
    "NO1": "Eliteserien",
    "SC1": "Premiership",
    "BRA1": "Serie A (Brazil)",
    "COL1": "Categoria Primera A",
    "SW1": "Super League",
    "TR1": "Super Lig"
}

def get_competition_teams(competition_id: str) -> List[Dict[str, Any]]:
    """Get teams from a competition"""
    url = f"{API_BASE_URL}/competitions/{competition_id}/teams"
    print(f"Fetching teams for {competition_id}: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'teams' in data:
            print(f"Found {len(data['teams'])} teams")
            return data['teams']
        else:
            print(f"No teams found in response: {data}")
            return []
            
    except Exception as e:
        print(f"Error fetching teams for {competition_id}: {e}")
        return []

def get_team_players(team_id: str, team_name: str, competition: str) -> List[Dict[str, Any]]:
    """Get players from a team"""
    url = f"{API_BASE_URL}/teams/{team_id}/players"
    print(f"Fetching players for {team_name} (ID: {team_id})")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'players' in data:
            players = data['players']
            print(f"Found {len(players)} players")
            
            # Add competition and team info to each player
            for player in players:
                player['competition'] = competition
                player['team_name'] = team_name
                player['team_id'] = team_id
                
            return players
        else:
            print(f"No players found in response: {data}")
            return []
            
    except Exception as e:
        print(f"Error fetching players for {team_name}: {e}")
        return []

def get_player_details(player_id: str) -> Dict[str, Any]:
    """Get detailed player information"""
    url = f"{API_BASE_URL}/players/{player_id}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'player' in data:
            return data['player']
        else:
            return {}
            
    except Exception as e:
        print(f"Error fetching details for player {player_id}: {e}")
        return {}

def extract_all_players():
    """Extract players from all competitions"""
    all_players = []
    
    print("=== Starting data extraction from Transfermarkt API ===")
    print(f"API Base URL: {API_BASE_URL}")
    
    for comp_id, comp_name in COMPETITIONS.items():
        print(f"\n=== Processing {comp_name} ({comp_id}) ===")
        
        # Get teams from competition
        teams = get_competition_teams(comp_id)
        
        if not teams:
            print(f"No teams found for {comp_name}")
            continue
            
        # Get players from each team (limit to first 3 teams per competition for speed)
        for team in teams[:3]:
            team_id = team.get('id', '')
            team_name = team.get('name', 'Unknown Team')
            
            if team_id:
                players = get_team_players(team_id, team_name, comp_id)
                all_players.extend(players)
                
                # Rate limiting - be respectful
                time.sleep(1)
        
        # Delay between competitions
        time.sleep(2)
    
    return all_players

def enrich_player_data(players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enrich player data with detailed information"""
    enriched_players = []
    
    print(f"\n=== Enriching data for {len(players)} players ===")
    
    for i, player in enumerate(players):
        player_id = player.get('id', '')
        
        if player_id:
            print(f"Enriching player {i+1}/{len(players)}: {player.get('name', 'Unknown')}")
            
            # Get detailed player information
            details = get_player_details(player_id)
            
            # Merge basic and detailed data
            enriched_player = {**player, **details}
            enriched_players.append(enriched_player)
            
            # Rate limiting
            time.sleep(0.5)
        else:
            enriched_players.append(player)
    
    return enriched_players

def save_to_csv(players: List[Dict[str, Any]], filename: str = "players_complete_data.csv"):
    """Save players data to CSV"""
    if not players:
        print("No players to save!")
        return
    
    df = pd.DataFrame(players)
    df.to_csv(filename, index=False, encoding='utf-8')
    
    print(f"\n=== Data saved to {filename} ===")
    print(f"Total players: {len(players)}")
    print(f"Competitions: {df['competition'].nunique()}")
    print(f"Teams: {df['team_name'].nunique()}")
    
    print(f"\n=== Sample data ===")
    # Show available columns
    print("Available columns:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. {col}")
    
    # Show sample data
    sample_cols = ['name', 'team_name', 'competition', 'position', 'age', 'nationality', 'market_value']
    available_cols = [col for col in sample_cols if col in df.columns]
    
    if available_cols:
        print(f"\nSample data:")
        print(df[available_cols].head(10).to_string())
    
    return df

def main():
    """Main function"""
    print("=== Transfermarkt Data Extractor ===")
    print("Using API: https://transfermarkt-api.fly.dev/")
    
    # Test API connection
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        print(f"API Status: {response.status_code}")
    except Exception as e:
        print(f"API connection failed: {e}")
        return
    
    # Extract basic player data
    players = extract_all_players()
    
    if not players:
        print("No players extracted!")
        return
    
    # Save basic data first
    basic_df = save_to_csv(players, "players_basic_data.csv")
    
    # Ask if user wants to enrich data (this takes longer)
    print(f"\n=== Basic extraction complete ===")
    print(f"Extracted {len(players)} players")
    print("Basic data saved to: players_basic_data.csv")
    
    # For now, just save the basic data
    # In a real scenario, you might want to enrich with detailed player info
    print("\n=== Extraction Complete ===")
    
    return basic_df

if __name__ == "__main__":
    df = main()
