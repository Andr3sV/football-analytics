#!/usr/bin/env python3
"""
Identify Youth Clubs from Transfers by URL - Use dev 2.db Transfer table to identify
youth clubs based on transfers before age 23, using URLs to match players
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

def calculate_age_at_date(date_of_birth, transfer_date):
    """Calculate age at a specific date"""
    if pd.isna(date_of_birth) or pd.isna(transfer_date):
        return None
    
    try:
        # Convert date_of_birth from Unix timestamp (milliseconds)
        if isinstance(date_of_birth, (int, float)):
            if date_of_birth > 1e10:  # milliseconds
                dob_timestamp = date_of_birth / 1000
            else:
                dob_timestamp = date_of_birth
            dob = pd.to_datetime(dob_timestamp, unit='s')
        else:
            dob = pd.to_datetime(date_of_birth)
            
        # Convert transfer_date from Unix timestamp (milliseconds)
        if isinstance(transfer_date, (int, float)):
            if transfer_date > 1e10:  # milliseconds
                transfer_timestamp = transfer_date / 1000
            else:
                transfer_timestamp = transfer_date
            transfer_dt = pd.to_datetime(transfer_timestamp, unit='s')
        else:
            transfer_dt = pd.to_datetime(transfer_date)
        
        # Calculate age
        age = transfer_dt.year - dob.year
        if transfer_dt.month < dob.month or (transfer_dt.month == dob.month and transfer_dt.day < dob.day):
            age -= 1
            
        return age
    except Exception as e:
        print(f"   ⚠️  Error calculating age: {e}")
        return None

def identify_youth_clubs_from_transfers():
    """Identify youth clubs from transfer data in dev 2.db using URLs"""
    print("🔄 Loading main database...")
    
    # Load the main database
    df_main = pd.read_csv('all_players_combined_database_expanded_youth_clubs_cleaned.csv')
    print(f"   ✅ Loaded {len(df_main)} records from main database")
    
    # Identify players without youth club data
    players_without_youth_clubs = df_main[
        df_main['youth_club'].isna() | (df_main['youth_club'] == '')
    ]
    
    print(f"   📊 Players without youth club data: {len(players_without_youth_clubs)}")
    
    # Get unique URLs from players without youth clubs
    unique_urls = players_without_youth_clubs['profile_url'].dropna().unique()
    print(f"   📊 Unique URLs to check: {len(unique_urls)}")
    
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get player data from dev 2.db using URLs
        print("🔍 Extracting player data from dev 2.db using URLs...")
        
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
        
        # Show examples
        if len(url_to_player_data) > 0:
            print(f"   📋 Sample player data found:")
            for i, (url, data) in enumerate(list(url_to_player_data.items())[:5]):
                print(f"     {url}: ID {data['player_id']}, {data['name']}, DOB: {data['date_of_birth']}")
        
        # Get transfer data for matched players
        if len(url_to_player_data) > 0:
            print("🔍 Extracting transfer data...")
            
            matched_player_ids = [data['player_id'] for data in url_to_player_data.values()]
            transfer_query = """
            SELECT 
                t.player_id,
                t.transfer_date,
                t.from_club,
                t.to_club,
                c1.name as from_club_name,
                c2.name as to_club_name
            FROM Transfer t
            LEFT JOIN Club c1 ON t.from_club = c1.id
            LEFT JOIN Club c2 ON t.to_club = c2.id
            WHERE t.player_id IN ({})
            ORDER BY t.player_id, t.transfer_date
            """.format(','.join(['?' for _ in matched_player_ids]))
            
            cursor.execute(transfer_query, matched_player_ids)
            transfer_results = cursor.fetchall()
            
            print(f"   📊 Found {len(transfer_results)} transfer records")
            
            # Process transfers to identify youth clubs
            print("🔧 Processing transfers to identify youth clubs...")
            
            youth_clubs_data = []
            players_processed = 0
            
            current_player_id = None
            current_player_youth_clubs = set()
            current_player_dob = None
            
            for transfer in transfer_results:
                player_id, transfer_date, from_club, to_club, from_club_name, to_club_name = transfer
                
                if player_id != current_player_id:
                    # Save previous player's youth clubs
                    if current_player_id and current_player_youth_clubs:
                        # Find the URL for this player
                        player_url = None
                        for url, data in url_to_player_data.items():
                            if data['player_id'] == current_player_id:
                                player_url = url
                                break
                        
                        if player_url:
                            for club_name in current_player_youth_clubs:
                                youth_clubs_data.append({
                                    'profile_url': player_url,
                                    'youth_club': club_name,
                                    'source': 'transfers_under_23'
                                })
                        players_processed += 1
                    
                    # Start new player
                    current_player_id = player_id
                    current_player_youth_clubs = set()
                    
                    # Get player's birth date
                    for data in url_to_player_data.values():
                        if data['player_id'] == player_id:
                            current_player_dob = data['date_of_birth']
                            break
                
                # Calculate age at transfer
                if current_player_dob:
                    age_at_transfer = calculate_age_at_date(current_player_dob, transfer_date)
                    
                    if age_at_transfer is not None and age_at_transfer < 23:
                        # Player was under 23, both clubs could be youth clubs
                        if from_club_name and from_club_name.strip():
                            current_player_youth_clubs.add(from_club_name.strip())
                        if to_club_name and to_club_name.strip():
                            current_player_youth_clubs.add(to_club_name.strip())
            
            # Don't forget the last player
            if current_player_id and current_player_youth_clubs:
                player_url = None
                for url, data in url_to_player_data.items():
                    if data['player_id'] == current_player_id:
                        player_url = url
                        break
                
                if player_url:
                    for club_name in current_player_youth_clubs:
                        youth_clubs_data.append({
                            'profile_url': player_url,
                            'youth_club': club_name,
                            'source': 'transfers_under_23'
                        })
                players_processed += 1
            
            print(f"   ✅ Processed {players_processed} players")
            print(f"   📊 Found {len(youth_clubs_data)} youth club records from transfers")
            
            # Show examples
            if youth_clubs_data:
                print(f"\n📋 EXAMPLES OF YOUTH CLUBS IDENTIFIED FROM TRANSFERS:")
                examples = youth_clubs_data[:10]
                for example in examples:
                    print(f"   • {example['profile_url']}: {example['youth_club']}")
        
        conn.close()
        
        # Create dataframe of new youth clubs
        if len(youth_clubs_data) > 0:
            df_new_youth_clubs = pd.DataFrame(youth_clubs_data)
            
            print(f"\n🔧 Updating main database with new youth clubs...")
            
            # Create expanded rows for players with multiple youth clubs
            expanded_rows = []
            
            for _, row in df_main.iterrows():
                profile_url = row['profile_url']
                
                if pd.isna(profile_url):
                    expanded_rows.append(row)
                    continue
                
                # Check if this player has new youth clubs from transfers
                player_youth_clubs = df_new_youth_clubs[df_new_youth_clubs['profile_url'] == profile_url]
                
                if len(player_youth_clubs) > 0:
                    # Player has new youth clubs - create multiple rows
                    for _, youth_club_row in player_youth_clubs.iterrows():
                        new_row = row.copy()
                        new_row['youth_club'] = youth_club_row['youth_club']
                        new_row['from_to'] = None  # We don't have date ranges for transfers
                        new_row['year_in_the_club_numeric'] = None
                        expanded_rows.append(new_row)
                else:
                    # Keep existing row
                    expanded_rows.append(row)
            
            # Create updated dataframe
            df_updated = pd.DataFrame(expanded_rows)
            
            # Statistics
            original_count = len(df_main)
            updated_count = len(df_updated)
            new_rows = updated_count - original_count
            
            print(f"   ✅ Database updated:")
            print(f"      Original rows: {original_count}")
            print(f"      New rows added: {new_rows}")
            print(f"      Final rows: {updated_count}")
            
            # Show coverage statistics
            youth_club_coverage = df_updated['youth_club'].notna().sum()
            print(f"   📊 Youth club coverage: {youth_club_coverage}/{updated_count} ({youth_club_coverage/updated_count*100:.1f}%)")
            
            # Save updated database
            output_file = 'all_players_combined_database_with_transfer_youth_clubs.csv'
            df_updated.to_csv(output_file, index=False)
            
            print(f"\n💾 Saved updated database to: {output_file}")
            print(f"📊 Total rows: {len(df_updated)}")
            print(f"📊 Players with youth club data: {youth_club_coverage}")
            
            return df_updated
        
        else:
            print(f"\n⚠️  No youth clubs found from transfer data")
            return df_main
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting youth clubs identification from transfers using URLs...")
    
    try:
        updated_df = identify_youth_clubs_from_transfers()
        
        if updated_df is not None:
            print(f"\n🎉 Successfully updated database with youth clubs from transfers!")
            print(f"📁 Output file: all_players_combined_database_with_transfer_youth_clubs.csv")
        else:
            print(f"\n❌ Failed to update database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
