#!/usr/bin/env python3
"""
Extract Market Values - Extract the latest current market values from dev 2.db
for all players in our final merged database
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

def explore_database_structure():
    """Explore the structure of the dev 2.db database"""
    print("🔍 Exploring database structure...")
    
    try:
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Found {len(tables)} tables:")
        for i, table in enumerate(tables):
            print(f"   {i+1}. {table[0]}")
        
        # Explore each table structure
        for table_name in tables:
            table = table_name[0]
            print(f"\n🔍 Table: {table}")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            print(f"   Columns ({len(columns)}):")
            for col in columns:
                print(f"   • {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   Rows: {count:,}")
            
            # Show sample data if table has data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                sample = cursor.fetchall()
                print(f"   Sample data:")
                for row in sample[:2]:  # Show first 2 rows
                    print(f"     {row}")
        
        conn.close()
        return tables
        
    except Exception as e:
        print(f"❌ Error exploring database: {e}")
        return None

def extract_market_values():
    """Extract market values from the database"""
    print("🔄 Loading final merged database...")
    
    # Load our final database
    df_final = pd.read_csv('merged_players_databases_final.csv')
    print(f"   ✅ Loaded {len(df_final)} players from final database")
    
    # Extract player IDs
    df_final['player_id'] = df_final['profile_url'].apply(extract_player_id_from_url)
    player_ids = df_final['player_id'].dropna().astype(int).tolist()
    
    print(f"   📊 Player IDs to lookup: {len(player_ids)}")
    
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # First, let's find tables that might contain market value data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"📋 Available tables: {tables}")
        
        # Look for tables that might contain market values
        market_value_tables = []
        for table in tables:
            if any(keyword in table.lower() for keyword in ['market', 'value', 'player', 'transfer']):
                market_value_tables.append(table)
        
        print(f"🎯 Potential market value tables: {market_value_tables}")
        
        # Explore each potential table
        for table in market_value_tables:
            print(f"\n🔍 Exploring table: {table}")
            
            try:
                # Get column info
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                print(f"   Columns: {column_names}")
                
                # Look for player ID and market value columns
                id_columns = [col for col in column_names if any(keyword in col.lower() for keyword in ['id', 'player'])]
                value_columns = [col for col in column_names if any(keyword in col.lower() for keyword in ['value', 'market', 'price'])]
                date_columns = [col for col in column_names if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'updated'])]
                
                print(f"   ID columns: {id_columns}")
                print(f"   Value columns: {value_columns}")
                print(f"   Date columns: {date_columns}")
                
                # Get sample data
                cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                sample = cursor.fetchall()
                print(f"   Sample data:")
                for row in sample[:2]:
                    print(f"     {row}")
                
                # Try to find matches with our player IDs
                if id_columns and value_columns:
                    id_col = id_columns[0]
                    value_col = value_columns[0]
                    
                    # Create a query to find our players
                    placeholders = ','.join(['?' for _ in player_ids[:100]])  # Limit to first 100 for testing
                    query = f"SELECT {id_col}, {value_col} FROM {table} WHERE {id_col} IN ({placeholders})"
                    
                    cursor.execute(query, player_ids[:100])
                    matches = cursor.fetchall()
                    
                    print(f"   🎯 Found {len(matches)} matches for our players")
                    if matches:
                        for match in matches[:3]:
                            print(f"     Player ID: {match[0]}, Value: {match[1]}")
                
            except Exception as e:
                print(f"   ❌ Error exploring {table}: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def main():
    """Main function"""
    print("🚀 Starting market value extraction from dev 2.db")
    
    # First explore the database structure
    tables = explore_database_structure()
    
    if tables:
        print(f"\n" + "="*50)
        # Then try to extract market values
        extract_market_values()
    
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main()
