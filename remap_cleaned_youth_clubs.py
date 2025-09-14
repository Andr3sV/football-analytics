#!/usr/bin/env python3
"""
Re-map Cleaned Youth Clubs - Map cleaned youth club names to dev 2.db Club table
"""
import sqlite3
import pandas as pd
import numpy as np
import re

def clean_youth_club_name(name):
    """Advanced cleaning of youth club names"""
    if pd.isna(name):
        return None
    
    # Convert to string and clean
    name = str(name).strip()
    
    # Remove U followed by numbers (U18, U20, etc.)
    name = re.sub(r'\s*U\d+', '', name, flags=re.IGNORECASE)
    
    # Remove "Youth" text
    name = re.sub(r'\s*Youth', '', name, flags=re.IGNORECASE)
    
    # Remove "Next Gen" text
    name = re.sub(r'\s*Next Gen', '', name, flags=re.IGNORECASE)
    
    # Remove club names with isolated letters B, C, D (like Sevilla FC C, Girona FC B, Villarreal CF B)
    name = re.sub(r'\s+[BCD]\s*$', '', name, flags=re.IGNORECASE)
    
    # Remove common suffixes and prefixes that might cause mismatches
    name = re.sub(r'\s*\([^)]*\)', '', name)  # Remove parentheses content
    name = re.sub(r'\s*\d{4}-\d{4}', '', name)  # Remove year ranges
    name = re.sub(r'\s*\(bis \d{4}\)', '', name)  # Remove "bis year" content
    name = re.sub(r'\s*Jugend', '', name)  # Remove Jugend
    
    # Normalize common variations (keep FC, AC, SC as they are part of official names)
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
                clean_name = clean_youth_club_name(name)
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
    clean_youth_name = clean_youth_club_name(youth_name)
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

def remap_cleaned_youth_clubs():
    """Re-map cleaned youth club names with dev 2.db data"""
    print("🚀 Starting re-mapping of cleaned youth clubs...")
    
    try:
        # Load the cleaned database
        print("🔄 Loading cleaned database...")
        df = pd.read_csv('db_players_youth_clubs_cleaned.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Step 1: Clear existing youth club data
        print(f"\n🧹 STEP 1: Clearing existing youth club data...")
        
        youth_club_columns = [
            'youth_club_members', 'youth_club_country', 'youth_club_league', 
            'youth_club_league_tier', 'youth_club_url', 'youth_club_date_of_birth'
        ]
        
        df_cleared = df.copy()
        for col in youth_club_columns:
            if col in df_cleared.columns:
                df_cleared[col] = np.nan
                print(f"   ✅ Cleared {col}")
        
        # Step 2: Create club mapping
        club_mapping_by_name, club_mapping_by_clean_name = create_club_mapping()
        
        if not club_mapping_by_name:
            print("❌ Failed to create club mapping")
            return None
        
        # Step 3: Re-map using cleaned names
        print(f"\n🔧 STEP 2: Re-mapping with cleaned names...")
        
        # Get unique cleaned youth clubs
        unique_cleaned_clubs = df_cleared['youth_club_cleaned'].dropna().unique()
        print(f"   📊 Unique cleaned youth clubs: {len(unique_cleaned_clubs)}")
        
        # Create mapping for cleaned names
        cleaned_club_mapping = {}
        matched_count = 0
        
        for cleaned_club in unique_cleaned_clubs:
            club_data = find_club_match(cleaned_club, club_mapping_by_name, club_mapping_by_clean_name)
            if club_data:
                cleaned_club_mapping[cleaned_club] = club_data
                matched_count += 1
        
        print(f"   📊 Successfully matched {matched_count}/{len(unique_cleaned_clubs)} cleaned youth clubs")
        
        # Step 4: Apply correct data to all records
        print(f"\n🔧 STEP 3: Applying correct data to all records...")
        
        df_final = df_cleared.copy()
        updated_count = 0
        
        # Process records with cleaned youth clubs
        records_with_youth_clubs = df_final[df_final['youth_club_cleaned'].notna()]
        print(f"   📊 Records with cleaned youth clubs: {len(records_with_youth_clubs)}")
        
        for idx, row in records_with_youth_clubs.iterrows():
            cleaned_youth_club = row['youth_club_cleaned']
            
            if cleaned_youth_club in cleaned_club_mapping:
                club_data = cleaned_club_mapping[cleaned_youth_club]
                
                # Update all youth club columns
                df_final.at[idx, 'youth_club_members'] = club_data['members']
                df_final.at[idx, 'youth_club_country'] = club_data['country']
                df_final.at[idx, 'youth_club_league'] = club_data['league_name']
                df_final.at[idx, 'youth_club_league_tier'] = club_data['league_tier']
                df_final.at[idx, 'youth_club_url'] = club_data['url']
                df_final.at[idx, 'youth_club_date_of_birth'] = club_data['founded']
                
                updated_count += 1
        
        print(f"   ✅ Updated {updated_count} records with correct youth club data")
        
        # Show final statistics
        print(f"\n📊 FINAL STATISTICS:")
        for col in youth_club_columns:
            if col in df_final.columns:
                filled = df_final[col].notna().sum()
                total = len(df_final)
                coverage = (filled / total) * 100
                print(f"   {col}: {filled}/{total} ({coverage:.1f}%)")
        
        # Show examples of final data
        print(f"\n📋 EXAMPLES OF FINAL DATA:")
        final_examples = df_final[
            df_final['youth_club_cleaned'].notna() & 
            df_final['youth_club_members'].notna()
        ][
            ['full_name', 'youth_club', 'youth_club_cleaned', 'youth_club_members', 
             'youth_club_country', 'youth_club_league', 'youth_club_league_tier']
        ].head(10)
        
        for _, row in final_examples.iterrows():
            print(f"   • {row['full_name']}: '{row['youth_club']}' → '{row['youth_club_cleaned']}'")
            print(f"     Members: {row['youth_club_members']}, Country: {row['youth_club_country']}")
            print(f"     League: {row['youth_club_league']} ({row['youth_club_league_tier']})")
        
        # Show unmatched cleaned clubs
        unmatched_clubs = set(unique_cleaned_clubs) - set(cleaned_club_mapping.keys())
        if unmatched_clubs:
            print(f"\n⚠️  UNMATCHED CLEANED YOUTH CLUBS ({len(unmatched_clubs)}):")
            for club in sorted(list(unmatched_clubs))[:20]:  # Show first 20
                print(f"   - '{club}'")
            if len(unmatched_clubs) > 20:
                print(f"   ... and {len(unmatched_clubs) - 20} more")
        
        # Save final database
        output_file = 'db_players_and_training_clubs_final_cleaned.csv'
        df_final.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved final cleaned database to: {output_file}")
        print(f"📊 Total records: {len(df_final)}")
        
        return df_final
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting re-mapping of cleaned youth clubs...")
    
    try:
        final_df = remap_cleaned_youth_clubs()
        
        if final_df is not None:
            print(f"\n🎉 Successfully completed re-mapping of cleaned youth clubs!")
            print(f"📁 Output file: db_players_and_training_clubs_final_cleaned.csv")
        else:
            print(f"\n❌ Failed to complete re-mapping of cleaned youth clubs")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
