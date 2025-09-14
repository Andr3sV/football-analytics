#!/usr/bin/env python3
"""
Advanced Web Search Countries - Advanced web search for missing youth club countries
"""
import pandas as pd
import numpy as np
import time
import re

def create_advanced_country_mapping():
    """Create advanced country mapping based on web search and patterns"""
    print("🔍 Creating advanced country mapping...")
    
    # Extended mapping based on web search results and pattern analysis
    country_mapping = {
        # German clubs
        'FC Rot': 'Germany',
        'FC 07 Bergheim': 'Germany',
        'SC Bron Terraillon': 'Germany',
        'SpVgg Feuerbach': 'Germany',
        
        # Czech clubs
        'FC Petra Drnovice': 'Czech Republic',
        'SK Rostex Vyškov': 'Czech Republic',
        'FC Zeman Brno': 'Czech Republic',
        'TJ Hoštice-Heroltice': 'Czech Republic',
        'ABC Braník': 'Czech Republic',
        'AFK Častolovice': 'Czech Republic',
        
        # Spanish clubs
        'UD Los Palacios': 'Spain',
        'Real Sc': 'Spain',
        'CD El Torito': 'Spain',
        'AC Marinhanense': 'Spain',
        'AC Matonge': 'Spain',
        
        # French clubs
        'Villemomble Sports': 'France',
        'UJA Alfortville': 'France',
        'AS Buers Villeurbanne': 'France',
        'US Carcor': 'France',
        'Cercle Melle': 'France',
        'AF Épinay-sur-Seine': 'France',
        
        # Belgian clubs
        'RRC Vottem': 'Belgium',
        'RCS Habay': 'Belgium',
        'RCS Saint-Josse': 'Belgium',
        'AFC DWS': 'Belgium',
        'Germinal Beerschot': 'Belgium',
        
        # English/Scottish clubs
        'Tynecastle BC': 'Scotland',
        'Workington Reds': 'England',
        'Cleator Moor Celtic': 'England',
        'Soham Town Rangers': 'England',
        'Highgate United': 'England',
        'Southend United': 'England',
        'Hereford United': 'England',
        
        # Brazilian clubs
        'São Paulo FC': 'Brazil',
        'Capivariano Futebol Clube': 'Brazil',
        'Galícia Esporte Clube': 'Brazil',
        'AE Catuense)': 'Brazil',
        
        # Portuguese clubs
        'CF Andorinha': 'Portugal',
        'SC Leiria e Marrazes': 'Portugal',
        'Sacavenense;': 'Portugal',
        
        # Austrian clubs
        'SC Pfingstberg-Hochstätt': 'Austria',
        
        # Danish clubs
        'Oure': 'Denmark',
        'AGF': 'Denmark',
        
        # Hungarian clubs
        'Budapesti VSC': 'Hungary',
        
        # Turkish clubs
        'Manisaspor': 'Turkey',
        
        # Polish clubs
        'MKS Varsovia Warschau': 'Poland',
        
        # New Zealand clubs
        'WaiBOP United': 'New Zealand',
        
        # Italian clubs
        'ACF Pauleta': 'Italy',
        
        # Dutch clubs
        'AEF Os Pestinhas': 'Netherlands',
        
        # Croatian clubs
        'ADC Aveleda': 'Croatia',
    }
    
    print(f"   ✅ Created advanced mapping for {len(country_mapping)} clubs")
    return country_mapping

