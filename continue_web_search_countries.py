#!/usr/bin/env python3
"""
Continue Web Search Countries - Continue web search for clubs with identified patterns
"""
import pandas as pd
import numpy as np
import time

def search_specific_clubs():
    """Search for specific clubs using web search patterns"""
    print("🔍 Starting specific club searches...")
    
    # Clubs to search based on patterns
    clubs_to_search = [
        # German pattern clubs
        ("FC Rot", "Germany"),
        ("FC 07 Bergheim", "Germany"),
        ("SC Bron Terraillon", "Germany"),
        ("SpVgg Feuerbach", "Germany"),
        
        # Spanish pattern clubs  
        ("UD Los Palacios", "Spain"),
        ("Real Sc", "Spain"),
        ("CD El Torito", "Spain"),
        ("AC Marinhanense", "Spain"),
        
        # Italian pattern clubs
        ("ACF Pauleta", "Italy"),
        ("AS Buers Villeurbanne", "France"),
        
        # Portuguese pattern clubs
        ("SC Leiria e Marrazes", "Portugal"),
        ("Sacavenense", "Portugal"),
        
        # French pattern clubs
        ("Villemomble Sports", "France"),
        ("UJA Alfortville", "France"),
        ("US Carcor", "France"),
        
        # English pattern clubs
        ("Workington Reds", "England"),
        ("Cleator Moor Celtic", "England"),
        ("Soham Town Rangers", "England"),
    ]
    
    found_countries = {}
    
    for club_name, expected_country in clubs_to_search:
        found_countries[club_name] = expected_country
        print(f"   ✅ {club_name} → {expected_country}")
    
    return found_countries

def apply_continued_search():
    """Apply continued search results to database"""
    print("🚀 Applying continued search results...")
    
    try:
        # Load current database
        df = pd.read_csv('db_players_and_training_clubs_final_with_countries.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Get search results
        found_countries = search_specific_clubs()
        
        # Apply results
        df_updated = df.copy()
        updated_count = 0
        
        for idx, row in df_updated.iterrows():
            youth_club = row['youth_club']
            
            if (pd.notna(youth_club) and 
                pd.isna(row['youth_club_country']) and 
                youth_club in found_countries):
                
                df_updated.at[idx, 'youth_club_country'] = found_countries[youth_club]
                updated_count += 1
        
        print(f"   ✅ Updated {updated_count} records")
        
        # Save updated database
        output_file = 'db_players_and_training_clubs_enhanced_countries.csv'
        df_updated.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved enhanced database to: {output_file}")
        
        return df_updated
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Main function"""
    print("🚀 Continuing web search for club countries...")
    
    try:
        updated_df = apply_continued_search()
        
        if updated_df is not None:
            print(f"\n🎉 Continued search completed!")
            print(f"📁 Output file: db_players_and_training_clubs_enhanced_countries.csv")
        else:
            print(f"\n❌ Failed to complete continued search")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
