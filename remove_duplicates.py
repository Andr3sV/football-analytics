#!/usr/bin/env python3
"""
Remove Duplicates - Remove duplicate players keeping the one with most recent db_yt_transfer_date
"""
import pandas as pd
import numpy as np
from datetime import datetime

def remove_duplicate_players():
    """Remove duplicate players keeping the most recent transfer date"""
    print("🔄 Loading cleaned dataset...")
    
    # Load the cleaned dataset
    df = pd.read_csv('merged_players_databases_cleaned.csv')
    print(f"   ✅ Loaded {len(df)} players")
    
    print(f"\n🔍 Analyzing duplicates...")
    
    # Check for duplicates by player_id only
    duplicates_by_id = df['player_id'].duplicated()
    id_duplicates_count = duplicates_by_id.sum()
    print(f"   📊 Duplicates by player_id: {id_duplicates_count}")
    
    # Show info about full_name duplicates (for reference only)
    duplicates_by_name = df['full_name'].duplicated()
    name_duplicates_count = duplicates_by_name.sum()
    print(f"   📊 Duplicates by full_name: {name_duplicates_count} (not removing these)")
    
    # Show examples of duplicates
    if id_duplicates_count > 0:
        print(f"\n📋 Examples of duplicates by player_id:")
        duplicate_ids = df[df['player_id'].duplicated(keep=False)]['player_id'].unique()[:5]
        for dup_id in duplicate_ids:
            dup_rows = df[df['player_id'] == dup_id][['full_name', 'player_id', 'db_yt_transfer_date']]
            print(f"   Player ID {dup_id}:")
            print(dup_rows.to_string(index=False))
            print()
    
    print(f"\n🔧 Removing duplicates...")
    
    # Convert transfer_date to datetime for comparison
    df['db_yt_transfer_date_clean'] = pd.to_datetime(df['db_yt_transfer_date'], errors='coerce')
    
    # Sort by player_id and transfer_date (most recent first)
    df_sorted = df.sort_values(['player_id', 'db_yt_transfer_date_clean'], 
                              ascending=[True, False], na_position='last')
    
    # Remove duplicates, keeping the first (most recent transfer_date)
    df_deduplicated = df_sorted.drop_duplicates(subset=['player_id'], keep='first')
    
    # Remove the temporary column
    df_deduplicated = df_deduplicated.drop('db_yt_transfer_date_clean', axis=1)
    
    removed_count = len(df) - len(df_deduplicated)
    print(f"   ✅ Removed {removed_count} duplicate players")
    print(f"   ✅ Kept {len(df_deduplicated)} unique players")
    
    # Verify no duplicates remain
    remaining_duplicates = df_deduplicated['player_id'].duplicated().sum()
    print(f"   ✅ Remaining duplicates by player_id: {remaining_duplicates}")
    
    # Show statistics
    print(f"\n📊 Statistics after deduplication:")
    print(f"   Original players: {len(df)}")
    print(f"   Unique players: {len(df_deduplicated)}")
    print(f"   Duplicates removed: {removed_count}")
    print(f"   Reduction: {removed_count/len(df)*100:.1f}%")
    
    # Show some examples of what was kept
    print(f"\n📋 Examples of kept records (most recent transfer_date):")
    sample_kept = df_deduplicated[['full_name', 'player_id', 'db_yt_transfer_date', 'youth_club']].head(10)
    print(sample_kept.to_string(index=False))
    
    # Show distribution of transfer dates
    print(f"\n📊 Distribution of transfer dates:")
    transfer_dates = df_deduplicated['db_yt_transfer_date'].notna().sum()
    print(f"   Players with transfer dates: {transfer_dates}")
    print(f"   Players without transfer dates: {len(df_deduplicated) - transfer_dates}")
    
    # Save the deduplicated dataset
    output_file = 'merged_players_databases_cleaned.csv'
    df_deduplicated.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved deduplicated dataset to: {output_file}")
    print(f"📊 Total unique players: {len(df_deduplicated)}")
    
    return df_deduplicated

def main():
    """Main function"""
    try:
        deduplicated_df = remove_duplicate_players()
        
        if deduplicated_df is not None:
            print(f"\n🎉 Successfully removed duplicates!")
            print(f"📁 Output file: merged_players_databases_cleaned.csv")
            print(f"📊 Total unique players: {len(deduplicated_df)}")
        else:
            print(f"\n❌ Failed to remove duplicates")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
