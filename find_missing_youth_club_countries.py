#!/usr/bin/env python3
"""
Find Missing Youth Club Countries - Identify youth clubs without country data
and search the web to find their countries
"""
import pandas as pd
import numpy as np
import re
import time
from urllib.parse import quote_plus

def identify_missing_countries():
    """Identify youth clubs without country data"""
    print("🔍 Identifying youth clubs without country data...")
    
    try:
        # Load the final cleaned database
        df = pd.read_csv('db_players_and_training_clubs_final_cleaned.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Get records with youth clubs but missing country
        missing_country_records = df[
            (df['youth_club'].notna()) & 
            (df['youth_club_country'].isna())
        ]
        
        print(f"   📊 Records with youth clubs but missing country: {len(missing_country_records)}")
        
        # Get unique youth clubs without country
        unique_missing_clubs = missing_country_records['youth_club'].dropna().unique()
        print(f"   📊 Unique youth clubs without country: {len(unique_missing_clubs)}")
        
        # Show examples
        print(f"\n📋 EXAMPLES OF MISSING COUNTRIES:")
        for i, club in enumerate(unique_missing_clubs[:20]):
            # Count how many players have this club
            player_count = len(missing_country_records[missing_country_records['youth_club'] == club])
            print(f"   {i+1:2d}. {club} ({player_count} players)")
        
        if len(unique_missing_clubs) > 20:
            print(f"   ... and {len(unique_missing_clubs) - 20} more clubs")
        
        # Create a mapping file for manual research
        missing_clubs_df = pd.DataFrame({
            'youth_club': unique_missing_clubs,
            'country_found': '',
            'source': '',
            'notes': ''
        })
        
        output_file = 'missing_youth_club_countries.csv'
        missing_clubs_df.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved missing clubs list to: {output_file}")
        print(f"📊 Total missing clubs: {len(unique_missing_clubs)}")
        
        # Show statistics
        total_youth_clubs = df[df['youth_club'].notna()]['youth_club'].nunique()
        clubs_with_country = df[df['youth_club_country'].notna()]['youth_club'].nunique()
        clubs_without_country = len(unique_missing_clubs)
        
        print(f"\n📊 YOUTH CLUB COUNTRY COVERAGE:")
        print(f"   Total unique youth clubs: {total_youth_clubs}")
        print(f"   Clubs with country: {clubs_with_country}")
        print(f"   Clubs without country: {clubs_without_country}")
        print(f"   Coverage: {(clubs_with_country / total_youth_clubs) * 100:.1f}%")
        
        return missing_clubs_df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_club_patterns():
    """Analyze patterns in missing club names to identify potential countries"""
    print(f"\n🔍 Analyzing patterns in missing club names...")
    
    try:
        # Load the final cleaned database
        df = pd.read_csv('db_players_and_training_clubs_final_cleaned.csv')
        
        # Get unique missing clubs
        missing_country_records = df[
            (df['youth_club'].notna()) & 
            (df['youth_club_country'].isna())
        ]
        unique_missing_clubs = missing_country_records['youth_club'].dropna().unique()
        
        print(f"   📊 Analyzing {len(unique_missing_clubs)} missing clubs...")
        
        # Pattern analysis
        patterns = {
            'German_clubs': [],
            'Spanish_clubs': [],
            'Italian_clubs': [],
            'French_clubs': [],
            'English_clubs': [],
            'Portuguese_clubs': [],
            'Other_patterns': []
        }
        
        for club in unique_missing_clubs:
            club_lower = club.lower()
            
            # German patterns
            if any(pattern in club_lower for pattern in ['fc', 'sv', '1.', '2.', '3.', 'verein', 'stadt', 'sport']):
                patterns['German_clubs'].append(club)
            # Spanish patterns
            elif any(pattern in club_lower for pattern in ['cf', 'ud', 'cd', 'real', 'atletico', 'sevilla']):
                patterns['Spanish_clubs'].append(club)
            # Italian patterns
            elif any(pattern in club_lower for pattern in ['ac', 'as', 'juventus', 'inter', 'milan']):
                patterns['Italian_clubs'].append(club)
            # French patterns
            elif any(pattern in club_lower for pattern in ['as', 'rc', 'olympique', 'paris', 'lyon']):
                patterns['French_clubs'].append(club)
            # English patterns
            elif any(pattern in club_lower for pattern in ['united', 'city', 'town', 'rovers', 'athletic']):
                patterns['English_clubs'].append(club)
            # Portuguese patterns
            elif any(pattern in club_lower for pattern in ['sc', 'cf', 'porto', 'sporting', 'benfica']):
                patterns['Portuguese_clubs'].append(club)
            else:
                patterns['Other_patterns'].append(club)
        
        # Show pattern analysis
        print(f"\n📋 PATTERN ANALYSIS:")
        for pattern_name, clubs in patterns.items():
            if clubs:
                print(f"   {pattern_name}: {len(clubs)} clubs")
                for club in clubs[:5]:  # Show first 5
                    print(f"      - {club}")
                if len(clubs) > 5:
                    print(f"      ... and {len(clubs) - 5} more")
        
        return patterns
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_search_queries():
    """Create search queries for missing clubs"""
    print(f"\n🔍 Creating search queries for missing clubs...")
    
    try:
        # Load missing clubs
        missing_clubs_df = pd.read_csv('missing_youth_club_countries.csv')
        
        print(f"   📊 Creating queries for {len(missing_clubs_df)} clubs...")
        
        # Create search queries
        search_queries = []
        
        for _, row in missing_clubs_df.iterrows():
            club_name = row['youth_club']
            
            # Create different search query variations
            queries = [
                f'"{club_name}" football club country',
                f'"{club_name}" soccer club location',
                f'"{club_name}" football team country',
                f'"{club_name}" club wikipedia',
                f'"{club_name}" transfermarkt'
            ]
            
            for query in queries:
                search_queries.append({
                    'youth_club': club_name,
                    'search_query': query,
                    'url': f'https://www.google.com/search?q={quote_plus(query)}'
                })
        
        # Save search queries
        queries_df = pd.DataFrame(search_queries)
        queries_file = 'youth_club_search_queries.csv'
        queries_df.to_csv(queries_file, index=False)
        
        print(f"   💾 Saved {len(search_queries)} search queries to: {queries_file}")
        
        # Show examples
        print(f"\n📋 EXAMPLE SEARCH QUERIES:")
        for i, query in enumerate(search_queries[:10]):
            print(f"   {i+1:2d}. {query['search_query']}")
        
        return queries_df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting analysis of missing youth club countries...")
    
    try:
        # Step 1: Identify missing countries
        missing_clubs_df = identify_missing_countries()
        
        if missing_clubs_df is not None:
            # Step 2: Analyze patterns
            patterns = analyze_club_patterns()
            
            # Step 3: Create search queries
            queries_df = create_search_queries()
            
            print(f"\n🎉 Analysis completed!")
            print(f"📁 Files created:")
            print(f"   - missing_youth_club_countries.csv")
            print(f"   - youth_club_search_queries.csv")
            print(f"\n📊 Next steps:")
            print(f"   1. Use the search queries to research missing countries")
            print(f"   2. Fill in the missing_youth_club_countries.csv file")
            print(f"   3. Run update script to apply the found countries")
        else:
            print(f"\n❌ Failed to analyze missing countries")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
