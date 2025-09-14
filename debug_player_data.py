#!/usr/bin/env python3
"""
Debug Player Data - Check what player data we have in dev 2.db
"""
import sqlite3
import pandas as pd

def debug_player_data():
    """Debug player data in dev 2.db"""
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Check Player table structure
        print("🔍 Exploring Player table schema...")
        cursor.execute("PRAGMA table_info(Player)")
        columns = cursor.fetchall()
        
        print(f"\n📋 PLAYER TABLE COLUMNS:")
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM Player")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total records in Player table: {count:,}")
        
        # Check sample data
        print(f"\n🔍 Sample data from Player table:")
        cursor.execute("SELECT * FROM Player LIMIT 5")
        sample_data = cursor.fetchall()
        
        if sample_data:
            print(f"   📊 Found {len(sample_data)} sample records")
            for i, row in enumerate(sample_data):
                print(f"   Record {i+1}: {row}")
        
        # Check date_of_birth column specifically
        print(f"\n🔍 Checking date_of_birth column...")
        cursor.execute("SELECT COUNT(*) FROM Player WHERE date_of_birth IS NOT NULL")
        dob_count = cursor.fetchone()[0]
        print(f"   Players with date_of_birth: {dob_count:,}")
        
        # Sample date_of_birth data
        cursor.execute("SELECT id, date_of_birth FROM Player WHERE date_of_birth IS NOT NULL LIMIT 10")
        dob_samples = cursor.fetchall()
        print(f"   Sample date_of_birth values:")
        for player_id, dob in dob_samples:
            print(f"     Player {player_id}: {dob}")
        
        # Check our main database player IDs
        print(f"\n🔍 Checking our main database player IDs...")
        df_main = pd.read_csv('all_players_combined_database_expanded_youth_clubs_cleaned.csv')
        
        # Extract player IDs from our database
        import re
        def extract_player_id_from_url(profile_url):
            if pd.isna(profile_url):
                return None
            url_str = str(profile_url)
            match = re.search(r'/spieler/(\d+)', url_str)
            if match:
                return int(match.group(1))
            return None
        
        df_main['player_id'] = df_main['profile_url'].apply(extract_player_id_from_url)
        our_player_ids = df_main['player_id'].dropna().unique()
        
        print(f"   Our database has {len(our_player_ids)} unique player IDs")
        print(f"   Sample IDs: {our_player_ids[:10].tolist()}")
        
        # Check how many of our players exist in dev 2.db Player table
        sample_ids = our_player_ids[:100].tolist()
        placeholders = ','.join(['?' for _ in sample_ids])
        cursor.execute(f"SELECT COUNT(*) FROM Player WHERE id IN ({placeholders})", sample_ids)
        matches = cursor.fetchone()[0]
        print(f"   Matches in dev 2.db (first 100 IDs): {matches}")
        
        # Check for players without youth clubs
        players_without_youth_clubs = df_main[
            df_main['youth_club'].isna() | (df_main['youth_club'] == '')
        ]['player_id'].dropna().unique()
        
        print(f"   Players without youth clubs: {len(players_without_youth_clubs)}")
        print(f"   Sample IDs without youth clubs: {players_without_youth_clubs[:10].tolist()}")
        
        # Check if these specific players exist in dev 2.db
        sample_no_youth_ids = players_without_youth_clubs[:50].tolist()
        placeholders = ','.join(['?' for _ in sample_no_youth_ids])
        cursor.execute(f"SELECT COUNT(*) FROM Player WHERE id IN ({placeholders})", sample_no_youth_ids)
        no_youth_matches = cursor.fetchone()[0]
        print(f"   Players without youth clubs that exist in dev 2.db (first 50): {no_youth_matches}")
        
        # Check their date_of_birth
        cursor.execute(f"""
            SELECT id, date_of_birth 
            FROM Player 
            WHERE id IN ({placeholders}) AND date_of_birth IS NOT NULL
            LIMIT 10
        """, sample_no_youth_ids)
        dob_for_no_youth = cursor.fetchall()
        print(f"   Players without youth clubs with date_of_birth:")
        for player_id, dob in dob_for_no_youth:
            print(f"     Player {player_id}: {dob}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🚀 Debugging player data...")
    debug_player_data()

if __name__ == "__main__":
    main()
