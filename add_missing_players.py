#!/usr/bin/env python3
"""
Add Missing Players - Add the 794 missing players with detailed data to the main database
"""
import pandas as pd
import re
import numpy as np

def extract_player_id_from_url(profile_url):
    """Extract player ID from Transfermarkt profile URL"""
    if pd.isna(profile_url):
        return None
    
    url_str = str(profile_url)
    match = re.search(r'/spieler/(\d+)', url_str)
    if match:
        return int(match.group(1))
    return None

def add_missing_players():
    """Add missing players to the main database"""
    print("🔄 Loading main enriched database...")
    
    # Load the main enriched database
    df_main = pd.read_csv('merged_players_databases_enriched.csv')
    print(f"   ✅ Loaded {len(df_main)} players from main database")
    
    print("🔄 Loading missing players with detailed data...")
    
    # Load the missing players
    df_missing = pd.read_csv('missing_players_with_data.csv')
    print(f"   ✅ Loaded {len(df_missing)} missing players with detailed data")
    
    # Load all_leagues for additional context
    df_all_leagues = pd.read_csv('players_ALL_LEAGUES.csv')
    print(f"   ✅ Loaded {len(df_all_leagues)} players from all_leagues for context")
    
    print("🔍 Processing missing players...")
    
    # Extract player IDs
    df_missing['player_id'] = df_missing['profile_url'].apply(extract_player_id_from_url)
    df_all_leagues['all_leagues_player_id'] = df_all_leagues['profile_url'].apply(extract_player_id_from_url)
    
    # Get the missing player IDs that we want to add
    missing_ids = set(df_missing['player_id'].dropna())
    print(f"   📊 Missing player IDs to add: {len(missing_ids)}")
    
    # Find these players in all_leagues to get their basic info
    df_missing_from_leagues = df_all_leagues[df_all_leagues['all_leagues_player_id'].isin(missing_ids)]
    print(f"   📊 Found {len(df_missing_from_leagues)} missing players in all_leagues")
    
    # Prepare the missing players for addition
    print("🔧 Preparing missing players for addition...")
    
    # Create a new dataframe for missing players
    missing_players = []
    
    for _, player in df_missing_from_leagues.iterrows():
        player_id = player['all_leagues_player_id']
        
        # Find detailed data for this player
        detailed_data = df_missing[df_missing['player_id'] == player_id]
        
        if len(detailed_data) > 0:
            detailed = detailed_data.iloc[0]  # Take the first match
            
            # Create new player record
            new_player = {
                'full_name': player['full_name'],
                'team_name': player['team_name'],
                'competition': player['competition'],
                'profile_url': player['profile_url'],
                'relative_profile_url': player['relative_profile_url'],
                'season': player['season'],
                'player_id': player_id,
                
                # Add detailed data
                'market_value': detailed.get('market_value', None),
                'age': detailed.get('age', None),
                'nationality': detailed.get('nationality', None),
                'current_club': detailed.get('current_club', None),
                'position': detailed.get('position', None),
                'date_of_birth': detailed.get('date_of_birth', None),
                'city_of_birth': detailed.get('city_of_birth', None),
                'country_of_birth': detailed.get('country_of_birth', None),
                'place_of_birth': detailed.get('place_of_birth', None),
                'dominant_foot': detailed.get('dominant_foot', None),
                'agent': detailed.get('agent', None),
                'social_links': detailed.get('social_links', None),
                
                # Add empty columns for youth club data (since these players don't have it)
                'db_yt_id': None,
                'db_yt_name': None,
                'db_yt_date_of_birth': None,
                'db_yt_Yname': None,
                'db_yt_transfer_date': None,
                'db_yt_market_value': None,
                'db_yt_url': None,
                'db_yt_clean_name': None,
                'youth_club': None,
                'from_to': None,
                'year_in_the_club_numeric': None
            }
            
            missing_players.append(new_player)
    
    print(f"   ✅ Prepared {len(missing_players)} missing players for addition")
    
    # Convert to DataFrame
    df_missing_players = pd.DataFrame(missing_players)
    
    # Ensure all columns exist in both dataframes
    print("🔧 Aligning column structure...")
    
    # Get all columns from both dataframes
    all_columns = set(df_main.columns) | set(df_missing_players.columns)
    
    # Add missing columns to both dataframes
    for col in all_columns:
        if col not in df_main.columns:
            df_main[col] = None
        if col not in df_missing_players.columns:
            df_missing_players[col] = None
    
    # Reorder columns to match
    df_missing_players = df_missing_players[df_main.columns]
    
    print("🔧 Adding missing players to main database...")
    
    # Combine the dataframes
    df_combined = pd.concat([df_main, df_missing_players], ignore_index=True)
    
    # Remove any potential duplicates based on player_id
    df_combined = df_combined.drop_duplicates(subset=['player_id'], keep='first')
    
    print(f"   ✅ Combined database created with {len(df_combined)} players")
    
    # Statistics
    print(f"\n📊 STATISTICS:")
    print(f"   Original players: {len(df_main)}")
    print(f"   Missing players added: {len(df_missing_players)}")
    print(f"   Total players: {len(df_combined)}")
    
    # Market value statistics
    market_value_count = df_combined['market_value'].notna().sum()
    print(f"   Players with market value: {market_value_count}")
    
    # Age statistics
    age_count = df_combined['age'].notna().sum()
    print(f"   Players with age: {age_count}")
    
    # Nationality statistics
    nationality_count = df_combined['nationality'].notna().sum()
    print(f"   Players with nationality: {nationality_count}")
    
    # Position statistics
    position_count = df_combined['position'].notna().sum()
    print(f"   Players with position: {position_count}")
    
    # Show examples of newly added players
    print(f"\n📋 Examples of newly added players:")
    newly_added = df_combined[df_combined['market_value'].notna() & df_combined['db_yt_id'].isna()][
        ['full_name', 'market_value', 'age', 'nationality', 'position', 'current_club']
    ].head(10)
    print(newly_added.to_string(index=False))
    
    # Save the enhanced database
    output_file = 'merged_players_databases_final.csv'
    df_combined.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved final enhanced database to: {output_file}")
    print(f"📊 Total players: {len(df_combined)}")
    
    return df_combined

def main():
    """Main function"""
    try:
        enhanced_df = add_missing_players()
        
        if enhanced_df is not None:
            print(f"\n🎉 Successfully enhanced database with missing players!")
            print(f"📁 Output file: merged_players_databases_final.csv")
            print(f"📊 Total players: {len(enhanced_df)}")
            print(f"📊 Players with market value: {enhanced_df['market_value'].notna().sum()}")
        else:
            print(f"\n❌ Failed to enhance database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
