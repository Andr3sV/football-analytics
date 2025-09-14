#!/usr/bin/env python3
"""
Enrich Player Fields - Use dev 2.db to fill missing player fields:
nationality, position, dominant_foot from Player, Citizenship, and Position tables
"""
import sqlite3
import pandas as pd
import numpy as np
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

def create_player_mappings():
    """Create mappings from dev 2.db for player data"""
    print("🔍 Creating player mappings from dev 2.db...")
    
    try:
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get Player data with foot information
        print("   📊 Loading Player table data...")
        cursor.execute("""
            SELECT id, url, name, foot, date_of_birth 
            FROM Player
            WHERE url IS NOT NULL
        """)
        player_data = cursor.fetchall()
        
        print(f"   ✅ Loaded {len(player_data)} player records")
        
        # Create URL to player data mapping
        player_mapping = {}
        for player_id, url, name, foot, date_of_birth in player_data:
            if url:
                player_mapping[url] = {
                    'player_id': player_id,
                    'name': name,
                    'foot': foot,
                    'date_of_birth': date_of_birth
                }
        
        # Get Citizenship data
        print("   📊 Loading Citizenship data...")
        cursor.execute("""
            SELECT c.player_id, c.country, p.url
            FROM Citizenship c
            JOIN Player p ON c.player_id = p.id
            WHERE p.url IS NOT NULL
        """)
        citizenship_data = cursor.fetchall()
        
        print(f"   ✅ Loaded {len(citizenship_data)} citizenship records")
        
        # Create citizenship mapping
        citizenship_mapping = {}
        for player_id, country, url in citizenship_data:
            if url:
                if url not in citizenship_mapping:
                    citizenship_mapping[url] = []
                citizenship_mapping[url].append(country)
        
        # Get Position data
        print("   📊 Loading Position data...")
        cursor.execute("""
            SELECT pos.player_id, pos.position, pos.is_main, p.url
            FROM Position pos
            JOIN Player p ON pos.player_id = p.id
            WHERE p.url IS NOT NULL
            ORDER BY pos.player_id, pos.is_main DESC, pos.id
        """)
        position_data = cursor.fetchall()
        
        print(f"   ✅ Loaded {len(position_data)} position records")
        
        # Create position mapping (prioritize main position)
        position_mapping = {}
        for player_id, position, is_main, url in position_data:
            if url:
                if url not in position_mapping:
                    position_mapping[url] = []
                position_mapping[url].append({
                    'position': position,
                    'is_main': bool(is_main)
                })
        
        conn.close()
        
        print(f"   📊 Created {len(player_mapping)} player mappings")
        print(f"   📊 Created {len(citizenship_mapping)} citizenship mappings")
        print(f"   📊 Created {len(position_mapping)} position mappings")
        
        return player_mapping, citizenship_mapping, position_mapping
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}, {}

def get_main_position(positions):
    """Get the main position from a list of positions"""
    if not positions:
        return None
    
    # First try to find main position
    for pos in positions:
        if pos['is_main']:
            return pos['position']
    
    # If no main position, return the first one
    return positions[0]['position']

def get_primary_nationality(nationalities):
    """Get the primary nationality from a list of nationalities"""
    if not nationalities:
        return None
    
    # Return the first nationality (could be enhanced with priority logic)
    return nationalities[0]

