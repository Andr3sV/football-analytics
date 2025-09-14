#!/usr/bin/env python3
"""
Merge Players Databases - Combine players from players_ALL_LEAGUES.csv and db-yt
Only include players that appear in both files
"""
import pandas as pd
import re
from urllib.parse import urlparse

def clean_name(name):
    """Clean player name for matching"""
    if pd.isna(name):
        return ""
    
    # Convert to lowercase and remove extra spaces
    name = str(name).lower().strip()
    
    # Remove special characters and normalize
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    
    return name

def extract_player_id_from_url(url):
    """Extract player ID from Transfermarkt URL"""
    if pd.isna(url):
        return None
    
    url_str = str(url)
    match = re.search(r'/spieler/(\d+)', url_str)
    if match:
        return match.group(1)
    return None

def merge_databases():
    """Merge the two databases"""
    print("🔄 Loading databases...")
    
    # Load players_ALL_LEAGUES.csv
    print("📊 Loading players_ALL_LEAGUES.csv...")
    df_all_leagues = pd.read_csv('players_ALL_LEAGUES.csv')
    print(f"   ✅ Loaded {len(df_all_leagues)} players from players_ALL_LEAGUES.csv")
    
    # Load db-yt
    print("📊 Loading db-yt...")
    df_db_yt = pd.read_csv('db-old/db-yt - db5 (1).csv')
    print(f"   ✅ Loaded {len(df_db_yt)} players from db-yt")
    
    # Display column information
    print(f"\n📋 Columns in players_ALL_LEAGUES.csv:")
    for i, col in enumerate(df_all_leagues.columns):
        print(f"   {i+1}. {col}")
    
    print(f"\n📋 Columns in db-yt:")
    for i, col in enumerate(df_db_yt.columns):
        print(f"   {i+1}. {col}")
    
    # Create player ID mapping for db-yt
    print(f"\n🔍 Extracting player IDs from db-yt...")
    df_db_yt['player_id'] = df_db_yt['url'].apply(extract_player_id_from_url)
    df_db_yt['clean_name'] = df_db_yt['name'].apply(clean_name)
    
    # Create player ID mapping for players_ALL_LEAGUES
    print(f"🔍 Extracting player IDs from players_ALL_LEAGUES...")
    df_all_leagues['player_id'] = df_all_leagues['profile_url'].apply(extract_player_id_from_url)
    df_all_leagues['clean_name'] = df_all_leagues['full_name'].apply(clean_name)
    
    # Find matches by player ID first (most reliable)
    print(f"\n🎯 Finding matches by player ID...")
    matches_by_id = df_all_leagues.merge(
        df_db_yt, 
        on='player_id', 
        how='inner',
        suffixes=('_all_leagues', '_db_yt')
    )
    print(f"   ✅ Found {len(matches_by_id)} matches by player ID")
    
    # Find matches by name for players without ID matches
    print(f"🎯 Finding additional matches by name...")
    
    # Get players from all_leagues that weren't matched by ID
    unmatched_all_leagues = df_all_leagues[~df_all_leagues['player_id'].isin(matches_by_id['player_id'])]
    
    # Get players from db_yt that weren't matched by ID
    unmatched_db_yt = df_db_yt[~df_db_yt['player_id'].isin(matches_by_id['player_id'])]
    
    # Try to match by clean name
    matches_by_name = unmatched_all_leagues.merge(
        unmatched_db_yt,
        on='clean_name',
        how='inner',
        suffixes=('_all_leagues', '_db_yt')
    )
    print(f"   ✅ Found {len(matches_by_name)} additional matches by name")
    
    # Combine both types of matches
    if len(matches_by_id) > 0 and len(matches_by_name) > 0:
        combined_matches = pd.concat([matches_by_id, matches_by_name], ignore_index=True)
    elif len(matches_by_id) > 0:
        combined_matches = matches_by_id
    elif len(matches_by_name) > 0:
        combined_matches = matches_by_name
    else:
        combined_matches = pd.DataFrame()
    
    print(f"\n📊 Total matches found: {len(combined_matches)}")
    
    if len(combined_matches) == 0:
        print("❌ No matches found between the two databases!")
        return None
    
    # Create the merged dataset
    print(f"\n🔧 Creating merged dataset...")
    
    # Debug: Check what columns are available
    print(f"Available columns in combined_matches: {list(combined_matches.columns)}")
    
    # Select and rename columns to avoid duplicates and conflicts
    merged_df = pd.DataFrame()
    
    # From players_ALL_LEAGUES (keep these as primary)
    # Handle different column name variations
    if 'full_name_all_leagues' in combined_matches.columns:
        merged_df['full_name'] = combined_matches['full_name_all_leagues']
    elif 'full_name' in combined_matches.columns:
        merged_df['full_name'] = combined_matches['full_name']
    else:
        merged_df['full_name'] = combined_matches['name_all_leagues']
    
    merged_df['team_name'] = combined_matches['team_name']
    merged_df['competition'] = combined_matches['competition']
    merged_df['profile_url'] = combined_matches['profile_url']
    merged_df['relative_profile_url'] = combined_matches['relative_profile_url']
    merged_df['season'] = combined_matches['season']
    merged_df['player_id'] = combined_matches['player_id']
    
    # From db-yt (add all unique columns)
    db_yt_columns = [col for col in df_db_yt.columns if col not in ['name', 'url', 'player_id', 'clean_name']]
    
    for col in db_yt_columns:
        if col in combined_matches.columns:
            # Use the _db_yt suffix version if available
            col_name = f"{col}_db_yt" if f"{col}_db_yt" in combined_matches.columns else col
            merged_df[f"db_yt_{col}"] = combined_matches[col_name]
        else:
            # Handle case where column might have different suffix
            possible_cols = [c for c in combined_matches.columns if c.startswith(col)]
            if possible_cols:
                merged_df[f"db_yt_{col}"] = combined_matches[possible_cols[0]]
    
    # Save the merged dataset
    output_file = 'merged_players_databases.csv'
    merged_df.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved merged dataset to: {output_file}")
    print(f"📊 Total players in merged dataset: {len(merged_df)}")
    
    # Show sample of merged data
    print(f"\n📋 Sample of merged data:")
    print(f"Columns: {list(merged_df.columns)}")
    print(f"\nFirst 5 rows:")
    print(merged_df.head().to_string())
    
    # Show statistics
    print(f"\n📊 Statistics:")
    print(f"   Players from players_ALL_LEAGUES: {len(df_all_leagues)}")
    print(f"   Players from db-yt: {len(df_db_yt)}")
    print(f"   Players in both databases: {len(merged_df)}")
    print(f"   Match rate: {len(merged_df)/min(len(df_all_leagues), len(df_db_yt))*100:.1f}%")
    
    return merged_df

def main():
    """Main function"""
    try:
        merged_df = merge_databases()
        
        if merged_df is not None:
            print(f"\n🎉 Successfully merged databases!")
            print(f"📁 Output file: merged_players_databases.csv")
            print(f"📊 Total players: {len(merged_df)}")
        else:
            print(f"\n❌ Failed to merge databases")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
