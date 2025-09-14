#!/usr/bin/env python3
"""
Check Missing Players - Find players that exist in progress files and players_ALL_LEAGUES
but are missing from the main enriched database
"""
import pandas as pd
import re

def extract_player_id_from_url(profile_url):
    """Extract player ID from Transfermarkt profile URL"""
    if pd.isna(profile_url):
        return None
    
    url_str = str(profile_url)
    match = re.search(r'/spieler/(\d+)', url_str)
    if match:
        return int(match.group(1))
    return None

def check_missing_players():
    """Check for missing players across databases"""
    print("🔄 Loading all databases...")
    
    # Load main enriched database
    df_main = pd.read_csv('merged_players_databases_enriched.csv')
    print(f"   ✅ Main enriched database: {len(df_main)} players")
    
    # Load progress files
    df_stealth = pd.read_csv('players_FINAL_STEALTH_PROGRESS_3525.csv')
    print(f"   ✅ Stealth progress: {len(df_stealth)} players")
    
    df_robust = pd.read_csv('players_ROBUST_PROGRESS_2200.csv')
    print(f"   ✅ Robust progress: {len(df_robust)} players")
    
    # Load original players_ALL_LEAGUES
    df_all_leagues = pd.read_csv('players_ALL_LEAGUES.csv')
    print(f"   ✅ All leagues: {len(df_all_leagues)} players")
    
    print("\n🔍 Extracting player IDs...")
    
    # Extract player IDs from all sources
    df_main['main_player_id'] = pd.to_numeric(df_main['player_id'], errors='coerce').astype('Int64')
    df_stealth['stealth_player_id'] = df_stealth['profile_url'].apply(extract_player_id_from_url)
    df_robust['robust_player_id'] = df_robust['profile_url'].apply(extract_player_id_from_url)
    df_all_leagues['all_leagues_player_id'] = df_all_leagues['profile_url'].apply(extract_player_id_from_url)
    
    # Get unique player IDs from each source
    main_ids = set(df_main['main_player_id'].dropna())
    stealth_ids = set(df_stealth['stealth_player_id'].dropna())
    robust_ids = set(df_robust['robust_player_id'].dropna())
    all_leagues_ids = set(df_all_leagues['all_leagues_player_id'].dropna())
    
    print(f"   📊 Unique player IDs in main database: {len(main_ids)}")
    print(f"   📊 Unique player IDs in stealth progress: {len(stealth_ids)}")
    print(f"   📊 Unique player IDs in robust progress: {len(robust_ids)}")
    print(f"   📊 Unique player IDs in all leagues: {len(all_leagues_ids)}")
    
    # Find players in progress files but not in main database
    print("\n🔍 Analyzing missing players...")
    
    # Players in stealth but not in main
    stealth_missing = stealth_ids - main_ids
    print(f"   📋 Players in stealth progress but NOT in main: {len(stealth_missing)}")
    
    # Players in robust but not in main
    robust_missing = robust_ids - main_ids
    print(f"   📋 Players in robust progress but NOT in main: {len(robust_missing)}")
    
    # Players in all_leagues but not in main
    all_leagues_missing = all_leagues_ids - main_ids
    print(f"   📋 Players in all_leagues but NOT in main: {len(all_leagues_missing)}")
    
    # Players in progress files AND all_leagues but not in main
    progress_ids = stealth_ids | robust_ids
    progress_and_leagues_missing = (progress_ids & all_leagues_ids) - main_ids
    print(f"   📋 Players in progress files AND all_leagues but NOT in main: {len(progress_and_leagues_missing)}")
    
    # Show examples of missing players
    if len(progress_and_leagues_missing) > 0:
        print(f"\n📋 Examples of missing players (in progress + all_leagues but not in main):")
        
        # Get player details from progress files
        missing_stealth = df_stealth[df_stealth['stealth_player_id'].isin(progress_and_leagues_missing)]
        missing_robust = df_robust[df_robust['robust_player_id'].isin(progress_and_leagues_missing)]
        
        # Combine and show examples
        if len(missing_stealth) > 0:
            print(f"\n   From stealth progress:")
            for _, player in missing_stealth.head(5).iterrows():
                print(f"   • {player['full_name']} (ID: {player['stealth_player_id']}) - {player.get('market_value', 'N/A')}")
        
        if len(missing_robust) > 0:
            print(f"\n   From robust progress:")
            for _, player in missing_robust.head(5).iterrows():
                print(f"   • {player['full_name']} (ID: {player['robust_player_id']}) - {player.get('market_value', 'N/A')}")
        
        # Get details from all_leagues for context
        missing_all_leagues = df_all_leagues[df_all_leagues['all_leagues_player_id'].isin(progress_and_leagues_missing)]
        print(f"\n   From all_leagues (context):")
        for _, player in missing_all_leagues.head(5).iterrows():
            print(f"   • {player['full_name']} - {player.get('team_name', 'N/A')} ({player.get('competition', 'N/A')})")
    
    # Summary statistics
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Main database has: {len(main_ids)} unique players")
    print(f"   📋 Missing from main (in progress files): {len(progress_ids - main_ids)}")
    print(f"   📋 Missing from main (in all_leagues): {len(all_leagues_missing)}")
    print(f"   📋 Missing from main (in both progress + all_leagues): {len(progress_and_leagues_missing)}")
    
    # Check if we can add these missing players
    if len(progress_and_leagues_missing) > 0:
        print(f"\n💡 RECOMMENDATION:")
        print(f"   There are {len(progress_and_leagues_missing)} players with scraped data that could be added to the main database.")
        print(f"   These players have detailed information (market value, age, etc.) that would enrich the dataset.")
        
        # Save missing players for potential addition
        missing_stealth_details = df_stealth[df_stealth['stealth_player_id'].isin(progress_and_leagues_missing)]
        missing_robust_details = df_robust[df_robust['robust_player_id'].isin(progress_and_leagues_missing)]
        
        if len(missing_stealth_details) > 0 or len(missing_robust_details) > 0:
            missing_combined = pd.concat([missing_stealth_details, missing_robust_details], ignore_index=True)
            missing_combined = missing_combined.drop_duplicates(subset=['stealth_player_id', 'robust_player_id'], keep='last')
            
            output_file = 'missing_players_with_data.csv'
            missing_combined.to_csv(output_file, index=False)
            print(f"   💾 Saved missing players with data to: {output_file}")
    
    return {
        'main_ids': main_ids,
        'stealth_ids': stealth_ids,
        'robust_ids': robust_ids,
        'all_leagues_ids': all_leagues_ids,
        'missing_count': len(progress_and_leagues_missing),
        'missing_ids': progress_and_leagues_missing
    }

def main():
    """Main function"""
    try:
        results = check_missing_players()
        
        if results['missing_count'] > 0:
            print(f"\n🎯 CONCLUSION:")
            print(f"   Found {results['missing_count']} players with scraped data that are missing from the main database.")
            print(f"   These players could be added to enrich the dataset further.")
        else:
            print(f"\n✅ All players with scraped data are already in the main database.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