def enrich_player_fields():
    """Enrich database with missing player fields from dev 2.db"""
    print("🚀 Starting player fields enrichment...")
    
    try:
        # Load current database
        print("🔄 Loading current database...")
        df = pd.read_csv('all_players_combined_database_enriched_youth_clubs.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Create mappings
        player_mapping, citizenship_mapping, position_mapping = create_player_mappings()
        
        if not player_mapping:
            print("❌ Failed to create player mappings")
            return None
        
        # Identify records that need enrichment
        print(f"\n🔍 Identifying records needing enrichment...")
        
        target_columns = ['nationality', 'position', 'dominant_foot']
        
        # Records that need enrichment (missing or "Not found")
        records_to_enrich = df[
            df['profile_url'].notna() & 
            (
                df['nationality'].isna() | (df['nationality'] == 'Not found') |
                df['position'].isna() | (df['position'] == 'Not found') |
                df['dominant_foot'].isna() | (df['dominant_foot'] == 'Not found')
            )
        ]
        
        print(f"   📊 Records needing enrichment: {len(records_to_enrich)}")
        
        # Show current coverage
        print(f"\n📊 CURRENT COVERAGE:")
        for col in target_columns:
            if col in df.columns:
                filled = df[df[col].notna() & (df[col] != 'Not found')][col]
                total = len(df)
                coverage = (len(filled) / total) * 100
                print(f"   {col}: {len(filled)}/{total} ({coverage:.1f}%)")
        
        # Process enrichment
        print(f"\n🔧 Processing enrichment...")
        
        df_updated = df.copy()
        enriched_count = 0
        matched_count = 0
        
        # Process in batches
        batch_size = 1000
        total_batches = (len(records_to_enrich) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(records_to_enrich))
            batch_records = records_to_enrich.iloc[start_idx:end_idx]
            
            for idx, row in batch_records.iterrows():
                profile_url = row['profile_url']
                
                if profile_url in player_mapping:
                    matched_count += 1
                    player_data = player_mapping[profile_url]
                    
                    # Update nationality
                    if (pd.isna(row['nationality']) or row['nationality'] == 'Not found') and profile_url in citizenship_mapping:
                        nationalities = citizenship_mapping[profile_url]
                        primary_nationality = get_primary_nationality(nationalities)
                        if primary_nationality:
                            df_updated.at[idx, 'nationality'] = primary_nationality
                            enriched_count += 1
                    
                    # Update position
                    if (pd.isna(row['position']) or row['position'] == 'Not found') and profile_url in position_mapping:
                        positions = position_mapping[profile_url]
                        main_position = get_main_position(positions)
                        if main_position:
                            df_updated.at[idx, 'position'] = main_position
                            enriched_count += 1
                    
                    # Update dominant_foot
                    if (pd.isna(row['dominant_foot']) or row['dominant_foot'] == 'Not found') and player_data['foot']:
                        df_updated.at[idx, 'dominant_foot'] = player_data['foot']
                        enriched_count += 1
            
            # Progress update
            if batch_idx % 5 == 0:
                progress = (batch_idx + 1) / total_batches * 100
                print(f"   📊 Progress: {progress:.1f}% ({batch_idx + 1}/{total_batches} batches)")
        
        print(f"\n📊 ENRICHMENT RESULTS:")
        print(f"   Records processed: {len(records_to_enrich)}")
        print(f"   Records matched: {matched_count}")
        print(f"   Fields enriched: {enriched_count}")
        
        # Show updated coverage
        print(f"\n📊 UPDATED COVERAGE:")
        for col in target_columns:
            if col in df_updated.columns:
                filled = df_updated[df_updated[col].notna() & (df_updated[col] != 'Not found')][col]
                total = len(df_updated)
                coverage = (len(filled) / total) * 100
                original_filled = df[df[col].notna() & (df[col] != 'Not found')][col]
                improvement = len(filled) - len(original_filled)
                print(f"   {col}: {len(filled)}/{total} ({coverage:.1f}%) [+{improvement}]")
        
        # Show examples of enriched data
        print(f"\n📋 EXAMPLES OF ENRICHED DATA:")
        enriched_examples = df_updated[
            (df_updated['nationality'].notna() & (df_updated['nationality'] != 'Not found')) |
            (df_updated['position'].notna() & (df_updated['position'] != 'Not found')) |
            (df_updated['dominant_foot'].notna() & (df_updated['dominant_foot'] != 'Not found'))
        ][
            ['full_name', 'nationality', 'position', 'dominant_foot']
        ].head(10)
        
        for _, row in enriched_examples.iterrows():
            print(f"   • {row['full_name']}: {row['nationality']}, {row['position']}, {row['dominant_foot']}")
        
        # Show statistics for fields that couldn't be enriched
        print(f"\n📊 FIELDS THAT COULDN'T BE ENRICHED (no data in dev 2.db):")
        other_columns = ['agent', 'social_links', 'country_of_birth']
        for col in other_columns:
            if col in df_updated.columns:
                filled = df_updated[df_updated[col].notna() & (df_updated[col] != 'Not found')][col]
                total = len(df_updated)
                coverage = (len(filled) / total) * 100
                print(f"   {col}: {len(filled)}/{total} ({coverage:.1f}%) - No data in dev 2.db")
        
        # Save updated database
        output_file = 'all_players_combined_database_enriched_player_fields.csv'
        df_updated.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved enriched database to: {output_file}")
        print(f"📊 Total records: {len(df_updated)}")
        
        return df_updated
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting player fields enrichment...")
    
    try:
        enriched_df = enrich_player_fields()
        
        if enriched_df is not None:
            print(f"\n🎉 Successfully enriched player fields!")
            print(f"📁 Output file: all_players_combined_database_enriched_player_fields.csv")
        else:
            print(f"\n❌ Failed to enrich player fields")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