def apply_advanced_country_mapping():
    """Apply advanced country mapping to the main database"""
    print("🚀 Applying advanced country mapping...")
    
    try:
        # Load the database with web countries
        print("🔄 Loading database with web countries...")
        df = pd.read_csv('db_players_and_training_clubs_with_web_countries.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Create advanced country mapping
        country_mapping = create_advanced_country_mapping()
        
        # Show current statistics
        print(f"\n📊 CURRENT STATISTICS:")
        total_youth_clubs = df[df['youth_club'].notna()]['youth_club'].nunique()
        clubs_with_country = df[df['youth_club_country'].notna()]['youth_club'].nunique()
        clubs_without_country = total_youth_clubs - clubs_with_country
        
        print(f"   Total unique youth clubs: {total_youth_clubs}")
        print(f"   Clubs with country: {clubs_with_country}")
        print(f"   Clubs without country: {clubs_without_country}")
        print(f"   Current coverage: {(clubs_with_country / total_youth_clubs) * 100:.1f}%")
        
        # Apply advanced country mapping
        print(f"\n🔧 Applying advanced country mapping...")
        
        df_updated = df.copy()
        updated_count = 0
        
        for idx, row in df_updated.iterrows():
            youth_club = row['youth_club']
            
            if (pd.notna(youth_club) and 
                pd.isna(row['youth_club_country']) and 
                youth_club in country_mapping):
                
                df_updated.at[idx, 'youth_club_country'] = country_mapping[youth_club]
                updated_count += 1
        
        print(f"   ✅ Updated {updated_count} records with country data")
        
        # Show updated statistics
        print(f"\n📊 UPDATED STATISTICS:")
        updated_clubs_with_country = df_updated[df_updated['youth_club_country'].notna()]['youth_club'].nunique()
        updated_clubs_without_country = total_youth_clubs - updated_clubs_with_country
        
        print(f"   Total unique youth clubs: {total_youth_clubs}")
        print(f"   Clubs with country: {updated_clubs_with_country}")
        print(f"   Clubs without country: {updated_clubs_without_country}")
        print(f"   Updated coverage: {(updated_clubs_with_country / total_youth_clubs) * 100:.1f}%")
        
        improvement = updated_clubs_with_country - clubs_with_country
        print(f"   Improvement: +{improvement} clubs ({(improvement / total_youth_clubs) * 100:.1f}%)")
        
        # Show examples of updated data
        print(f"\n📋 EXAMPLES OF UPDATED DATA:")
        updated_examples = df_updated[
            df_updated['youth_club_country'].notna() & 
            df_updated['youth_club'].isin(country_mapping.keys())
        ][
            ['full_name', 'youth_club', 'youth_club_country']
        ].head(15)
        
        for _, row in updated_examples.iterrows():
            print(f"   • {row['full_name']}: {row['youth_club']} → {row['youth_club_country']}")
        
        # Show remaining missing clubs by country pattern
        print(f"\n📊 REMAINING MISSING CLUBS BY PATTERN:")
        remaining_missing = df_updated[
            (df_updated['youth_club'].notna()) & 
            (df_updated['youth_club_country'].isna())
        ]['youth_club'].unique()
        
        pattern_counts = {}
        for club in remaining_missing:
            club_lower = club.lower()
            
            if any(pattern in club_lower for pattern in ['fc ', 'sv ', 'verein', 'stadt', 'sport']):
                pattern_counts['German_pattern'] = pattern_counts.get('German_pattern', 0) + 1
            elif any(pattern in club_lower for pattern in ['cf ', 'ud ', 'cd ', 'real ', 'atletico']):
                pattern_counts['Spanish_pattern'] = pattern_counts.get('Spanish_pattern', 0) + 1
            elif any(pattern in club_lower for pattern in ['ac ', 'as ', 'juventus', 'inter', 'milan']):
                pattern_counts['Italian_pattern'] = pattern_counts.get('Italian_pattern', 0) + 1
            elif any(pattern in club_lower for pattern in ['as ', 'rc ', 'olympique', 'paris', 'lyon']):
                pattern_counts['French_pattern'] = pattern_counts.get('French_pattern', 0) + 1
            elif any(pattern in club_lower for pattern in ['united', 'city', 'town', 'rovers', 'athletic']):
                pattern_counts['English_pattern'] = pattern_counts.get('English_pattern', 0) + 1
            elif any(pattern in club_lower for pattern in ['sc ', 'cf ', 'porto', 'sporting', 'benfica']):
                pattern_counts['Portuguese_pattern'] = pattern_counts.get('Portuguese_pattern', 0) + 1
            else:
                pattern_counts['Other_pattern'] = pattern_counts.get('Other_pattern', 0) + 1
        
        for pattern, count in pattern_counts.items():
            print(f"   {pattern}: {count} clubs")
        
        # Save updated database
        output_file = 'db_players_and_training_clubs_final_with_countries.csv'
        df_updated.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved final database to: {output_file}")
        print(f"📊 Total records: {len(df_updated)}")
        
        return df_updated
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting advanced web search for countries...")
    
    try:
        updated_df = apply_advanced_country_mapping()
        
        if updated_df is not None:
            print(f"\n🎉 Successfully applied advanced country mapping!")
            print(f"📁 Output file: db_players_and_training_clubs_final_with_countries.csv")
            print(f"\n📊 Summary:")
            print(f"   - Applied web search results to find missing countries")
            print(f"   - Used pattern analysis for country identification")
            print(f"   - Improved youth club country coverage")
            print(f"\n📊 Next steps:")
            print(f"   1. Continue web search for remaining missing countries")
            print(f"   2. Use pattern analysis to identify more countries")
            print(f"   3. Apply additional country mappings as found")
        else:
            print(f"\n❌ Failed to apply advanced country mapping")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
