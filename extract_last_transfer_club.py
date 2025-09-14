#!/usr/bin/env python3
"""
Extract Last Transfer Club - Extract the last club each player was transferred to
from the Transfer table in dev 2.db
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

def extract_last_transfer_clubs():
    """Extract the last transfer club for each player"""
    print("🔄 Loading final database with fixed values...")
    
    # Load our final database
    df_final = pd.read_csv('merged_players_databases_fixed_values.csv')
    print(f"   ✅ Loaded {len(df_final)} players from final database")
    
    # Extract player IDs
    df_final['player_id'] = df_final['profile_url'].apply(extract_player_id_from_url)
    player_ids = df_final['player_id'].dropna().astype(int).tolist()
    
    print(f"   📊 Player IDs to lookup: {len(player_ids)}")
    
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        print("🔍 Extracting last transfer clubs from Transfer table...")
        
        # Query to get the most recent transfer for each player
        # We'll get the latest transfer (by transfer_date) for each player
        query = """
        SELECT 
            t.player_id,
            t.to_club,
            t.transfer_date,
            t.fee,
            c.name as club_name,
            c.country as club_country,
            c.league_name as club_league,
            c.league_tier as club_league_tier
        FROM Transfer t
        LEFT JOIN Club c ON t.to_club = c.id
        WHERE t.player_id IN ({})
        AND t.transfer_date IS NOT NULL
        ORDER BY t.player_id, t.transfer_date DESC
        """.format(','.join(['?' for _ in player_ids]))
        
        cursor.execute(query, player_ids)
        results = cursor.fetchall()
        
        print(f"   📊 Found {len(results)} transfers")
        
        # Process results to get the latest transfer per player
        latest_transfers = {}
        for row in results:
            player_id, to_club, transfer_date, fee, club_name, club_country, club_league, club_league_tier = row
            
            # Convert timestamp to readable date
            if transfer_date:
                transfer_date_readable = datetime.fromtimestamp(transfer_date / 1000).strftime('%Y-%m-%d')
            else:
                transfer_date_readable = None
            
            # Only keep the latest transfer for each player
            if player_id not in latest_transfers:
                latest_transfers[player_id] = {
                    'player_id': player_id,
                    'last_transfer_to_club_id': to_club,
                    'last_transfer_date': transfer_date_readable,
                    'last_transfer_fee': fee,
                    'last_transfer_club_name': club_name,
                    'last_transfer_club_country': club_country,
                    'last_transfer_club_league': club_league,
                    'last_transfer_club_league_tier': club_league_tier
                }
        
        print(f"   ✅ Found latest transfers for {len(latest_transfers)} players")
        
        # Convert to DataFrame
        df_latest_transfers = pd.DataFrame(list(latest_transfers.values()))
        
        # Show statistics
        print(f"\n📊 TRANSFER STATISTICS:")
        print(f"   Players with last transfer data: {len(df_latest_transfers)}")
        
        # Analyze transfer fees
        fee_data = df_latest_transfers['last_transfer_fee'].value_counts().head(10)
        print(f"\n📋 Top transfer fee types:")
        for fee_type, count in fee_data.items():
            print(f"   {fee_type}: {count} transfers")
        
        # Analyze countries
        country_data = df_latest_transfers['last_transfer_club_country'].value_counts().head(10)
        print(f"\n📋 Top destination countries:")
        for country, count in country_data.items():
            print(f"   {country}: {count} transfers")
        
        # Analyze leagues
        league_data = df_latest_transfers['last_transfer_club_league'].value_counts().head(10)
        print(f"\n📋 Top destination leagues:")
        for league, count in league_data.items():
            print(f"   {league}: {count} transfers")
        
        # Show examples
        print(f"\n📋 EXAMPLES OF LATEST TRANSFERS:")
        examples = df_latest_transfers.head(10)[
            ['player_id', 'last_transfer_club_name', 'last_transfer_club_country', 
             'last_transfer_club_league', 'last_transfer_fee', 'last_transfer_date']
        ]
        for _, row in examples.iterrows():
            print(f"   Player ID: {row['player_id']}, Club: {row['last_transfer_club_name']}, "
                  f"Country: {row['last_transfer_club_country']}, League: {row['last_transfer_club_league']}, "
                  f"Fee: {row['last_transfer_fee']}, Date: {row['last_transfer_date']}")
        
        # Save the latest transfers data
        output_file = 'last_transfer_clubs.csv'
        df_latest_transfers.to_csv(output_file, index=False)
        print(f"\n💾 Saved last transfer data to: {output_file}")
        
        # Now merge with our final database
        print(f"\n🔧 Merging with final database...")
        
        # Merge the transfer data with our final database
        df_merged = df_final.merge(
            df_latest_transfers,
            left_on='player_id',
            right_on='player_id',
            how='left',
            suffixes=('', '_transfer')
        )
        
        # Statistics after merge
        players_with_transfer_data = df_merged['last_transfer_club_name'].notna().sum()
        
        print(f"   📊 Players with last transfer data: {players_with_transfer_data}")
        
        # Show examples of merged data
        print(f"\n📋 EXAMPLES OF ENRICHED PLAYERS:")
        enriched_examples = df_merged[df_merged['last_transfer_club_name'].notna()][
            ['full_name', 'current_club', 'last_transfer_club_name', 'last_transfer_club_country', 
             'last_transfer_fee', 'last_transfer_date', 'market_value']
        ].head(10)
        for _, row in enriched_examples.iterrows():
            print(f"   {row['full_name']}: {row['current_club']} → {row['last_transfer_club_name']} "
                  f"({row['last_transfer_club_country']}) - {row['last_transfer_fee']} on {row['last_transfer_date']} "
                  f"- Value: {row['market_value']}")
        
        # Save the enhanced final database
        final_output = 'merged_players_databases_with_transfers.csv'
        df_merged.to_csv(final_output, index=False)
        
        print(f"\n💾 Saved enhanced database to: {final_output}")
        print(f"📊 Total players: {len(df_merged)}")
        print(f"📊 Players with transfer data: {players_with_transfer_data}")
        
        # Additional analysis
        print(f"\n📊 ADDITIONAL INSIGHTS:")
        
        # Players who transferred to different clubs than current
        different_club = df_merged[
            (df_merged['current_club'].notna()) & 
            (df_merged['last_transfer_club_name'].notna()) & 
            (df_merged['current_club'] != df_merged['last_transfer_club_name'])
        ]
        print(f"   Players who transferred to different clubs than current: {len(different_club)}")
        
        # Free transfers
        free_transfers = df_merged[df_merged['last_transfer_fee'] == 'free transfer']
        print(f"   Players with free transfers: {len(free_transfers)}")
        
        # Paid transfers
        paid_transfers = df_merged[
            (df_merged['last_transfer_fee'].notna()) & 
            (df_merged['last_transfer_fee'] != 'free transfer') & 
            (df_merged['last_transfer_fee'] != 'loan transfer')
        ]
        print(f"   Players with paid transfers: {len(paid_transfers)}")
        
        conn.close()
        
        return df_merged
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting last transfer club extraction from dev 2.db")
    
    try:
        enhanced_df = extract_last_transfer_clubs()
        
        if enhanced_df is not None:
            print(f"\n🎉 Successfully extracted last transfer clubs!")
            print(f"📁 Enhanced database: merged_players_databases_with_transfers.csv")
            print(f"📁 Transfer data only: last_transfer_clubs.csv")
        else:
            print(f"\n❌ Failed to extract transfer data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
