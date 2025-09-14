#!/usr/bin/env python3
"""
Restore Correct Market Values - Replace latest_market_value in the final database
with the correct values from merged_players_databases_fixed_values.csv
"""
import pandas as pd
import numpy as np

def restore_correct_market_values():
    """Restore correct market values from the fixed values file"""
    print("🔄 Loading files...")
    
    # Load the current final database
    df_final = pd.read_csv('all_players_combined_database_with_transfer_youth_clubs.csv')
    print(f"   ✅ Loaded final database: {len(df_final)} records")
    
    # Load the correct market values file
    df_correct = pd.read_csv('merged_players_databases_fixed_values.csv')
    print(f"   ✅ Loaded correct market values file: {len(df_correct)} records")
    
    # Check columns
    print(f"\n🔍 Checking columns...")
    print(f"   Final database columns with 'market_value': {[col for col in df_final.columns if 'market_value' in col.lower()]}")
    print(f"   Correct values file columns with 'market_value': {[col for col in df_correct.columns if 'market_value' in col.lower()]}")
    
    # Check if we have the right columns
    if 'latest_market_value' not in df_final.columns:
        print(f"   ⚠️  'latest_market_value' not found in final database")
        return None
    
    if 'latest_market_value' not in df_correct.columns:
        print(f"   ⚠️  'latest_market_value' not found in correct values file")
        return None
    
    # Get player IDs for matching
    print(f"\n🔍 Preparing data for matching...")
    
    # Extract player IDs from URLs for both files
    import re
    def extract_player_id_from_url(profile_url):
        if pd.isna(profile_url):
            return None
        url_str = str(profile_url)
        match = re.search(r'/spieler/(\d+)', url_str)
        if match:
            return int(match.group(1))
        return None
    
    df_final['player_id'] = df_final['profile_url'].apply(extract_player_id_from_url)
    df_correct['player_id'] = df_correct['profile_url'].apply(extract_player_id_from_url)
    
    print(f"   Final database player IDs: {df_final['player_id'].notna().sum()}")
    print(f"   Correct values player IDs: {df_correct['player_id'].notna().sum()}")
    
    # Create mapping of correct market values
    print(f"\n🔧 Creating market value mapping...")
    
    # Get unique players with correct market values
    correct_market_values = df_correct[
        df_correct['player_id'].notna() & 
        df_correct['latest_market_value'].notna()
    ][['player_id', 'latest_market_value']].drop_duplicates(subset=['player_id'])
    
    print(f"   Players with correct market values: {len(correct_market_values)}")
    
    # Show examples of correct values
    print(f"\n📋 EXAMPLES OF CORRECT MARKET VALUES:")
    examples = correct_market_values.head(10)
    for _, row in examples.iterrows():
        market_val = row['latest_market_value']
        try:
            if pd.isna(market_val):
                market_str = "N/A"
            else:
                market_str = f"€{float(market_val):,.0f}"
        except:
            market_str = str(market_val)
        print(f"   Player ID {row['player_id']}: {market_str}")
    
    # Create mapping dictionary
    correct_values_dict = dict(zip(correct_market_values['player_id'], correct_market_values['latest_market_value']))
    
    # Apply corrections
    print(f"\n🔧 Restoring correct market values...")
    
    # Count how many will be updated
    players_to_update = df_final[
        df_final['player_id'].notna() & 
        df_final['player_id'].isin(correct_values_dict.keys())
    ]
    
    print(f"   Players to be updated: {len(players_to_update)}")
    
    # Apply the corrections
    df_final['latest_market_value_restored'] = df_final['latest_market_value'].copy()
    
    for idx, row in df_final.iterrows():
        player_id = row['player_id']
        if pd.notna(player_id) and player_id in correct_values_dict:
            df_final.at[idx, 'latest_market_value_restored'] = correct_values_dict[player_id]
    
    # Replace the original column
    df_final['latest_market_value'] = df_final['latest_market_value_restored']
    df_final = df_final.drop('latest_market_value_restored', axis=1)
    
    # Statistics
    print(f"\n📊 RESTORATION STATISTICS:")
    
    # Count non-null market values
    final_market_values = df_final['latest_market_value'].notna().sum()
    print(f"   Records with latest_market_value: {final_market_values}")
    
    # Show examples of restored values
    print(f"\n📋 EXAMPLES OF RESTORED MARKET VALUES:")
    restored_examples = df_final[
        df_final['player_id'].notna() & 
        df_final['latest_market_value'].notna()
    ][['full_name', 'team_name', 'latest_market_value', 'player_id']].head(10)
    
    for _, row in restored_examples.iterrows():
        market_val = row['latest_market_value']
        try:
            if pd.isna(market_val):
                market_str = "N/A"
            else:
                market_str = f"€{float(market_val):,.0f}"
        except:
            market_str = str(market_val)
        print(f"   {row['full_name']} ({row['team_name']}): {market_str}")
    
    # Save the corrected database
    output_file = 'all_players_combined_database_with_transfer_youth_clubs_restored.csv'
    df_final.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved corrected database to: {output_file}")
    print(f"📊 Total records: {len(df_final)}")
    print(f"📊 Records with market values: {final_market_values}")
    
    return df_final

def main():
    """Main function"""
    print("🚀 Starting market values restoration...")
    
    try:
        restored_df = restore_correct_market_values()
        
        if restored_df is not None:
            print(f"\n🎉 Successfully restored correct market values!")
            print(f"📁 Output file: all_players_combined_database_with_transfer_youth_clubs_restored.csv")
        else:
            print(f"\n❌ Failed to restore market values")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
