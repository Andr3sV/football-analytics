#!/usr/bin/env python3
"""
Enrich Youth Club Data - Use dev 2.db Club table to fill missing
db_yt_members, db_yt_country, db_yt_league_name, db_yt_league_tier columns
"""
import sqlite3
import pandas as pd
import numpy as np
import re

def clean_club_name(name):
    """Clean club name for better matching"""
    if pd.isna(name):
        return None
    
    # Convert to string and clean
    name = str(name).strip()
    
    # Remove common suffixes and prefixes that might cause mismatches
    name = re.sub(r'\s*\([^)]*\)', '', name)  # Remove parentheses content
    name = re.sub(r'\s*\d{4}-\d{4}', '', name)  # Remove year ranges
    name = re.sub(r'\s*\(bis \d{4}\)', '', name)  # Remove "bis year" content
    name = re.sub(r'\s*U\d+', '', name)  # Remove U15, U17, etc.
    name = re.sub(r'\s*Jugend', '', name)  # Remove Jugend
    name = re.sub(r'\s*Youth', '', name)  # Remove Youth
    
    # Normalize common variations
    name = name.replace('FC ', '').replace('AC ', '').replace('SC ', '')
    name = name.replace('1.', '').replace('2.', '').replace('3.', '')
    
    return name.strip()

def create_club_mapping():
    """Create mapping between youth clubs and club data from dev 2.db"""
    print("🔍 Creating club mapping from dev 2.db...")
    
    try:
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get all club data
        print("   📊 Loading Club table data...")
        cursor.execute("""
            SELECT id, name, members, country, league_name, league_tier 
            FROM Club
            WHERE name IS NOT NULL
        """)
        club_data = cursor.fetchall()
        
        print(f"   ✅ Loaded {len(club_data)} club records")
        
        # Create mapping dictionaries
        club_mapping_by_name = {}
        club_mapping_by_clean_name = {}
        
        for club_id, name, members, country, league_name, league_tier in club_data:
            if name:
                # Direct name mapping
                club_mapping_by_name[name.lower()] = {
                    'id': club_id,
                    'name': name,
                    'members': members,
                    'country': country,
                    'league_name': league_name,
                    'league_tier': league_tier
                }
                
                # Clean name mapping
                clean_name = clean_club_name(name)
                if clean_name and clean_name.lower() != name.lower():
                    club_mapping_by_clean_name[clean_name.lower()] = {
                        'id': club_id,
                        'name': name,
                        'members': members,
                        'country': country,
                        'league_name': league_name,
                        'league_tier': league_tier
                    }
        
        print(f"   📊 Created {len(club_mapping_by_name)} direct name mappings")
        print(f"   📊 Created {len(club_mapping_by_clean_name)} clean name mappings")
        
        conn.close()
        
        return club_mapping_by_name, club_mapping_by_clean_name
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}

def find_club_match(youth_club_name, club_mapping_by_name, club_mapping_by_clean_name):
    """Find matching club data for a youth club name"""
    if pd.isna(youth_club_name):
        return None
    
    youth_name = str(youth_club_name).strip()
    
    # Try direct match first
    if youth_name.lower() in club_mapping_by_name:
        return club_mapping_by_name[youth_name.lower()]
    
    # Try clean name match
    clean_youth_name = clean_club_name(youth_name)
    if clean_youth_name and clean_youth_name.lower() in club_mapping_by_clean_name:
        return club_mapping_by_clean_name[clean_youth_name.lower()]
    
    # Try partial matching
    youth_name_lower = youth_name.lower()
    for club_name, club_data in club_mapping_by_name.items():
        if (youth_name_lower in club_name or 
            club_name in youth_name_lower or
            any(word in club_name for word in youth_name_lower.split() if len(word) > 3)):
            return club_data
    
    return None

