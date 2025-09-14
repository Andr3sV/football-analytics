#!/usr/bin/env python3
"""
Update Date of Birth - Update date_of_birth column in all_players_combined_database.csv
using player_date_of_birth from dev 2.db with the specified logic
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

def update_date_of_birth():
    """Update date_of_birth column using player_date_of_birth from dev 2.db"""
    print("🔄 Loading combined database...")
    
    # Load the combined database
    df_combined = pd.read_csv('all_players_combined_database.csv')
    print(f"   ✅ Loaded {len(df_combined)} players from combined database")
    
    # Extract player IDs
    df_combined['player_id'] = df_combined['profile_url'].apply(extract_player_id_from_url)
    player_ids = df_combined['player_id'].dropna().astype(int).tolist()
    
    print(f"   📊 Player IDs to check: {len(player_ids)}")
    
    # Analyze current date_of_birth data
    current_dob_count = df_combined['date_of_birth'].notna().sum()
    print(f"   📊 Current players with date_of_birth: {current_dob_count}")
    
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        print("🔍 Extracting player_date_of_birth from Player table...")
        
        # Query to get player_date_of_birth data
        query = """
        SELECT 
            id,
            date_of_birth
        FROM Player 
        WHERE id IN ({})
        """.format(','.join(['?' for _ in player_ids]))
        
        cursor.execute(query, player_ids)
        results = cursor.fetchall()
        
        print(f"   📊 Found {len(results)} players in Player table")
        
        # Process results and convert timestamps to readable dates
        player_dob_data = {}
        for row in results:
            player_id, date_of_birth = row
            
            # Convert timestamp to readable date
            dob_readable = None
            if date_of_birth:
                try:
                    dob_readable = datetime.fromtimestamp(date_of_birth / 1000).strftime('%Y-%m-%d')
                except:
                    dob_readable = None
            
            player_dob_data[player_id] = dob_readable
        
        print(f"   ✅ Processed {len(player_dob_data)} players with date_of_birth data")
        
        # Apply the update logic
        print("🔧 Applying date_of_birth update logic...")
        
        updates_made = 0
        updates_from_player_table = 0
        updates_kept_original = 0
        
        for idx, row in df_combined.iterrows():
            player_id = row['player_id']
            current_dob = row['date_of_birth']
            
            # Skip if no player_id
            if pd.isna(player_id):
                continue
            
            player_id = int(player_id)
            
            # Get player_date_of_birth from dev 2.db
            player_dob = player_dob_data.get(player_id, None)
            
            # Apply the logic:
            # 1. If player_date_of_birth is empty and date_of_birth has value, keep date_of_birth
            # 2. If date_of_birth has value and player_date_of_birth has value, use player_date_of_birth
            # 3. If both are empty, leave empty
            
            if pd.notna(player_dob):  # player_date_of_birth has value
                if pd.notna(current_dob):  # date_of_birth also has value
                    # Use player_date_of_birth (more recent/accurate)
                    df_combined.at[idx, 'date_of_birth'] = player_dob
                    updates_made += 1
                    updates_from_player_table += 1
                else:  # date_of_birth is empty
                    # Use player_date_of_birth
                    df_combined.at[idx, 'date_of_birth'] = player_dob
                    updates_made += 1
                    updates_from_player_table += 1
            elif pd.notna(current_dob):  # player_date_of_birth is empty, date_of_birth has value
                # Keep current date_of_birth (no change needed)
                updates_kept_original += 1
        
        print(f"   ✅ Update logic applied:")
        print(f"      Total updates made: {updates_made}")
        print(f"      Updated from player table: {updates_from_player_table}")
        print(f"      Kept original values: {updates_kept_original}")
        
        # Analyze results
        final_dob_count = df_combined['date_of_birth'].notna().sum()
        improvement = final_dob_count - current_dob_count
        
        print(f"\n📊 DATE OF BIRTH UPDATE RESULTS:")
        print(f"   Before update: {current_dob_count} players with date_of_birth")
        print(f"   After update: {final_dob_count} players with date_of_birth")
        print(f"   Improvement: +{improvement} players")
        print(f"   Coverage: {final_dob_count}/{len(df_combined)} ({final_dob_count/len(df_combined)*100:.1f}%)")
        
        # Show examples of updated players
        print(f"\n📋 EXAMPLES OF UPDATED PLAYERS:")
        
        # Find players that were updated
        updated_players = df_combined[df_combined['date_of_birth'].notna()][
            ['full_name', 'team_name', 'competition', 'date_of_birth', 'player_id']
        ].head(10)
        
        for _, row in updated_players.iterrows():
            print(f"   • {row['full_name']} ({row['team_name']}, {row['competition']}) - "
                  f"DOB: {row['date_of_birth']}, ID: {row['player_id']}")
        
        # Show age distribution for players with date_of_birth
        print(f"\n📊 AGE DISTRIBUTION (players with date_of_birth):")
        try:
            # Calculate ages from date_of_birth
            current_year = datetime.now().year
            ages = []
            
            for dob in df_combined['date_of_birth'].dropna():
                if pd.notna(dob) and str(dob) != 'nan':
                    try:
                        # Parse date in format YYYY-MM-DD
                        dob_date = datetime.strptime(str(dob), '%Y-%m-%d')
                        age = current_year - dob_date.year
                        ages.append(age)
                    except:
                        continue
            
            if ages:
                ages_df = pd.DataFrame({'age': ages})
                age_stats = ages_df['age'].describe()
                print(f"   Average age: {age_stats['mean']:.1f} years")
                print(f"   Youngest: {age_stats['min']:.0f} years")
                print(f"   Oldest: {age_stats['max']:.0f} years")
                print(f"   Median: {age_stats['50%']:.1f} years")
        
        except Exception as e:
            print(f"   Could not calculate age distribution: {e}")
        
        conn.close()
        
        # Save the updated database
        output_file = 'all_players_combined_database_updated_dob.csv'
        df_combined.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved updated database to: {output_file}")
        print(f"📊 Total players: {len(df_combined)}")
        print(f"📊 Players with date_of_birth: {final_dob_count}")
        
        return df_combined
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting date_of_birth update...")
    
    try:
        updated_df = update_date_of_birth()
        
        if updated_df is not None:
            print(f"\n🎉 Successfully updated date_of_birth data!")
            print(f"📁 Output file: all_players_combined_database_updated_dob.csv")
        else:
            print(f"\n❌ Failed to update date_of_birth data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
