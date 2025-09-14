#!/usr/bin/env python3
"""
Update Missing Market Values - Update latest_market_value for all players 
that don't have it, using the latest market value from dev 2.db Transfer table
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

def update_missing_market_values():
    """Update latest_market_value for players that don't have it"""
    print("🔄 Loading updated combined database...")
    
    # Load the updated combined database
    df_combined = pd.read_csv('all_players_combined_database_updated_dob.csv')
    print(f"   ✅ Loaded {len(df_combined)} players from updated database")
    
    # Extract player IDs
    df_combined['player_id'] = df_combined['profile_url'].apply(extract_player_id_from_url)
    player_ids = df_combined['player_id'].dropna().astype(int).tolist()
    
    print(f"   📊 Player IDs to check: {len(player_ids)}")
    
    # Analyze current market value data
    current_mv_count = df_combined['latest_market_value'].notna().sum()
    print(f"   📊 Current players with latest_market_value: {current_mv_count}")
    
    # Find players without market values
    players_without_mv = df_combined[df_combined['latest_market_value'].isna()]
    player_ids_without_mv = players_without_mv['player_id'].dropna().astype(int).tolist()
    
    print(f"   📊 Players without market values: {len(player_ids_without_mv)}")
    
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        print("🔍 Extracting latest market values from Transfer table...")
        
        # Query to get the latest market value for each player without market value
        query = """
        SELECT 
            player_id,
            market_value,
            transfer_date,
            fee
        FROM Transfer 
        WHERE player_id IN ({})
        AND market_value IS NOT NULL
        AND market_value > 0
        ORDER BY player_id, transfer_date DESC
        """.format(','.join(['?' for _ in player_ids_without_mv]))
        
        cursor.execute(query, player_ids_without_mv)
        results = cursor.fetchall()
        
        print(f"   📊 Found {len(results)} transfers with market values for players without MV")
        
        # Process results to get the latest market value per player
        latest_values = {}
        for row in results:
            player_id, market_value, transfer_date, fee = row
            
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
                    'latest_fee': fee
                }
        
        print(f"   ✅ Found latest market values for {len(latest_values)} players without MV")
        
        # Apply the updates to the dataframe
        print("🔧 Updating missing market values...")
        
        updates_made = 0
        total_value_added = 0
        
        for player_id, data in latest_values.items():
            # Find the row in the dataframe
            mask = df_combined['player_id'] == player_id
            
            if mask.any():
                # Update the latest_market_value
                df_combined.loc[mask, 'latest_market_value'] = data['latest_market_value']
                df_combined.loc[mask, 'latest_transfer_date'] = data['latest_transfer_date']
                df_combined.loc[mask, 'latest_fee'] = data['latest_fee']
                
                updates_made += 1
                total_value_added += data['latest_market_value']
        
        print(f"   ✅ Updated {updates_made} players with market values")
        print(f"   💰 Total value added: €{total_value_added:,.0f}")
        
        # Analyze results
        final_mv_count = df_combined['latest_market_value'].notna().sum()
        improvement = final_mv_count - current_mv_count
        
        print(f"\n📊 MARKET VALUE UPDATE RESULTS:")
        print(f"   Before update: {current_mv_count} players with latest_market_value")
        print(f"   After update: {final_mv_count} players with latest_market_value")
        print(f"   Improvement: +{improvement} players")
        print(f"   Coverage: {final_mv_count}/{len(df_combined)} ({final_mv_count/len(df_combined)*100:.1f}%)")
        
        # Calculate total market value
        total_mv = df_combined['latest_market_value'].sum()
        avg_mv = df_combined['latest_market_value'].mean()
        median_mv = df_combined['latest_market_value'].median()
        
        print(f"\n💰 MARKET VALUE STATISTICS:")
        print(f"   Total market value: €{total_mv:,.0f}")
        print(f"   Average market value: €{avg_mv:,.0f}")
        print(f"   Median market value: €{median_mv:,.0f}")
        
        # Show examples of updated players
        print(f"\n📋 EXAMPLES OF UPDATED PLAYERS:")
        
        # Find players that were updated (had no market value before)
        updated_players = df_combined[
            df_combined['latest_market_value'].notna()
        ][
            ['full_name', 'team_name', 'competition', 'latest_market_value', 'latest_transfer_date', 'latest_fee']
        ].head(10)
        
        for _, row in updated_players.iterrows():
            mv_str = f"€{row['latest_market_value']:,.0f}" if pd.notna(row['latest_market_value']) else "N/A"
            print(f"   • {row['full_name']} ({row['team_name']}, {row['competition']}) - "
                  f"Value: {mv_str}, Date: {row['latest_transfer_date']}, Fee: {row['latest_fee']}")
        
        # Show top players by market value
        print(f"\n🏆 TOP 10 PLAYERS BY MARKET VALUE:")
        top_players = df_combined.nlargest(10, 'latest_market_value')[
            ['full_name', 'team_name', 'competition', 'latest_market_value']
        ]
        
        for i, (_, row) in enumerate(top_players.iterrows(), 1):
            mv_str = f"€{row['latest_market_value']:,.0f}" if pd.notna(row['latest_market_value']) else "N/A"
            print(f"   {i:2d}. {row['full_name']} ({row['team_name']}) - {mv_str}")
        
        # Market value distribution
        print(f"\n📊 MARKET VALUE DISTRIBUTION:")
        if df_combined['latest_market_value'].notna().any():
            # Define value ranges
            ranges = [
                (0, 1000000, "Under €1M"),
                (1000000, 5000000, "€1M - €5M"),
                (5000000, 10000000, "€5M - €10M"),
                (10000000, 25000000, "€10M - €25M"),
                (25000000, 50000000, "€25M - €50M"),
                (50000000, 100000000, "€50M - €100M"),
                (100000000, float('inf'), "Over €100M")
            ]
            
            for min_val, max_val, label in ranges:
                count = df_combined[
                    (df_combined['latest_market_value'] >= min_val) & 
                    (df_combined['latest_market_value'] < max_val)
                ].shape[0]
                percentage = (count / len(df_combined)) * 100
                print(f"   {label}: {count:,} players ({percentage:.1f}%)")
        
        conn.close()
        
        # Save the updated database
        output_file = 'all_players_combined_database_final.csv'
        df_combined.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved final database to: {output_file}")
        print(f"📊 Total players: {len(df_combined)}")
        print(f"📊 Players with market values: {final_mv_count}")
        
        return df_combined
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting missing market values update...")
    
    try:
        updated_df = update_missing_market_values()
        
        if updated_df is not None:
            print(f"\n🎉 Successfully updated missing market values!")
            print(f"📁 Output file: all_players_combined_database_final.csv")
        else:
            print(f"\n❌ Failed to update market values")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
