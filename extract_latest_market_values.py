#!/usr/bin/env python3
"""
Extract Latest Market Values - Extract the most recent market values from Transfer table
for all players in our final merged database
"""
import sqlite3
import pandas as pd
import re
from datetime import datetime

def extract_player_id_from_url(profile_url):
    """Extract player ID from Transfermarkt profile URL"""
    if pd.isna(profile_url):
        return None
    
    url_str = str(profile_url)
    match = re.search(r'/spieler/(\d+)', url_str)
    if match:
        return int(match.group(1))
    return None

def extract_latest_market_values():
    """Extract the latest market values from the Transfer table"""
    print("🔄 Loading final merged database...")
    
    # Load our final database
    df_final = pd.read_csv('merged_players_databases_final.csv')
    print(f"   ✅ Loaded {len(df_final)} players from final database")
    
    # Extract player IDs
    df_final['player_id'] = df_final['profile_url'].apply(extract_player_id_from_url)
    player_ids = df_final['player_id'].dropna().astype(int).tolist()
    
    print(f"   📊 Player IDs to lookup: {len(player_ids)}")
    
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        print("🔍 Extracting latest market values from Transfer table...")
        
        # Query to get the latest market value for each player
        # We'll get the most recent transfer with a market_value for each player
        query = """
        SELECT 
            player_id,
            market_value,
            transfer_date,
            fee,
            from_club,
            to_club
        FROM Transfer 
        WHERE player_id IN ({})
        AND market_value IS NOT NULL
        AND market_value > 0
        ORDER BY player_id, transfer_date DESC
        """.format(','.join(['?' for _ in player_ids]))
        
        cursor.execute(query, player_ids)
        results = cursor.fetchall()
        
        print(f"   📊 Found {len(results)} transfers with market values")
        
        # Process results to get the latest market value per player
        latest_values = {}
        for row in results:
            player_id, market_value, transfer_date, fee, from_club, to_club = row
            
            # Convert timestamp to readable date
            if transfer_date:
                transfer_date_readable = datetime.fromtimestamp(transfer_date / 1000).strftime('%Y-%m-%d')
            else:
                transfer_date_readable = None
            
            # Only keep the latest value for each player
            if player_id not in latest_values:
                latest_values[player_id] = {
                    'player_id': player_id,
                    'latest_market_value': market_value,
                    'latest_transfer_date': transfer_date_readable,
                    'latest_fee': fee,
                    'from_club': from_club,
                    'to_club': to_club
                }
        
        print(f"   ✅ Found latest market values for {len(latest_values)} players")
        
        # Convert to DataFrame
        df_latest_values = pd.DataFrame(list(latest_values.values()))
        
        # Show statistics
        print(f"\n📊 MARKET VALUE STATISTICS:")
        print(f"   Players with latest market values: {len(df_latest_values)}")
        print(f"   Total market value: €{df_latest_values['latest_market_value'].sum():,}")
        print(f"   Average market value: €{df_latest_values['latest_market_value'].mean():,.0f}")
        print(f"   Median market value: €{df_latest_values['latest_market_value'].median():,.0f}")
        print(f"   Max market value: €{df_latest_values['latest_market_value'].max():,}")
        print(f"   Min market value: €{df_latest_values['latest_market_value'].min():,}")
        
        # Show examples
        print(f"\n📋 EXAMPLES OF LATEST MARKET VALUES:")
        examples = df_latest_values.nlargest(10, 'latest_market_value')[
            ['player_id', 'latest_market_value', 'latest_transfer_date', 'latest_fee']
        ]
        for _, row in examples.iterrows():
            print(f"   Player ID: {row['player_id']}, Value: €{row['latest_market_value']:,}, Date: {row['latest_transfer_date']}, Fee: {row['latest_fee']}")
        
        # Save the latest market values
        output_file = 'latest_market_values.csv'
        df_latest_values.to_csv(output_file, index=False)
        print(f"\n💾 Saved latest market values to: {output_file}")
        
        # Now merge with our final database
        print(f"\n🔧 Merging with final database...")
        
        # Merge the market values with our final database
        df_merged = df_final.merge(
            df_latest_values,
            left_on='player_id',
            right_on='player_id',
            how='left',
            suffixes=('', '_db')
        )
        
        # Statistics after merge
        players_with_db_values = df_merged['latest_market_value'].notna().sum()
        players_with_existing_values = df_merged['market_value'].notna().sum()
        
        print(f"   📊 Players with market values from final DB: {players_with_existing_values}")
        print(f"   📊 Players with market values from dev 2.db: {players_with_db_values}")
        
        # Update market values where we have newer data from dev 2.db
        print(f"   🔄 Updating market values with latest data...")
        
        # For players that have both values, keep the one from dev 2.db (more recent)
        mask_update = df_merged['latest_market_value'].notna()
        df_merged.loc[mask_update, 'market_value'] = df_merged.loc[mask_update, 'latest_market_value']
        df_merged.loc[mask_update, 'market_value_source'] = 'dev_2_db_latest'
        
        # For players that only had values in final DB
        mask_keep_existing = df_merged['market_value'].notna() & df_merged['latest_market_value'].isna()
        df_merged.loc[mask_keep_existing, 'market_value_source'] = 'final_db_scraped'
        
        # Final statistics
        final_market_value_count = df_merged['market_value'].notna().sum()
        print(f"   📊 Final players with market values: {final_market_value_count}")
        
        # Save the enhanced final database
        final_output = 'merged_players_databases_with_latest_values.csv'
        df_merged.to_csv(final_output, index=False)
        
        print(f"\n💾 Saved enhanced database to: {final_output}")
        print(f"📊 Total players: {len(df_merged)}")
        print(f"📊 Players with market values: {final_market_value_count}")
        
        conn.close()
        
        return df_merged
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting latest market value extraction from dev 2.db")
    
    try:
        enhanced_df = extract_latest_market_values()
        
        if enhanced_df is not None:
            print(f"\n🎉 Successfully extracted latest market values!")
            print(f"📁 Enhanced database: merged_players_databases_with_latest_values.csv")
            print(f"📁 Latest values only: latest_market_values.csv")
        else:
            print(f"\n❌ Failed to extract market values")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
