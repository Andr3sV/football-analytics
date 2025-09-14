#!/usr/bin/env python3
"""
Identify Youth Clubs from Transfers - Use dev 2.db Transfer table to identify
youth clubs based on transfers before age 23, then update the main database
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
    """Identify youth clubs from transfer data in dev 2.db"""
    print("🔄 Loading main database...")
    
    # Load the main database
    df_main = pd.read_csv('all_players_combined_database_expanded_youth_clubs_cleaned.csv')
    print(f"   ✅ Loaded {len(df_main)} records from main database")
    
    # Extract player IDs
    df_main['player_id'] = df_main['profile_url'].apply(extract_player_id_from_url)
    
    # Identify players without youth club data
    players_without_youth_clubs = df_main[
        df_main['youth_club'].isna() | (df_main['youth_club'] == '')
    ]['player_id'].dropna().unique()
    
    print(f"   📊 Players without youth club data: {len(players_without_youth_clubs)}")
    
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get player birth dates
        print("🔍 Extracting player birth dates...")
        player_dob_query = """
        SELECT id, date_of_birth 
        FROM Player 
        WHERE id IN ({})
        """.format(','.join(['?' for _ in players_without_youth_clubs]))
        
        cursor.execute(player_dob_query, players_without_youth_clubs)
        player_dobs = dict(cursor.fetchall())
        print(f"   ✅ Found birth dates for {len(player_dobs)} players")
        
        # Debug: show some examples
        if len(player_dobs) > 0:
            print(f"   📋 Sample birth dates found:")
            for i, (player_id, dob) in enumerate(list(player_dobs.items())[:5]):
                print(f"     Player {player_id}: {dob}")
        else:
            print(f"   ⚠️  No birth dates found. Checking sample queries...")
            # Try with a smaller sample
            sample_ids = list(players_without_youth_clubs)[:10]
            cursor.execute("SELECT id, date_of_birth FROM Player WHERE id IN ({})".format(','.join(['?' for _ in sample_ids])), sample_ids)
            sample_results = cursor.fetchall()
            print(f"   Sample query results: {sample_results}")
        
        # Get transfer data for these players
        print("🔍 Extracting transfer data...")
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
        """.format(','.join(['?' for _ in players_without_youth_clubs]))
        
        cursor.execute(transfer_query, players_without_youth_clubs)
        transfer_results = cursor.fetchall()
        
        print(f"   📊 Found {len(transfer_results)} transfer records")
        
        # Process transfers to identify youth clubs
        print("🔧 Processing transfers to identify youth clubs...")
        
        youth_clubs_data = []
        players_processed = 0
        
        current_player_id = None
        current_player_youth_clubs = set()
        
        for transfer in transfer_results:
            player_id, transfer_date, from_club, to_club, from_club_name, to_club_name = transfer
            
            if player_id != current_player_id:
                # Save previous player's youth clubs
                if current_player_id and current_player_youth_clubs:
                    for club_name in current_player_youth_clubs:
                        youth_clubs_data.append({
                            'player_id': current_player_id,
                            'youth_club': club_name,
                            'source': 'transfers_under_23'
                        })
                    players_processed += 1
                
                # Start new player
                current_player_id = player_id
                current_player_youth_clubs = set()
            
            # Get player's birth date
            if player_id not in player_dobs:
                continue
                
            dob = player_dobs[player_id]
            age_at_transfer = calculate_age_at_date(dob, transfer_date)
            
            if age_at_transfer is not None and age_at_transfer < 23:
                # Player was under 23, both clubs could be youth clubs
                if from_club_name and from_club_name.strip():
                    current_player_youth_clubs.add(from_club_name.strip())
                if to_club_name and to_club_name.strip():
                    current_player_youth_clubs.add(to_club_name.strip())
        
        # Don't forget the last player
        if current_player_id and current_player_youth_clubs:
            for club_name in current_player_youth_clubs:
                youth_clubs_data.append({
                    'player_id': current_player_id,
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
                print(f"   • Player ID {example['player_id']}: {example['youth_club']}")
        
        conn.close()
        
        # Create dataframe of new youth clubs
        df_new_youth_clubs = pd.DataFrame(youth_clubs_data)
        
        if len(df_new_youth_clubs) > 0:
            print(f"\n🔧 Updating main database with new youth clubs...")
            
            # Create expanded rows for players with multiple youth clubs
            expanded_rows = []
            
            for _, row in df_main.iterrows():
                player_id = row['player_id']
                
                if pd.isna(player_id):
                    expanded_rows.append(row)
                    continue
                
                player_id = int(player_id)
                
                # Check if this player has new youth clubs from transfers
                player_youth_clubs = df_new_youth_clubs[df_new_youth_clubs['player_id'] == player_id]
                
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
    print("🚀 Starting youth clubs identification from transfers...")
    
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
