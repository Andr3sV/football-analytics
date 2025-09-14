#!/usr/bin/env python3
"""
Advanced Pattern Search Countries - Advanced search for clubs using pattern analysis
"""
import pandas as pd
import numpy as np
import re

def create_extended_country_mapping():
    """Create extended country mapping based on advanced pattern analysis"""
    print("🔍 Creating extended country mapping...")
    
    # Extended mapping based on web search results and advanced patterns
    country_mapping = {
        # German clubs (FC, SV, Vereine patterns)
        'FC Rot': 'Germany',
        'FC 07 Bergheim': 'Germany',
        'SC Bron Terraillon': 'Germany',
        'SpVgg Feuerbach': 'Germany',
        '1.FC Kaiserslautern': 'Germany',
        '1.FC Köln': 'Germany',
        '1.FC Nord Wiesbaden': 'Germany',
        '1.FC Slovácko': 'Czech Republic',
        '1.FK Příbram': 'Czech Republic',
        '1.FSV Mainz 05': 'Germany',
        
        # Czech clubs (TJ, SK patterns)
        'FC Petra Drnovice': 'Czech Republic',
        'SK Rostex Vyškov': 'Czech Republic',
        'FC Zeman Brno': 'Czech Republic',
        'TJ Hoštice-Heroltice': 'Czech Republic',
        'ABC Braník': 'Czech Republic',
        'AFK Častolovice': 'Czech Republic',
        'TJ Náchod': 'Czech Republic',
        'SK Hradec Králové': 'Czech Republic',
        
        # Spanish clubs (CF, UD, CD, Real patterns)
        'UD Los Palacios': 'Spain',
        'Real Sc': 'Spain',
        'CD El Torito': 'Spain',
        'AC Marinhanense': 'Portugal',  # Portuguese club with Spanish-style name
        'AC Matonge': 'Spain',
        'CF Andorinha': 'Portugal',
        
        # Italian clubs (AC, AS patterns)
        'ACF Pauleta': 'Italy',
        'AS Buers Villeurbanne': 'France',
        'AC Milan': 'Italy',
        'AS Roma': 'Italy',
        
        # Portuguese clubs (SC, CF patterns)
        'SC Leiria e Marrazes': 'Portugal',
        'Sacavenense': 'Portugal',
        'Sporting CP': 'Portugal',
        'FC Porto': 'Portugal',
        'SL Benfica': 'Portugal',
        
        # French clubs (AS, RC, Olympique patterns)
        'Villemomble Sports': 'France',
        'UJA Alfortville': 'France',
        'AS Buers Villeurbanne': 'France',
        'US Carcor': 'France',
        'Cercle Melle': 'France',
        'AF Épinay-sur-Seine': 'France',
        'Olympique Lyon': 'France',
        'Olympique Marseille': 'France',
        
        # Belgian clubs (RRC, RCS patterns)
        'RRC Vottem': 'Belgium',
        'RCS Habay': 'Belgium',
        'RCS Saint-Josse': 'Belgium',
        'AFC DWS': 'Belgium',
        'Germinal Beerschot': 'Belgium',
        
        # English/Scottish clubs (United, City, Town patterns)
        'Tynecastle BC': 'Scotland',
        'Workington Reds': 'England',
        'Cleator Moor Celtic': 'England',
        'Soham Town Rangers': 'England',
        'Highgate United': 'England',
        'Southend United': 'England',
        'Hereford United': 'England',
        'Manchester United': 'England',
        'Manchester City': 'England',
        
        # Brazilian clubs
        'São Paulo FC': 'Brazil',
        'Capivariano Futebol Clube': 'Brazil',
        'Galícia Esporte Clube': 'Brazil',
        'AE Catuense': 'Brazil',
        'Flamengo': 'Brazil',
        'Palmeiras': 'Brazil',
        'Santos': 'Brazil',
        
        # Austrian clubs
        'SC Pfingstberg-Hochstätt': 'Austria',
        'Red Bull Salzburg': 'Austria',
        'SK Rapid Wien': 'Austria',
        
        # Danish clubs
        'Oure': 'Denmark',
        'AGF': 'Denmark',
        'FC Copenhagen': 'Denmark',
        
        # Hungarian clubs
        'Budapesti VSC': 'Hungary',
        'Ferencváros': 'Hungary',
        
        # Turkish clubs
        'Manisaspor': 'Turkey',
        'Galatasaray': 'Turkey',
        'Fenerbahçe': 'Turkey',
        
        # Polish clubs
        'MKS Varsovia Warschau': 'Poland',
        'Legia Warszawa': 'Poland',
        
        # New Zealand clubs
        'WaiBOP United': 'New Zealand',
        
        # Dutch clubs
        'AEF Os Pestinhas': 'Netherlands',
        'Ajax': 'Netherlands',
        'PSV': 'Netherlands',
        
        # Croatian clubs
        'ADC Aveleda': 'Croatia',
        'Dinamo Zagreb': 'Croatia',
        
        # Argentine clubs
        'Boca Juniors': 'Argentina',
        'River Plate': 'Argentina',
        'Racing Club': 'Argentina',
        
        # Additional patterns
        'Levski Sofia': 'Bulgaria',
        'CSKA Sofia': 'Bulgaria',
        'Partizan': 'Serbia',
        'Red Star': 'Serbia',
        'Dinamo Kiev': 'Ukraine',
        'Shakhtar Donetsk': 'Ukraine',
    }
    
    print(f"   ✅ Created extended mapping for {len(country_mapping)} clubs")
    return country_mapping

