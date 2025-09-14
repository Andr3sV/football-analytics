#!/usr/bin/env python3
"""
Explore Transfer Table - Check the structure of the Transfer table in dev 2.db
"""
import sqlite3
import pandas as pd

def explore_transfer_table():
    """Explore the Transfer table structure"""
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get table schema
        print("🔍 Exploring Transfer table schema...")
        cursor.execute("PRAGMA table_info(Transfer)")
        columns = cursor.fetchall()
        
        print(f"\n📋 TRANSFER TABLE COLUMNS:")
        for col in columns:
            print(f"   • {col[1]} ({col[2]})")
        
        # Get sample data
        print(f"\n🔍 Sample data from Transfer table:")
        cursor.execute("SELECT * FROM Transfer LIMIT 5")
        sample_data = cursor.fetchall()
        
        if sample_data:
            print(f"   📊 Found {len(sample_data)} sample records")
            for i, row in enumerate(sample_data):
                print(f"   Record {i+1}: {row}")
        else:
            print("   ⚠️  No data found in Transfer table")
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM Transfer")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total records in Transfer table: {count:,}")
        
        # Check for related tables
        print(f"\n🔍 Checking for Club table...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%club%'")
        club_tables = cursor.fetchall()
        print(f"   Club-related tables: {[table[0] for table in club_tables]}")
        
        if club_tables:
            # Check Club table structure
            club_table = club_tables[0][0]
            print(f"\n📋 {club_table.upper()} TABLE COLUMNS:")
            cursor.execute(f"PRAGMA table_info({club_table})")
            club_columns = cursor.fetchall()
            for col in club_columns:
                print(f"   • {col[1]} ({col[2]})")
            
            # Sample club data
            cursor.execute(f"SELECT * FROM {club_table} LIMIT 3")
            club_sample = cursor.fetchall()
            print(f"\n📊 Sample {club_table} data:")
            for i, row in enumerate(club_sample):
                print(f"   Record {i+1}: {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("🚀 Exploring Transfer table structure...")
    explore_transfer_table()

if __name__ == "__main__":
    main()
