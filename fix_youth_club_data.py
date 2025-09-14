#!/usr/bin/env python3
"""
Fix Youth Club Data - Clear incorrect data and re-populate with correct data
from dev 2.db Club table using youth_club names
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
    """Create mapping from dev 2.db Club table"""
    print("🔍 Creating club mapping from dev 2.db...")
    
    try:
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        # Get all club data
        print("   📊 Loading Club table data...")
        cursor.execute("""
            SELECT id, url, name, members, country, league_name, league_tier, founded 
            FROM Club
            WHERE name IS NOT NULL
        """)
        club_data = cursor.fetchall()
        
        print(f"   ✅ Loaded {len(club_data)} club records")
        
        # Create mapping dictionaries
        club_mapping_by_name = {}
        club_mapping_by_clean_name = {}
        
        for club_id, url, name, members, country, league_name, league_tier, founded in club_data:
            if name:
                # Direct name mapping
                club_mapping_by_name[name.lower()] = {
                    'id': club_id,
                    'url': url,
                    'name': name,
                    'members': members,
                    'country': country,
                    'league_name': league_name,
                    'league_tier': league_tier,
                    'founded': founded
                }
                
                # Clean name mapping
                clean_name = clean_club_name(name)
                if clean_name and clean_name.lower() != name.lower():
                    club_mapping_by_clean_name[clean_name.lower()] = {
                        'id': club_id,
                        'url': url,
                        'name': name,
                        'members': members,
                        'country': country,
                        'league_name': league_name,
                        'league_tier': league_tier,
                        'founded': founded
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

def fix_youth_club_data():
    """Fix youth club data by clearing incorrect data and re-populating from dev 2.db"""
    print("🚀 Starting youth club data fix...")
    
    try:
        # Load the manually cleaned database
        print("🔄 Loading manually cleaned database...")
        df = pd.read_csv('db_players_and_training_clubs.csv.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Show current state of youth club columns
        youth_club_columns = [
            'youth_club_members', 'youth_club_country', 'youth_club_league', 
            'youth_club_league_tier', 'youth_club_url', 'youth_club_date_of_birth'
        ]
        
        print(f"\n📊 CURRENT STATE OF YOUTH CLUB COLUMNS:")
        for col in youth_club_columns:
            if col in df.columns:
                filled = df[col].notna().sum()
                total = len(df)
                coverage = (filled / total) * 100
                print(f"   {col}: {filled}/{total} ({coverage:.1f}%)")
        
        # Step 1: Clear incorrect data from youth club columns
        print(f"\n🧹 STEP 1: Clearing incorrect data from youth club columns...")
        
        df_cleared = df.copy()
        
        for col in youth_club_columns:
            if col in df_cleared.columns:
                # Clear all data in these columns
                df_cleared[col] = np.nan
                print(f"   ✅ Cleared {col}")
        
        print(f"   ✅ All youth club columns cleared")
        
        # Step 2: Create club mapping
        club_mapping_by_name, club_mapping_by_clean_name = create_club_mapping()
        
        if not club_mapping_by_name:
            print("❌ Failed to create club mapping")
            return None
        
        # Step 3: Re-populate with correct data
        print(f"\n🔧 STEP 2: Re-populating with correct data from dev 2.db...")
        
        # Get unique youth clubs
        unique_youth_clubs = df_cleared['youth_club'].dropna().unique()
        print(f"   📊 Unique youth clubs to process: {len(unique_youth_clubs)}")
        
        # Create youth club to club data mapping
        youth_club_mapping = {}
        matched_count = 0
        
        for youth_club in unique_youth_clubs:
            club_data = find_club_match(youth_club, club_mapping_by_name, club_mapping_by_clean_name)
            if club_data:
                youth_club_mapping[youth_club] = club_data
                matched_count += 1
        
        print(f"   📊 Successfully matched {matched_count}/{len(unique_youth_clubs)} youth clubs")
        
        # Step 4: Apply correct data to all records
        print(f"\n🔧 STEP 3: Applying correct data to all records...")
        
        df_fixed = df_cleared.copy()
        updated_count = 0
        
        # Process records with youth clubs
        records_with_youth_clubs = df_fixed[df_fixed['youth_club'].notna()]
        print(f"   📊 Records with youth clubs: {len(records_with_youth_clubs)}")
        
        for idx, row in records_with_youth_clubs.iterrows():
            youth_club_name = row['youth_club']
            
            if youth_club_name in youth_club_mapping:
                club_data = youth_club_mapping[youth_club_name]
                
                # Update all youth club columns
                df_fixed.at[idx, 'youth_club_members'] = club_data['members']
                df_fixed.at[idx, 'youth_club_country'] = club_data['country']
                df_fixed.at[idx, 'youth_club_league'] = club_data['league_name']
                df_fixed.at[idx, 'youth_club_league_tier'] = club_data['league_tier']
                df_fixed.at[idx, 'youth_club_url'] = club_data['url']
                df_fixed.at[idx, 'youth_club_date_of_birth'] = club_data['founded']
                
                updated_count += 1
        
        print(f"   ✅ Updated {updated_count} records with correct youth club data")
        
        # Show final statistics
        print(f"\n📊 FINAL STATISTICS:")
        for col in youth_club_columns:
            if col in df_fixed.columns:
                filled = df_fixed[col].notna().sum()
                total = len(df_fixed)
                coverage = (filled / total) * 100
                print(f"   {col}: {filled}/{total} ({coverage:.1f}%)")
        
        # Show examples of fixed data
        print(f"\n📋 EXAMPLES OF FIXED DATA:")
        fixed_examples = df_fixed[
            df_fixed['youth_club'].notna() & 
            df_fixed['youth_club_members'].notna()
        ][
            ['full_name', 'youth_club', 'youth_club_members', 'youth_club_country', 
             'youth_club_league', 'youth_club_league_tier']
        ].head(10)
        
        for _, row in fixed_examples.iterrows():
            print(f"   • {row['full_name']}: {row['youth_club']}")
            print(f"     Members: {row['youth_club_members']}, Country: {row['youth_club_country']}")
            print(f"     League: {row['youth_club_league']} ({row['youth_club_league_tier']})")
        
        # Show unmatched youth clubs
        unmatched_clubs = set(unique_youth_clubs) - set(youth_club_mapping.keys())
        if unmatched_clubs:
            print(f"\n⚠️  UNMATCHED YOUTH CLUBS ({len(unmatched_clubs)}):")
            for club in sorted(list(unmatched_clubs))[:20]:  # Show first 20
                print(f"   - {club}")
            if len(unmatched_clubs) > 20:
                print(f"   ... and {len(unmatched_clubs) - 20} more")
        
        # Save fixed database
        output_file = 'db_players_and_training_clubs_fixed.csv'
        df_fixed.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved fixed database to: {output_file}")
        print(f"📊 Total records: {len(df_fixed)}")
        
        return df_fixed
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting youth club data fix...")
    
    try:
        fixed_df = fix_youth_club_data()
        
        if fixed_df is not None:
            print(f"\n🎉 Successfully fixed youth club data!")
            print(f"📁 Output file: db_players_and_training_clubs_fixed.csv")
        else:
            print(f"\n❌ Failed to fix youth club data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
