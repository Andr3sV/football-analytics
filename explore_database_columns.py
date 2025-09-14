#!/usr/bin/env python3
"""
Explore Database Columns - Deep dive into dev 2.db to find all available columns
that could enrich our player database
"""
import sqlite3
import pandas as pd
from datetime import datetime

def explore_detailed_database_structure():
    """Explore the database structure in detail to find all available data"""
    print("🔍 Deep exploration of dev 2.db structure...")
    
    try:
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"📋 Found {len(tables)} tables: {tables}")
        
        # Detailed exploration of each table
        for table_name in tables:
            print(f"\n" + "="*60)
            print(f"🔍 DETAILED ANALYSIS: {table_name}")
            print(f"="*60)
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"📊 Columns ({len(columns)}):")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, primary_key = col
                pk_indicator = " (PRIMARY KEY)" if primary_key else ""
                null_indicator = " (NOT NULL)" if not_null else ""
                default_indicator = f" (DEFAULT: {default_val})" if default_val else ""
                print(f"   • {col_name}: {col_type}{pk_indicator}{null_indicator}{default_indicator}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"📊 Total rows: {count:,}")
            
            if count > 0:
                # Get sample data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample = cursor.fetchall()
                
                print(f"📋 Sample data (first 5 rows):")
                for i, row in enumerate(sample):
                    print(f"   Row {i+1}: {row}")
                
                # Get unique values for each column (if not too many)
                print(f"📊 Unique values analysis:")
                for col in columns:
                    col_name = col[1]
                    try:
                        cursor.execute(f"SELECT DISTINCT {col_name} FROM {table_name} WHERE {col_name} IS NOT NULL LIMIT 10")
                        unique_values = cursor.fetchall()
                        
                        if len(unique_values) > 0:
                            print(f"   {col_name}: {len(unique_values)} unique values")
                            if len(unique_values) <= 10:
                                values_str = ", ".join([str(val[0]) for val in unique_values])
                                print(f"     Examples: {values_str}")
                            else:
                                # Show first few examples
                                examples = ", ".join([str(val[0]) for val in unique_values[:5]])
                                print(f"     Examples: {examples}...")
                        
                    except Exception as e:
                        print(f"   {col_name}: Error analyzing - {e}")
            
            # Special analysis for specific tables
            if table_name == "Player":
                analyze_player_table(cursor)
            elif table_name == "Transfer":
                analyze_transfer_table(cursor)
            elif table_name == "Club":
                analyze_club_table(cursor)
            elif table_name == "Position":
                analyze_position_table(cursor)
            elif table_name == "Citizenship":
                analyze_citizenship_table(cursor)
            elif table_name == "YouthClub":
                analyze_youth_club_table(cursor)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error exploring database: {e}")
        import traceback
        traceback.print_exc()

def analyze_player_table(cursor):
    """Special analysis for Player table"""
    print(f"\n🎯 PLAYER TABLE SPECIAL ANALYSIS:")
    
    # Analyze retirement data
    cursor.execute("SELECT COUNT(*) FROM Player WHERE is_retired = 1")
    retired_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Player WHERE is_retired = 0")
    active_count = cursor.fetchone()[0]
    print(f"   📊 Retired players: {retired_count:,}")
    print(f"   📊 Active players: {active_count:,}")
    
    # Analyze foot data
    cursor.execute("SELECT foot, COUNT(*) FROM Player WHERE foot IS NOT NULL GROUP BY foot")
    foot_data = cursor.fetchall()
    print(f"   📊 Foot preference:")
    for foot, count in foot_data:
        print(f"      {foot}: {count:,}")
    
    # Analyze retirement dates
    cursor.execute("SELECT MIN(retired_since), MAX(retired_since) FROM Player WHERE retired_since IS NOT NULL")
    retirement_dates = cursor.fetchone()
    if retirement_dates[0]:
        min_date = datetime.fromtimestamp(retirement_dates[0] / 1000).strftime('%Y-%m-%d')
        max_date = datetime.fromtimestamp(retirement_dates[1] / 1000).strftime('%Y-%m-%d')
        print(f"   📊 Retirement date range: {min_date} to {max_date}")

def analyze_transfer_table(cursor):
    """Special analysis for Transfer table"""
    print(f"\n🎯 TRANSFER TABLE SPECIAL ANALYSIS:")
    
    # Analyze transfer fees
    cursor.execute("SELECT COUNT(*) FROM Transfer WHERE fee IS NOT NULL AND fee != ''")
    fee_count = cursor.fetchone()[0]
    print(f"   📊 Transfers with fee data: {fee_count:,}")
    
    # Analyze market values
    cursor.execute("SELECT COUNT(*) FROM Transfer WHERE market_value IS NOT NULL AND market_value > 0")
    market_value_count = cursor.fetchone()[0]
    print(f"   📊 Transfers with market value: {market_value_count:,}")
    
    # Analyze upcoming transfers
    cursor.execute("SELECT COUNT(*) FROM Transfer WHERE upcoming = 1")
    upcoming_count = cursor.fetchone()[0]
    print(f"   📊 Upcoming transfers: {upcoming_count:,}")
    
    # Analyze transfer date range
    cursor.execute("SELECT MIN(transfer_date), MAX(transfer_date) FROM Transfer WHERE transfer_date IS NOT NULL")
    date_range = cursor.fetchone()
    if date_range[0]:
        min_date = datetime.fromtimestamp(date_range[0] / 1000).strftime('%Y-%m-%d')
        max_date = datetime.fromtimestamp(date_range[1] / 1000).strftime('%Y-%m-%d')
        print(f"   📊 Transfer date range: {min_date} to {max_date}")

def analyze_club_table(cursor):
    """Special analysis for Club table"""
    print(f"\n🎯 CLUB TABLE SPECIAL ANALYSIS:")
    
    # Analyze leagues
    cursor.execute("SELECT league_name, COUNT(*) FROM Club WHERE league_name IS NOT NULL GROUP BY league_name ORDER BY COUNT(*) DESC LIMIT 10")
    leagues = cursor.fetchall()
    print(f"   📊 Top leagues by club count:")
    for league, count in leagues:
        print(f"      {league}: {count:,} clubs")
    
    # Analyze countries
    cursor.execute("SELECT country, COUNT(*) FROM Club WHERE country IS NOT NULL GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10")
    countries = cursor.fetchall()
    print(f"   📊 Top countries by club count:")
    for country, count in countries:
        print(f"      {country}: {count:,} clubs")
    
    # Analyze market values
    cursor.execute("SELECT AVG(current_market_value), MAX(current_market_value), MIN(current_market_value) FROM Club WHERE current_market_value IS NOT NULL")
    market_stats = cursor.fetchone()
    if market_stats[0]:
        print(f"   📊 Club market values:")
        print(f"      Average: €{market_stats[0]:,.0f}")
        print(f"      Maximum: €{market_stats[1]:,.0f}")
        print(f"      Minimum: €{market_stats[2]:,.0f}")

def analyze_position_table(cursor):
    """Special analysis for Position table"""
    print(f"\n🎯 POSITION TABLE SPECIAL ANALYSIS:")
    
    # Analyze main positions
    cursor.execute("SELECT position, COUNT(*) FROM Position WHERE is_main = 1 GROUP BY position ORDER BY COUNT(*) DESC LIMIT 10")
    main_positions = cursor.fetchall()
    print(f"   📊 Top main positions:")
    for position, count in main_positions:
        print(f"      {position}: {count:,} players")
    
    # Analyze all positions
    cursor.execute("SELECT position, COUNT(*) FROM Position GROUP BY position ORDER BY COUNT(*) DESC LIMIT 15")
    all_positions = cursor.fetchall()
    print(f"   📊 Top all positions:")
    for position, count in all_positions:
        print(f"      {position}: {count:,} players")

def analyze_citizenship_table(cursor):
    """Special analysis for Citizenship table"""
    print(f"\n🎯 CITIZENSHIP TABLE SPECIAL ANALYSIS:")
    
    # Analyze countries
    cursor.execute("SELECT country, COUNT(*) FROM Citizenship GROUP BY country ORDER BY COUNT(*) DESC LIMIT 15")
    countries = cursor.fetchall()
    print(f"   📊 Top countries by player count:")
    for country, count in countries:
        print(f"      {country}: {count:,} players")
    
    # Analyze players with multiple citizenships
    cursor.execute("SELECT player_id, COUNT(*) as citizenship_count FROM Citizenship GROUP BY player_id HAVING COUNT(*) > 1")
    multi_citizenship = cursor.fetchall()
    print(f"   📊 Players with multiple citizenships: {len(multi_citizenship):,}")

def analyze_youth_club_table(cursor):
    """Special analysis for YouthClub table"""
    print(f"\n🎯 YOUTH CLUB TABLE SPECIAL ANALYSIS:")
    
    # Analyze top youth clubs
    cursor.execute("SELECT name, COUNT(*) FROM YouthClub GROUP BY name ORDER BY COUNT(*) DESC LIMIT 15")
    youth_clubs = cursor.fetchall()
    print(f"   📊 Top youth clubs by player count:")
    for club, count in youth_clubs:
        print(f"      {club}: {count:,} players")
    
    # Analyze players with multiple youth clubs
    cursor.execute("SELECT player_id, COUNT(*) as club_count FROM YouthClub GROUP BY player_id HAVING COUNT(*) > 1")
    multi_youth = cursor.fetchall()
    print(f"   📊 Players with multiple youth clubs: {len(multi_youth):,}")

def suggest_enrichment_opportunities():
    """Suggest what data could be added to enrich our player database"""
    print(f"\n" + "="*60)
    print(f"💡 ENRICHMENT OPPORTUNITIES")
    print(f"="*60)
    
    suggestions = [
        {
            "table": "Player",
            "columns": ["is_retired", "retired_since", "foot", "retrieved_at"],
            "description": "Player status, retirement info, foot preference, data freshness"
        },
        {
            "table": "Transfer",
            "columns": ["fee", "transfer_date", "upcoming", "from_club", "to_club"],
            "description": "Transfer history, fees, upcoming transfers, club relationships"
        },
        {
            "table": "Club",
            "columns": ["current_market_value", "members", "stadium", "stadium_seats", "founded", "league_tier"],
            "description": "Current club market value, membership, stadium info, founding year, league level"
        },
        {
            "table": "Position",
            "columns": ["position", "is_main"],
            "description": "Detailed position data, main vs secondary positions"
        },
        {
            "table": "Citizenship",
            "columns": ["country"],
            "description": "Multiple citizenships, nationality details"
        },
        {
            "table": "YouthClub",
            "columns": ["name"],
            "description": "Youth development clubs, academy history"
        }
    ]
    
    for suggestion in suggestions:
        print(f"\n📋 {suggestion['table'].upper()} TABLE:")
        print(f"   Available columns: {', '.join(suggestion['columns'])}")
        print(f"   Description: {suggestion['description']}")
    
    print(f"\n🎯 RECOMMENDED PRIORITIES:")
    print(f"   1. 🏆 Player status (retired/active) and foot preference")
    print(f"   2. 📈 Current club market values and league tiers")
    print(f"   3. 🏃 Transfer history and upcoming transfers")
    print(f"   4. 🌍 Multiple citizenships")
    print(f"   5. 🎓 Youth club academy history")
    print(f"   6. ⚽ Detailed position information")

def main():
    """Main function"""
    print("🚀 Starting detailed database exploration...")
    
    try:
        explore_detailed_database_structure()
        suggest_enrichment_opportunities()
        
        print(f"\n✅ Exploration complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
