#!/usr/bin/env python3
"""
Explore Club Tables - Analyze Youth Clubs and Clubs tables in dev 2.db
to identify available data for missing db_yt columns
"""
import sqlite3
import pandas as pd

def explore_club_tables():
    """Explore Youth Clubs and Clubs tables in dev 2.db"""
    print("🔍 Exploring Club tables in dev 2.db...")
    
    try:
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Available tables: {[table[0] for table in tables]}")
        
        # Check if Youth Clubs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%Youth%' OR name LIKE '%youth%'")
        youth_tables = cursor.fetchall()
        print(f"📋 Youth-related tables: {[table[0] for table in youth_tables]}")
        
        # Check if Clubs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%Club%' OR name LIKE '%club%'")
        club_tables = cursor.fetchall()
        print(f"📋 Club-related tables: {[table[0] for table in club_tables]}")
        
        # Explore Youth Clubs table if it exists
        if youth_tables:
            for table_tuple in youth_tables:
                table_name = table_tuple[0]
                print(f"\n🔍 Exploring table: {table_name}")
                
                # Get table structure
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"   📋 Columns in {table_name}:")
                for col in columns:
                    print(f"      - {col[1]} ({col[2]})")
                
                # Get sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample_data = cursor.fetchall()
                print(f"   📊 Sample data from {table_name}:")
                for row in sample_data:
                    print(f"      {row}")
                
                # Get total count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   📊 Total records: {count}")
        
        # Explore Clubs table if it exists
        if club_tables:
            for table_tuple in club_tables:
                table_name = table_tuple[0]
                print(f"\n🔍 Exploring table: {table_name}")
                
                # Get table structure
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"   📋 Columns in {table_name}:")
                for col in columns:
                    print(f"      - {col[1]} ({col[2]})")
                
                # Get sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample_data = cursor.fetchall()
                print(f"   📊 Sample data from {table_name}:")
                for row in sample_data:
                    print(f"      {row}")
                
                # Get total count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   📊 Total records: {count}")
        
        # Look for tables that might contain league information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%League%' OR name LIKE '%league%'")
        league_tables = cursor.fetchall()
        print(f"\n📋 League-related tables: {[table[0] for table in league_tables]}")
        
        if league_tables:
            for table_tuple in league_tables:
                table_name = table_tuple[0]
                print(f"\n🔍 Exploring table: {table_name}")
                
                # Get table structure
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print(f"   📋 Columns in {table_name}:")
                for col in columns:
                    print(f"      - {col[1]} ({col[2]})")
                
                # Get sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_data = cursor.fetchall()
                print(f"   📊 Sample data from {table_name}:")
                for row in sample_data:
                    print(f"      {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def analyze_current_database():
    """Analyze current database to see what youth club data is missing"""
    print(f"\n🔍 Analyzing current database for missing youth club data...")
    
    try:
        # Load the current database
        df = pd.read_csv('all_players_combined_database_with_calculated_youth_years.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Check missing data in youth club columns
        youth_columns = ['db_yt_members', 'db_yt_country', 'db_yt_league_name', 'db_yt_league_tier']
        
        print(f"\n📊 MISSING DATA ANALYSIS:")
        for col in youth_columns:
            if col in df.columns:
                total_records = len(df)
                missing_records = df[col].isna().sum()
                filled_records = total_records - missing_records
                coverage = (filled_records / total_records) * 100
                
                print(f"   {col}:")
                print(f"      - Total records: {total_records}")
                print(f"      - Filled records: {filled_records}")
                print(f"      - Missing records: {missing_records}")
                print(f"      - Coverage: {coverage:.1f}%")
            else:
                print(f"   {col}: Column not found in database")
        
        # Check unique youth clubs
        if 'youth_club' in df.columns:
            unique_youth_clubs = df['youth_club'].dropna().unique()
            print(f"\n📊 UNIQUE YOUTH CLUBS: {len(unique_youth_clubs)}")
            
            # Show some examples
            print(f"   Examples:")
            for i, club in enumerate(unique_youth_clubs[:10]):
                print(f"      {i+1}. {club}")
        
        # Check db_yt_id.1 column
        if 'db_yt_id.1' in df.columns:
            unique_ids = df['db_yt_id.1'].dropna().unique()
            print(f"\n📊 UNIQUE DB_YT_ID.1: {len(unique_ids)}")
            
            # Show some examples
            print(f"   Examples:")
            for i, club_id in enumerate(unique_ids[:10]):
                print(f"      {i+1}. {club_id}")
        
        # Check records that have youth_club but missing other data
        if 'youth_club' in df.columns:
            records_with_youth_club = df[df['youth_club'].notna()]
            print(f"\n📊 RECORDS WITH YOUTH_CLUB: {len(records_with_youth_club)}")
            
            # Check how many of these are missing other youth club data
            for col in youth_columns:
                if col in df.columns:
                    missing_in_youth_records = records_with_youth_club[col].isna().sum()
                    print(f"   - {col} missing in youth club records: {missing_in_youth_records}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🚀 Starting club tables exploration...")
    
    try:
        explore_club_tables()
        analyze_current_database()
        
        print(f"\n🎉 Exploration completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
