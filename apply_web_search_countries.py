#!/usr/bin/env python3
"""
Apply Web Search Countries - Apply found countries from web search to main database
"""
import pandas as pd
import numpy as np
import time

def create_country_mapping_from_patterns():
    """Create country mapping based on patterns and known data"""
    print("🔍 Creating country mapping from patterns and known data...")
    
    # Based on web search results and pattern analysis
    country_mapping = {
        # German clubs
        'FC Rot': 'Germany',
        'FC 07 Bergheim': 'Germany',
        'SC Bron Terraillon': 'Germany',
        'FC Petra Drnovice': 'Czech Republic',
        'SK Rostex Vyškov': 'Czech Republic',
        'FC Zeman Brno': 'Czech Republic',
        'TJ Hoštice-Heroltice': 'Czech Republic',
        
        # Spanish clubs
        'CF Andorinha': 'Portugal',  # Portuguese club with Spanish name
        'UD Los Palacios': 'Spain',
        'Real Sc': 'Spain',
        'CD El Torito': 'Spain',
        
        # French clubs
        'Villemomble Sports': 'France',
        'UJA Alfortville': 'France',
        'AS Buers Villeurbanne': 'France',
        'RRC Vottem': 'Belgium',
        'US Carcor': 'France',
        'RCS Habay': 'Belgium',
        'RCS Saint-Josse': 'Belgium',
        'Cercle Melle': 'France',
        
        # English/Scottish clubs
        'Tynecastle BC': 'Scotland',
        'Workington Reds': 'England',
        'Cleator Moor Celtic': 'England',
        'Soham Town Rangers': 'England',
        'Highgate United': 'England',
        'Southend United': 'England',
        'Hereford United': 'England',
        'WaiBOP United': 'New Zealand',
        
        # Brazilian clubs
        'São Paulo FC': 'Brazil',
        'Capivariano Futebol Clube': 'Brazil',
        'Galícia Esporte Clube': 'Brazil',
        'AE Catuense)': 'Brazil',
        
        # Portuguese clubs
        'SC Leiria e Marrazes': 'Portugal',
        'SC Pfingstberg-Hochstätt': 'Austria',
        
        # Other clubs
        'Oure': 'Denmark',
        'Budapesti VSC': 'Hungary',
        'Manisaspor': 'Turkey',
        'SpVgg Feuerbach': 'Germany',
        'MKS Varsovia Warschau': 'Poland',
        'Germinal Beerschot': 'Belgium',
        'Sacavenense;': 'Portugal',
    }
    
    print(f"   ✅ Created mapping for {len(country_mapping)} clubs")
    return country_mapping

def apply_country_mapping():
    """Apply country mapping to the main database"""
    print("🚀 Applying country mapping to main database...")
    
    try:
        # Load the main database
        print("🔄 Loading main database...")
        df = pd.read_csv('db_players_and_training_clubs_final_cleaned.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Create country mapping
        country_mapping = create_country_mapping_from_patterns()
        
        # Show current statistics
        print(f"\n📊 CURRENT STATISTICS:")
        total_youth_clubs = df[df['youth_club'].notna()]['youth_club'].nunique()
        clubs_with_country = df[df['youth_club_country'].notna()]['youth_club'].nunique()
        clubs_without_country = total_youth_clubs - clubs_with_country
        
        print(f"   Total unique youth clubs: {total_youth_clubs}")
        print(f"   Clubs with country: {clubs_with_country}")
        print(f"   Clubs without country: {clubs_without_country}")
        print(f"   Current coverage: {(clubs_with_country / total_youth_clubs) * 100:.1f}%")
        
        # Apply country mapping
        print(f"\n🔧 Applying country mapping...")
        
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
        ].head(10)
        
        for _, row in updated_examples.iterrows():
            print(f"   • {row['full_name']}: {row['youth_club']} → {row['youth_club_country']}")
        
        # Save updated database
        output_file = 'db_players_and_training_clubs_with_web_countries.csv'
        df_updated.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved updated database to: {output_file}")
        print(f"📊 Total records: {len(df_updated)}")
        
        return df_updated
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting application of web search countries...")
    
    try:
        updated_df = apply_country_mapping()
        
        if updated_df is not None:
            print(f"\n🎉 Successfully applied web search countries!")
            print(f"📁 Output file: db_players_and_training_clubs_with_web_countries.csv")
            print(f"\n📊 Next steps:")
            print(f"   1. Continue web search for more missing countries")
            print(f"   2. Manually verify any uncertain matches")
            print(f"   3. Apply additional country mappings as found")
        else:
            print(f"\n❌ Failed to apply web search countries")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
