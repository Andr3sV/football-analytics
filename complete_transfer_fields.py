#!/usr/bin/env python3
"""
Complete Transfer Fields - Map and fill missing transfer fields using dev 2.db
"""
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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

def complete_transfer_fields():
    """Complete missing transfer fields using dev 2.db"""
    print("🔄 Loading final database...")
    
    # Load the final database
    df_final = pd.read_csv('all_players_combined_database_with_transfer_youth_clubs_restored.csv')
    print(f"   ✅ Loaded final database: {len(df_final)} records")
    
    # Define the transfer fields we need to complete
    transfer_fields = [
        'latest_transfer_date',
        'latest_fee', 
        'from_club',
        'to_club',
        'market_value_source',
        'last_transfer_to_club_id',
        'last_transfer_date',
        'last_transfer_fee',
        'last_transfer_club_name',
        'last_transfer_club_country',
        'last_transfer_club_league',
        'last_transfer_club_league_tier'
    ]
    
    print(f"\n🔍 Checking current status of transfer fields...")
    
    # Check which fields are missing data
    missing_fields = {}
    for field in transfer_fields:
        if field in df_final.columns:
            missing_count = df_final[field].isna().sum()
            missing_fields[field] = missing_count
            print(f"   {field}: {missing_count} missing values")
        else:
            print(f"   {field}: Column not found")
    
    # Get unique player URLs
    unique_urls = df_final['profile_url'].dropna().unique()
    print(f"\n📊 Unique player URLs: {len(unique_urls)}")
    
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get player data from dev 2.db using URLs
        print("🔍 Extracting player data from dev 2.db...")
        
        # Create a mapping of URL to player data
        url_to_player_data = {}
        
        # Process URLs in batches to avoid query size limits
        batch_size = 100
        for i in range(0, len(unique_urls), batch_size):
            batch_urls = unique_urls[i:i+batch_size]
            placeholders = ','.join(['?' for _ in batch_urls])
            
            query = f"""
            SELECT id, url, name, date_of_birth 
            FROM Player 
            WHERE url IN ({placeholders})
            """
            
            cursor.execute(query, batch_urls)
            results = cursor.fetchall()
            
            for player_id, url, name, date_of_birth in results:
                url_to_player_data[url] = {
                    'player_id': player_id,
                    'name': name,
                    'date_of_birth': date_of_birth
                }
        
        print(f"   ✅ Found player data for {len(url_to_player_data)} URLs")
        
        # Get transfer data for all matched players
        if len(url_to_player_data) > 0:
            print("🔍 Extracting transfer data...")
            
            matched_player_ids = [data['player_id'] for data in url_to_player_data.values()]
            
            # Get all transfers for these players
            transfer_query = """
            SELECT 
                t.player_id,
                t.transfer_date,
                t.from_club,
                t.to_club,
                t.fee,
                t.market_value,
                c1.name as from_club_name,
                c1.country as from_club_country,
                c1.league_name as from_club_league,
                c1.league_tier as from_club_league_tier,
                c2.name as to_club_name,
                c2.country as to_club_country,
                c2.league_name as to_club_league,
                c2.league_tier as to_club_league_tier
            FROM Transfer t
            LEFT JOIN Club c1 ON t.from_club = c1.id
            LEFT JOIN Club c2 ON t.to_club = c2.id
            WHERE t.player_id IN ({})
            ORDER BY t.player_id, t.transfer_date DESC
            """.format(','.join(['?' for _ in matched_player_ids]))
            
            cursor.execute(transfer_query, matched_player_ids)
            transfer_results = cursor.fetchall()
            
            print(f"   📊 Found {len(transfer_results)} transfer records")
            
            # Process transfers to create transfer data
            print("🔧 Processing transfers to create transfer data...")
            
            transfer_data = {}
            
            for transfer in transfer_results:
                (player_id, transfer_date, from_club, to_club, fee, market_value,
                 from_club_name, from_club_country, from_club_league, from_club_league_tier,
                 to_club_name, to_club_country, to_club_league, to_club_league_tier) = transfer
                
                if player_id not in transfer_data:
                    transfer_data[player_id] = {
                        'latest_transfer_date': transfer_date,
                        'latest_fee': fee,
                        'from_club': from_club_name,
                        'to_club': to_club_name,
                        'market_value_source': market_value,
                        'last_transfer_to_club_id': to_club,
                        'last_transfer_date': transfer_date,
                        'last_transfer_fee': fee,
                        'last_transfer_club_name': to_club_name,
                        'last_transfer_club_country': to_club_country,
                        'last_transfer_club_league': to_club_league,
                        'last_transfer_club_league_tier': to_club_league_tier
                    }
            
            print(f"   ✅ Processed transfer data for {len(transfer_data)} players")
            
            # Show examples
            if len(transfer_data) > 0:
                print(f"\n📋 EXAMPLES OF TRANSFER DATA:")
                examples = list(transfer_data.items())[:5]
                for player_id, data in examples:
                    print(f"   Player ID {player_id}:")
                    print(f"     Latest transfer: {data['from_club']} → {data['to_club']} ({data['latest_fee']})")
                    print(f"     Last club: {data['last_transfer_club_name']} ({data['last_transfer_club_country']})")
        
        conn.close()
        
        # Apply transfer data to the final database
        print(f"\n🔧 Applying transfer data to final database...")
        
        # Create a copy to work with
        df_updated = df_final.copy()
        
        # Create URL to player ID mapping for our database
        df_updated['player_id'] = df_updated['profile_url'].apply(extract_player_id_from_url)
        
        # Apply transfer data
        updated_count = 0
        
        for idx, row in df_updated.iterrows():
            player_id = row['player_id']
            
            if pd.notna(player_id) and player_id in transfer_data:
                transfer_info = transfer_data[player_id]
                
                # Update all transfer fields
                for field in transfer_fields:
                    if field in df_updated.columns:
                        df_updated.at[idx, field] = transfer_info.get(field, None)
                
                updated_count += 1
        
        print(f"   ✅ Updated {updated_count} players with transfer data")
        
        # Statistics after update
        print(f"\n📊 FINAL STATISTICS:")
        
        for field in transfer_fields:
            if field in df_updated.columns:
                non_null_count = df_updated[field].notna().sum()
                total_count = len(df_updated)
                coverage = (non_null_count / total_count) * 100
                print(f"   {field}: {non_null_count}/{total_count} ({coverage:.1f}%)")
        
        # Show examples of completed data
        print(f"\n📋 EXAMPLES OF COMPLETED TRANSFER DATA:")
        completed_examples = df_updated[
            df_updated['last_transfer_club_name'].notna()
        ][
            ['full_name', 'team_name', 'latest_fee', 'from_club', 'to_club', 
             'last_transfer_club_name', 'last_transfer_club_country', 'last_transfer_club_league']
        ].head(10)
        
        for _, row in completed_examples.iterrows():
            print(f"   • {row['full_name']} ({row['team_name']})")
            print(f"     Latest transfer: {row['from_club']} → {row['to_club']} ({row['latest_fee']})")
            print(f"     Last club: {row['last_transfer_club_name']} ({row['last_transfer_club_country']}, {row['last_transfer_club_league']})")
        
        # Save the updated database
        output_file = 'all_players_combined_database_complete_transfer_fields.csv'
        df_updated.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved completed database to: {output_file}")
        print(f"📊 Total records: {len(df_updated)}")
        
        return df_updated
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting transfer fields completion...")
    
    try:
        completed_df = complete_transfer_fields()
        
        if completed_df is not None:
            print(f"\n🎉 Successfully completed transfer fields!")
            print(f"📁 Output file: all_players_combined_database_complete_transfer_fields.csv")
        else:
            print(f"\n❌ Failed to complete transfer fields")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
