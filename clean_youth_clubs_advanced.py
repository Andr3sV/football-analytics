#!/usr/bin/env python3
"""
Clean Youth Clubs Advanced - Advanced cleaning of youth club names and re-mapping
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

def main():
    """Main function"""
    print("🚀 Starting advanced youth club cleaning and re-mapping...")
    
    try:
        # Load the fixed database
        print("🔄 Loading fixed database...")
        df = pd.read_csv('db_players_and_training_clubs_fixed.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Show current state
        print(f"\n📊 CURRENT STATE:")
        unique_youth_clubs = df['youth_club'].dropna().unique()
        print(f"   Unique youth clubs: {len(unique_youth_clubs)}")
        
        # Step 1: Clean youth club names
        print(f"\n🧹 STEP 1: Cleaning youth club names...")
        
        df_cleaned = df.copy()
        
        # Apply advanced cleaning
        df_cleaned['youth_club_cleaned'] = df_cleaned['youth_club'].apply(clean_youth_club_name)
        
        # Show examples of cleaning
        print(f"   📋 EXAMPLES OF CLEANING:")
        cleaning_examples = df_cleaned[
            (df_cleaned['youth_club'].notna()) & 
            (df_cleaned['youth_club'] != df_cleaned['youth_club_cleaned'])
        ][['youth_club', 'youth_club_cleaned']].head(10)
        
        for _, row in cleaning_examples.iterrows():
            print(f"      '{row['youth_club']}' → '{row['youth_club_cleaned']}'")
        
        # Count cleaned clubs
        cleaned_clubs = df_cleaned[
            (df_cleaned['youth_club'].notna()) & 
            (df_cleaned['youth_club'] != df_cleaned['youth_club_cleaned'])
        ]
        print(f"   ✅ Cleaned {len(cleaned_clubs)} club names")
        
        # Save intermediate result
        intermediate_file = 'db_players_youth_clubs_cleaned.csv'
        df_cleaned.to_csv(intermediate_file, index=False)
        print(f"   💾 Saved cleaned names to: {intermediate_file}")
        
        print(f"\n🎉 Successfully completed advanced youth club cleaning!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()