def enrich_youth_club_data():
    """Enrich database with missing youth club data from dev 2.db"""
    print("🚀 Starting youth club data enrichment...")
    
    try:
        # Load current database
        print("🔄 Loading current database...")
        df = pd.read_csv('all_players_combined_database_with_calculated_youth_years.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Create club mapping
        club_mapping_by_name, club_mapping_by_clean_name = create_club_mapping()
        
        if not club_mapping_by_name:
            print("❌ Failed to create club mapping")
            return None
        
        # Identify records that need enrichment
        print(f"\n🔍 Identifying records needing enrichment...")
        
        target_columns = ['db_yt_members', 'db_yt_country', 'db_yt_league_name', 'db_yt_league_tier']
        
        # Records with youth_club but missing target data
        records_to_enrich = df[
            df['youth_club'].notna() & 
            (
                df['db_yt_members'].isna() | 
                df['db_yt_country'].isna() | 
                df['db_yt_league_name'].isna() | 
                df['db_yt_league_tier'].isna()
            )
        ]
        
        print(f"   📊 Records needing enrichment: {len(records_to_enrich)}")
        
        # Show current coverage
        print(f"\n📊 CURRENT COVERAGE:")
        for col in target_columns:
            if col in df.columns:
                filled = df[col].notna().sum()
                total = len(df)
                coverage = (filled / total) * 100
                print(f"   {col}: {filled}/{total} ({coverage:.1f}%)")
        
        # Process enrichment
        print(f"\n🔧 Processing enrichment...")
        
        df_updated = df.copy()
        enriched_count = 0
        matched_count = 0
        
        # Process in batches to avoid memory issues
        batch_size = 1000
        total_batches = (len(records_to_enrich) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(records_to_enrich))
            batch_records = records_to_enrich.iloc[start_idx:end_idx]
            
            for idx, row in batch_records.iterrows():
                youth_club_name = row['youth_club']
                
                # Find matching club data
                club_data = find_club_match(youth_club_name, club_mapping_by_name, club_mapping_by_clean_name)
                
                if club_data:
                    matched_count += 1
                    
                    # Update missing columns
                    if pd.isna(row['db_yt_members']) and club_data['members'] is not None:
                        df_updated.at[idx, 'db_yt_members'] = club_data['members']
                        enriched_count += 1
                    
                    if pd.isna(row['db_yt_country']) and club_data['country'] is not None:
                        df_updated.at[idx, 'db_yt_country'] = club_data['country']
                        enriched_count += 1
                    
                    if pd.isna(row['db_yt_league_name']) and club_data['league_name'] is not None:
                        df_updated.at[idx, 'db_yt_league_name'] = club_data['league_name']
                        enriched_count += 1
                    
                    if pd.isna(row['db_yt_league_tier']) and club_data['league_tier'] is not None:
                        df_updated.at[idx, 'db_yt_league_tier'] = club_data['league_tier']
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
                filled = df_updated[col].notna().sum()
                total = len(df_updated)
                coverage = (filled / total) * 100
                original_filled = df[col].notna().sum()
                improvement = filled - original_filled
                print(f"   {col}: {filled}/{total} ({coverage:.1f}%) [+{improvement}]")
        
        # Show examples of enriched data
        print(f"\n📋 EXAMPLES OF ENRICHED DATA:")
        enriched_examples = df_updated[
            (df_updated['db_yt_members'].notna() | 
             df_updated['db_yt_country'].notna() | 
             df_updated['db_yt_league_name'].notna() | 
             df_updated['db_yt_league_tier'].notna()) &
            df_updated['youth_club'].notna()
        ][
            ['full_name', 'youth_club', 'db_yt_members', 'db_yt_country', 'db_yt_league_name', 'db_yt_league_tier']
        ].head(10)
        
        for _, row in enriched_examples.iterrows():
            print(f"   • {row['full_name']}: {row['youth_club']}")
            print(f"     Members: {row['db_yt_members']}, Country: {row['db_yt_country']}")
            print(f"     League: {row['db_yt_league_name']} ({row['db_yt_league_tier']})")
        
        # Save updated database
        output_file = 'all_players_combined_database_enriched_youth_clubs.csv'
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
    print("🚀 Starting youth club data enrichment...")
    
    try:
        enriched_df = enrich_youth_club_data()
        
        if enriched_df is not None:
            print(f"\n🎉 Successfully enriched youth club data!")
            print(f"📁 Output file: all_players_combined_database_enriched_youth_clubs.csv")
        else:
            print(f"\n❌ Failed to enrich youth club data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
