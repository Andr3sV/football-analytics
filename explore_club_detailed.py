#!/usr/bin/env python3
"""
Explore Club Tables Detailed - Analyze Club table structure and data
to see what information is available for youth clubs
"""
import sqlite3
import pandas as pd

def explore_club_table_detailed():
    """Explore Club table in detail"""
    print("🔍 Exploring Club table in detail...")
    
    try:
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get Club table structure
        print("📋 Club table structure:")
        cursor.execute("PRAGMA table_info(Club)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Get sample data from Club table
        print(f"\n📊 Sample data from Club table:")
        cursor.execute("SELECT * FROM Club LIMIT 10")
        sample_data = cursor.fetchall()
        
        # Get column names for better display
        column_names = [col[1] for col in columns]
        
        for row in sample_data:
            print(f"   Row: {dict(zip(column_names, row))}")
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM Club")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total Club records: {count}")
        
        # Look for specific columns that might contain the data we need
        relevant_columns = ['members', 'country', 'league_name', 'league_tier']
        
        print(f"\n🔍 Checking for relevant columns:")
        for col_name in relevant_columns:
            if col_name in column_names:
                print(f"   ✅ Found column: {col_name}")
                
                # Get sample values
                cursor.execute(f"SELECT DISTINCT {col_name} FROM Club WHERE {col_name} IS NOT NULL LIMIT 5")
                values = cursor.fetchall()
                print(f"      Sample values: {[v[0] for v in values]}")
            else:
                print(f"   ❌ Column not found: {col_name}")
        
        # Check for columns with similar names
        print(f"\n🔍 Looking for columns with similar names:")
        for col_name in column_names:
            if any(keyword in col_name.lower() for keyword in ['member', 'country', 'league', 'tier']):
                print(f"   📋 Found similar column: {col_name}")
        
        # Explore YouthClub table structure
        print(f"\n🔍 YouthClub table structure:")
        cursor.execute("PRAGMA table_info(YouthClub)")
        youth_columns = cursor.fetchall()
        for col in youth_columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Get sample data from YouthClub
        print(f"\n📊 Sample data from YouthClub table:")
        cursor.execute("SELECT * FROM YouthClub LIMIT 10")
        youth_sample = cursor.fetchall()
        
        youth_column_names = [col[1] for col in youth_columns]
        for row in youth_sample:
            print(f"   Row: {dict(zip(youth_column_names, row))}")
        
        # Check if there's a relationship between YouthClub and Club
        print(f"\n🔍 Checking relationships:")
        
        # See if YouthClub has club_id or similar
        if 'club_id' in youth_column_names:
            print(f"   ✅ YouthClub has club_id column")
        else:
            print(f"   ❌ YouthClub doesn't have club_id column")
        
        # Check if we can match by name
        print(f"\n🔍 Checking name matching between YouthClub and Club:")
        cursor.execute("SELECT name FROM YouthClub WHERE name IN (SELECT name FROM Club) LIMIT 5")
        matching_names = cursor.fetchall()
        print(f"   📊 Found {len(matching_names)} matching club names:")
        for name in matching_names:
            print(f"      - {name[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def analyze_youth_club_mapping():
    """Analyze how to map youth clubs to club data"""
    print(f"\n🔍 Analyzing youth club mapping possibilities...")
    
    try:
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get unique youth club names
        cursor.execute("SELECT DISTINCT name FROM YouthClub ORDER BY name")
        youth_clubs = cursor.fetchall()
        print(f"📊 Total unique youth clubs: {len(youth_clubs)}")
        
        # Get unique club names
        cursor.execute("SELECT DISTINCT name FROM Club ORDER BY name")
        clubs = cursor.fetchall()
        print(f"📊 Total unique clubs: {len(clubs)}")
        
        # Find exact matches
        cursor.execute("""
            SELECT yc.name, COUNT(*) as count
            FROM YouthClub yc
            WHERE yc.name IN (SELECT name FROM Club)
            GROUP BY yc.name
            ORDER BY count DESC
            LIMIT 10
        """)
        exact_matches = cursor.fetchall()
        
        print(f"\n📊 Top 10 exact matches between YouthClub and Club:")
        for name, count in exact_matches:
            print(f"   - {name}: {count} records")
        
        # Check for partial matches (clubs that contain youth club names)
        print(f"\n🔍 Checking for partial matches...")
        
        # Get some youth club names to test
        cursor.execute("SELECT DISTINCT name FROM YouthClub LIMIT 20")
        test_youth_clubs = cursor.fetchall()
        
        for youth_club_name in test_youth_clubs[:5]:
            youth_name = youth_club_name[0]
            cursor.execute("""
                SELECT name FROM Club 
                WHERE name LIKE ? OR name LIKE ?
                LIMIT 3
            """, (f"%{youth_name}%", f"{youth_name}%"))
            
            partial_matches = cursor.fetchall()
            if partial_matches:
                print(f"   Youth: {youth_name}")
                for match in partial_matches:
                    print(f"      → Club: {match[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🚀 Starting detailed club exploration...")
    
    try:
        explore_club_table_detailed()
        analyze_youth_club_mapping()
        
        print(f"\n🎉 Detailed exploration completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