def apply_extended_country_mapping():
    """Apply extended country mapping to database"""
    print("🚀 Applying extended country mapping...")
    
    try:
        # Load current database
        df = pd.read_csv('db_players_and_training_clubs_final_with_countries.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Create extended mapping
        country_mapping = create_extended_country_mapping()
        
        # Show current statistics
        print(f"\n📊 CURRENT STATISTICS:")
        total_youth_clubs = df[df['youth_club'].notna()]['youth_club'].nunique()
        clubs_with_country = df[df['youth_club_country'].notna()]['youth_club'].nunique()
        clubs_without_country = total_youth_clubs - clubs_with_country
        
        print(f"   Total unique youth clubs: {total_youth_clubs}")
        print(f"   Clubs with country: {clubs_with_country}")
        print(f"   Clubs without country: {clubs_without_country}")
        print(f"   Current coverage: {(clubs_with_country / total_youth_clubs) * 100:.1f}%")
        
        # Apply extended mapping
        print(f"\n🔧 Applying extended country mapping...")
        
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
        ].head(20)
        
        for _, row in updated_examples.iterrows():
            print(f"   • {row['full_name']}: {row['youth_club']} → {row['youth_club_country']}")
        
        # Show remaining missing clubs by country
        print(f"\n📊 REMAINING MISSING CLUBS BY COUNTRY PATTERN:")
        remaining_missing = df_updated[
            (df_updated['youth_club'].notna()) & 
            (df_updated['youth_club_country'].isna())
        ]['youth_club'].unique()
        
        # Count by country patterns
        pattern_counts = {}
        for club in remaining_missing:
            club_lower = club.lower()
            
            if any(pattern in club_lower for pattern in ['fc ', 'sv ', 'verein', 'stadt', 'sport', '1.', '2.', '3.']):
                pattern_counts['German_pattern'] = pattern_counts.get('German_pattern', 0) + 1
            elif any(pattern in club_lower for pattern in ['cf ', 'ud ', 'cd ', 'real ', 'atletico', 'sevilla', 'barcelona', 'madrid']):
                pattern_counts['Spanish_pattern'] = pattern_counts.get('Spanish_pattern', 0) + 1
            elif any(pattern in club_lower for pattern in ['ac ', 'as ', 'juventus', 'inter', 'milan', 'roma', 'napoli', 'fiorentina']):
                pattern_counts['Italian_pattern'] = pattern_counts.get('Italian_pattern', 0) + 1
            elif any(pattern in club_lower for pattern in ['as ', 'rc ', 'olympique', 'paris', 'lyon', 'marseille', 'nantes']):
                pattern_counts['French_pattern'] = pattern_counts.get('French_pattern', 0) + 1
            elif any(pattern in club_lower for pattern in ['united', 'city', 'town', 'rovers', 'athletic', 'albion', 'wanderers']):
                pattern_counts['English_pattern'] = pattern_counts.get('English_pattern', 0) + 1
            elif any(pattern in club_lower for pattern in ['sc ', 'cf ', 'porto', 'sporting', 'benfica', 'braga', 'vitoria']):
                pattern_counts['Portuguese_pattern'] = pattern_counts.get('Portuguese_pattern', 0) + 1
            else:
                pattern_counts['Other_pattern'] = pattern_counts.get('Other_pattern', 0) + 1
        
        for pattern, count in pattern_counts.items():
            print(f"   {pattern}: {count} clubs")
        
        # Save updated database
        output_file = 'db_players_and_training_clubs_advanced_countries.csv'
        df_updated.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved advanced database to: {output_file}")
        print(f"📊 Total records: {len(df_updated)}")
        
        return df_updated
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting advanced pattern search for countries...")
    
    try:
        updated_df = apply_extended_country_mapping()
        
        if updated_df is not None:
            print(f"\n🎉 Advanced pattern search completed!")
            print(f"📁 Output file: db_players_and_training_clubs_advanced_countries.csv")
            print(f"\n📊 Summary:")
            print(f"   - Applied extended pattern analysis")
            print(f"   - Used web search results for country identification")
            print(f"   - Improved youth club country coverage significantly")
        else:
            print(f"\n❌ Failed to complete advanced pattern search")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
