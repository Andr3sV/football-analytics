#!/usr/bin/env python3
"""
Compare Player IDs - Compare player ID ranges between our database and dev 2.db
"""
import sqlite3
import pandas as pd
import numpy as np

def compare_player_ids():
    """Compare player ID ranges between databases"""
    try:
        print("🔍 Loading our main database...")
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
        
        print(f"   Our database player IDs:")
        print(f"     Count: {len(our_player_ids)}")
        print(f"     Min: {our_player_ids.min()}")
        print(f"     Max: {our_player_ids.max()}")
        print(f"     Sample: {sorted(our_player_ids)[:20]}")
        
        # Connect to dev 2.db
        print("\n🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get Player table ID ranges
        cursor.execute("SELECT MIN(id), MAX(id), COUNT(*) FROM Player")
        min_id, max_id, count = cursor.fetchone()
        
        print(f"   Dev 2.db Player table:")
        print(f"     Count: {count:,}")
        print(f"     Min ID: {min_id}")
        print(f"     Max ID: {max_id}")
        
        # Check for overlap
        our_min, our_max = our_player_ids.min(), our_player_ids.max()
        overlap_min = max(our_min, min_id)
        overlap_max = min(our_max, max_id)
        
        if overlap_min <= overlap_max:
            print(f"   Overlap range: {overlap_min} to {overlap_max}")
            
            # Check how many of our IDs fall in the overlap
            overlap_count = np.sum((our_player_ids >= overlap_min) & (our_player_ids <= overlap_max))
            print(f"   Our IDs in overlap range: {overlap_count}/{len(our_player_ids)} ({overlap_count/len(our_player_ids)*100:.1f}%)")
        else:
            print(f"   No overlap between ID ranges!")
        
        # Check a few specific IDs from different ranges
        print(f"\n🔍 Checking specific IDs from different ranges...")
        test_ids = [
            our_player_ids.min(),
            our_player_ids.max(),
            (our_player_ids.min() + our_player_ids.max()) // 2,
            overlap_min if overlap_min <= overlap_max else None,
            overlap_max if overlap_min <= overlap_max else None
        ]
        
        for test_id in test_ids:
            if test_id is not None:
                cursor.execute("SELECT id, name, date_of_birth FROM Player WHERE id = ?", (test_id,))
                result = cursor.fetchone()
                print(f"   ID {test_id}: {result}")
        
        # Check Transfer table ID ranges
        cursor.execute("SELECT MIN(player_id), MAX(player_id), COUNT(*) FROM Transfer")
        t_min_id, t_max_id, t_count = cursor.fetchone()
        
        print(f"\n   Dev 2.db Transfer table:")
        print(f"     Count: {t_count:,}")
        print(f"     Min player_id: {t_min_id}")
        print(f"     Max player_id: {t_max_id}")
        
        # Check if any of our IDs have transfers
        sample_our_ids = our_player_ids[:100]
        placeholders = ','.join(['?' for _ in sample_our_ids])
        cursor.execute(f"SELECT COUNT(*) FROM Transfer WHERE player_id IN ({placeholders})", sample_our_ids)
        transfer_matches = cursor.fetchone()[0]
        print(f"   Our IDs with transfers (first 100): {transfer_matches}")
        
        # Check if any of our IDs exist in Player table
        cursor.execute(f"SELECT COUNT(*) FROM Player WHERE id IN ({placeholders})", sample_our_ids)
        player_matches = cursor.fetchone()[0]
        print(f"   Our IDs in Player table (first 100): {player_matches}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🚀 Comparing player IDs between databases...")
    compare_player_ids()

if __name__ == "__main__":
    main()
