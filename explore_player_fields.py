#!/usr/bin/env python3
"""
Explore Player Fields - Analyze Player and related tables in dev 2.db
to identify available data for missing player fields
"""
import sqlite3
import pandas as pd

def explore_player_related_tables():
    """Explore Player and related tables to find available fields"""
    print("🔍 Exploring Player-related tables in dev 2.db...")
    
    try:
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Available tables: {[table[0] for table in tables]}")
        
        # Focus on Player and related tables
        relevant_tables = ['Player', 'Citizenship', 'Position']
        
        for table_name in relevant_tables:
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
            
            column_names = [col[1] for col in columns]
            for row in sample_data:
                print(f"      Row: {dict(zip(column_names, row))}")
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📊 Total records: {count}")
        
        # Check for relationships between tables
        print(f"\n🔍 Checking relationships...")
        
        # Check if Player has citizenship_id or position_id
        cursor.execute("PRAGMA table_info(Player)")
        player_columns = [col[1] for col in cursor.fetchall()]
        
        if 'citizenship_id' in player_columns:
            print(f"   ✅ Player table has citizenship_id")
        if 'position_id' in player_columns:
            print(f"   ✅ Player table has position_id")
        
        # Check what fields Player table has that might help
        target_fields = ['nationality', 'position', 'dominant_foot', 'agent', 'social_links', 'country_of_birth']
        print(f"\n🔍 Checking target fields in Player table:")
        for field in target_fields:
            if field in player_columns:
                print(f"   ✅ Found: {field}")
            else:
                print(f"   ❌ Not found: {field}")
        
        # Look for similar field names
        print(f"\n🔍 Looking for similar field names in Player table:")
        for col_name in player_columns:
            if any(keyword in col_name.lower() for keyword in ['nation', 'country', 'citizen', 'position', 'foot', 'agent', 'social', 'birth']):
                print(f"   📋 Found similar column: {col_name}")
        
        # Check if there are other tables that might contain this data
        print(f"\n🔍 Looking for other relevant tables:")
        for table_tuple in tables:
            table_name = table_tuple[0]
            if any(keyword in table_name.lower() for keyword in ['social', 'agent', 'birth', 'location']):
                print(f"   📋 Found potentially relevant table: {table_name}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def analyze_current_missing_data():
    """Analyze what data is missing in current database"""
    print(f"\n🔍 Analyzing missing data in current database...")
    
    try:
        # Load the current database
        df = pd.read_csv('all_players_combined_database_enriched_youth_clubs.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Check missing data in target columns
        target_columns = ['nationality', 'position', 'dominant_foot', 'agent', 'social_links', 'country_of_birth']
        
        print(f"\n📊 MISSING DATA ANALYSIS:")
        for col in target_columns:
            if col in df.columns:
                total_records = len(df)
                missing_records = df[col].isna().sum()
                
                # Also check for "Not found" values
                not_found_count = 0
                if df[col].dtype == 'object':  # String column
                    not_found_count = (df[col] == 'Not found').sum()
                
                filled_records = total_records - missing_records - not_found_count
                coverage = (filled_records / total_records) * 100
                
                print(f"   {col}:")
                print(f"      - Total records: {total_records}")
                print(f"      - Filled records: {filled_records}")
                print(f"      - Missing records: {missing_records}")
                print(f"      - 'Not found' records: {not_found_count}")
                print(f"      - Coverage: {coverage:.1f}%")
                
                # Show some examples of filled data
                if filled_records > 0:
                    examples = df[df[col].notna() & (df[col] != 'Not found')][col].unique()[:5]
                    print(f"      - Examples: {list(examples)}")
            else:
                print(f"   {col}: Column not found in database")
        
        # Check unique values for filled data
        print(f"\n📊 UNIQUE VALUES IN FILLED DATA:")
        for col in target_columns:
            if col in df.columns:
                filled_data = df[df[col].notna() & (df[col] != 'Not found')][col]
                if len(filled_data) > 0:
                    unique_count = filled_data.nunique()
                    print(f"   {col}: {unique_count} unique values")
                    
                    if unique_count <= 20:  # Show all if not too many
                        print(f"      Values: {sorted(filled_data.unique())}")
                    else:  # Show sample
                        sample_values = sorted(filled_data.unique())[:10]
                        print(f"      Sample values: {sample_values}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🚀 Starting player fields exploration...")
    
    try:
        explore_player_related_tables()
        analyze_current_missing_data()
        
        print(f"\n🎉 Player fields exploration completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
