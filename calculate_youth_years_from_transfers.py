#!/usr/bin/env python3
"""
Calculate Youth Years from Transfers - Use dev 2.db Transfer table to calculate
how many years a player could have spent in their youth club
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
        return None

def calculate_youth_years_from_transfers():
    """Calculate youth years from transfer data for players without year_in_the_club_numeric"""
    print("🔄 Loading final database...")
    
    # Load the final database
    df_final = pd.read_csv('all_players_combined_database_final_cleaned_youth_clubs.csv')
    print(f"   ✅ Loaded {len(df_final)} records from final database")
    
    # Identify players without year_in_the_club_numeric
    players_without_years = df_final[
        (df_final['youth_club'].notna()) & 
        (df_final['year_in_the_club_numeric'].isna())
    ]
    
    print(f"   📊 Players with youth_club but no year_in_the_club_numeric: {len(players_without_years)}")
    
    # Get unique player URLs
    unique_urls = players_without_years['profile_url'].dropna().unique()
    print(f"   📊 Unique URLs to analyze: {len(unique_urls)}")
    
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
        
        # Get transfer data for matched players
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
            
            # Process transfers to calculate youth years
            print("🔧 Processing transfers to calculate youth years...")
            
            youth_years_data = {}
            
            current_player_id = None
            current_player_dob = None
            current_player_youth_club = None
            current_player_transfers = []
            
            for transfer in transfer_results:
                player_id, transfer_date, from_club, to_club, from_club_name, to_club_name = transfer
                
                if player_id != current_player_id:
                    # Process previous player
                    if current_player_id and current_player_dob and current_player_youth_club:
                        years_in_youth = calculate_years_in_youth_club(
                            current_player_dob, 
                            current_player_youth_club, 
                            current_player_transfers
                        )
                        
                        if years_in_youth is not None:
                            # Find the URL for this player
                            player_url = None
                            for url, data in url_to_player_data.items():
                                if data['player_id'] == current_player_id:
                                    player_url = url
                                    break
                            
                            if player_url:
                                youth_years_data[player_url] = {
                                    'calculated_years': years_in_youth,
                                    'youth_club': current_player_youth_club
                                }
                    
                    # Start new player
                    current_player_id = player_id
                    current_player_transfers = []
                    
                    # Get player's birth date and youth club
                    for data in url_to_player_data.values():
                        if data['player_id'] == player_id:
                            current_player_dob = data['date_of_birth']
                            # Get youth club from our database
                            player_records = players_without_years[
                                players_without_years['profile_url'].isin([
                                    url for url, data in url_to_player_data.items() 
                                    if data['player_id'] == player_id
                                ])
                            ]
                            if len(player_records) > 0:
                                current_player_youth_club = player_records.iloc[0]['youth_club']
                            break
                
                # Add transfer to current player
                current_player_transfers.append({
                    'transfer_date': transfer_date,
                    'from_club': from_club_name,
                    'to_club': to_club_name
                })
            
            # Don't forget the last player
            if current_player_id and current_player_dob and current_player_youth_club:
                years_in_youth = calculate_years_in_youth_club(
                    current_player_dob, 
                    current_player_youth_club, 
                    current_player_transfers
                )
                
                if years_in_youth is not None:
                    player_url = None
                    for url, data in url_to_player_data.items():
                        if data['player_id'] == current_player_id:
                            player_url = url
                            break
                    
                    if player_url:
                        youth_years_data[player_url] = {
                            'calculated_years': years_in_youth,
                            'youth_club': current_player_youth_club
                        }
            
            print(f"   ✅ Calculated youth years for {len(youth_years_data)} players")
            
            # Show examples
            if len(youth_years_data) > 0:
                print(f"\n📋 EXAMPLES OF CALCULATED YOUTH YEARS:")
                examples = list(youth_years_data.items())[:10]
                for url, data in examples:
                    print(f"   {url}: {data['youth_club']} - {data['calculated_years']} years")
        
        conn.close()
        
        # Apply calculated years to the final database
        print(f"\n🔧 Applying calculated youth years to final database...")
        
        # Create a copy to work with
        df_updated = df_final.copy()
        
        # Apply calculated years
        updated_count = 0
        
        for idx, row in df_updated.iterrows():
            profile_url = row['profile_url']
            
            if pd.notna(profile_url) and profile_url in youth_years_data:
                calculated_data = youth_years_data[profile_url]
                
                # Update year_in_the_club_numeric
                df_updated.at[idx, 'year_in_the_club_numeric'] = calculated_data['calculated_years']
                
                # Also update from_to if it's empty
                if pd.isna(row['from_to']):
                    df_updated.at[idx, 'from_to'] = f"Calculated: {calculated_data['calculated_years']} years"
                
                updated_count += 1
        
        print(f"   ✅ Updated {updated_count} players with calculated youth years")
        
        # Statistics after update
        print(f"\n📊 FINAL STATISTICS:")
        
        youth_club_count = df_updated['youth_club'].notna().sum()
        year_count = df_updated['year_in_the_club_numeric'].notna().sum()
        coverage = (year_count / youth_club_count) * 100 if youth_club_count > 0 else 0
        
        print(f"   Records with youth_club data: {youth_club_count}")
        print(f"   Records with year_in_the_club_numeric: {year_count}")
        print(f"   Coverage: {coverage:.1f}%")
        
        # Show examples of updated data
        print(f"\n📋 EXAMPLES OF UPDATED DATA:")
        updated_examples = df_updated[
            df_updated['year_in_the_club_numeric'].notna() & 
            df_updated['from_to'].str.contains('Calculated', na=False)
        ][
            ['full_name', 'youth_club', 'year_in_the_club_numeric', 'from_to']
        ].head(10)
        
        for _, row in updated_examples.iterrows():
            print(f"   • {row['full_name']}: {row['youth_club']} - {row['year_in_the_club_numeric']} years ({row['from_to']})")
        
        # Save the updated database
        output_file = 'all_players_combined_database_with_calculated_youth_years.csv'
        df_updated.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved updated database to: {output_file}")
        print(f"📊 Total records: {len(df_updated)}")
        print(f"📊 Records with youth years: {year_count}")
        
        return df_updated
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_years_in_youth_club(date_of_birth, youth_club_name, transfers):
    """Calculate years a player spent in their youth club based on transfer data"""
    if not transfers or not youth_club_name:
        return None
    
    try:
        # Find transfers involving the youth club
        youth_club_transfers = []
        
        for transfer in transfers:
            if (transfer['from_club'] and youth_club_name.lower() in transfer['from_club'].lower()) or \
               (transfer['to_club'] and youth_club_name.lower() in transfer['to_club'].lower()):
                youth_club_transfers.append(transfer)
        
        if not youth_club_transfers:
            return None
        
        # Sort transfers by date
        youth_club_transfers.sort(key=lambda x: x['transfer_date'])
        
        # Calculate age at first and last transfer with youth club
        first_transfer_date = youth_club_transfers[0]['transfer_date']
        last_transfer_date = youth_club_transfers[-1]['transfer_date']
        
        age_at_first = calculate_age_at_date(date_of_birth, first_transfer_date)
        age_at_last = calculate_age_at_date(date_of_birth, last_transfer_date)
        
        if age_at_first is None or age_at_last is None:
            return None
        
        # Estimate years in youth club
        # If player was very young (under 12) at first transfer, assume they started earlier
        if age_at_first <= 12:
            estimated_years = age_at_last - age_at_first + 2  # Add 2 years for very young start
        elif age_at_first <= 16:
            estimated_years = age_at_last - age_at_first + 1  # Add 1 year for young start
        else:
            estimated_years = age_at_last - age_at_first
        
        # Ensure reasonable bounds
        estimated_years = max(1, min(estimated_years, 15))  # Between 1 and 15 years
        
        return int(estimated_years)
        
    except Exception as e:
        print(f"   ⚠️  Error calculating years for {youth_club_name}: {e}")
        return None

def main():
    """Main function"""
    print("🚀 Starting youth years calculation from transfers...")
    
    try:
        updated_df = calculate_youth_years_from_transfers()
        
        if updated_df is not None:
            print(f"\n🎉 Successfully calculated youth years from transfers!")
            print(f"📁 Output file: all_players_combined_database_with_calculated_youth_years.csv")
        else:
            print(f"\n❌ Failed to calculate youth years")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
