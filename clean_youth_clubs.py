#!/usr/bin/env python3
"""
Clean Youth Clubs Data - Extract structured information from db_yt_Yname column
Creates three new columns: youth-club, from-to, year-in-the-club
"""
import pandas as pd
import re
import numpy as np

def extract_youth_club_info(youth_name):
    """
    Extract youth club information from the db_yt_Yname column
    Returns: (youth_club, from_to, years_in_club)
    """
    if pd.isna(youth_name) or youth_name == '' or youth_name == 'nan':
        return '', '', ''
    
    youth_str = str(youth_name).strip()
    
    # Pattern to match club name with years in parentheses
    # Examples: "Bilzen VV (1997–1999)", "FC Metalist Kharkiv (2012-2015)"
    pattern_with_years = r'^(.+?)\s*\((\d{4})[–\-](\d{4})\)$'
    match_with_years = re.match(pattern_with_years, youth_str)
    
    if match_with_years:
        club_name = match_with_years.group(1).strip()
        from_year = int(match_with_years.group(2))
        to_year = int(match_with_years.group(3))
        
        # Calculate years in club
        years_in_club = to_year - from_year
        
        return club_name, f"{from_year}-{to_year}", str(years_in_club)
    
    # Pattern for single year (e.g., "Club Name (2005)")
    pattern_single_year = r'^(.+?)\s*\((\d{4})\)$'
    match_single_year = re.match(pattern_single_year, youth_str)
    
    if match_single_year:
        club_name = match_single_year.group(1).strip()
        year = match_single_year.group(2)
        
        return club_name, year, "1"
    
    # Pattern for year range with different separators
    # Examples: "Club Name (2009-2013)", "Club Name (2009–2013)"
    pattern_range = r'^(.+?)\s*\((\d{4})[–\-](\d{4})\)$'
    match_range = re.match(pattern_range, youth_str)
    
    if match_range:
        club_name = match_range.group(1).strip()
        from_year = int(match_range.group(2))
        to_year = int(match_range.group(3))
        
        # Calculate years in club
        years_in_club = to_year - from_year
        
        return club_name, f"{from_year}-{to_year}", str(years_in_club)
    
    # Pattern for complex formats like "Club Name (11/2001-2002)"
    pattern_complex = r'^(.+?)\s*\(\d*/\d{4}[–\-]\d{4}\)$'
    match_complex = re.match(pattern_complex, youth_str)
    
    if match_complex:
        club_name = match_complex.group(1).strip()
        # Extract years from the complex format
        year_match = re.search(r'(\d{4})[–\-](\d{4})', youth_str)
        if year_match:
            from_year = int(year_match.group(1))
            to_year = int(year_match.group(2))
            years_in_club = to_year - from_year
            return club_name, f"{from_year}-{to_year}", str(years_in_club)
    
    # If no pattern matches, return the original string as club name
    return youth_str, '', ''

def clean_youth_clubs_data():
    """Clean the youth clubs data in the merged dataset"""
    print("🔄 Loading merged players database...")
    
    # Load the merged dataset
    df = pd.read_csv('merged_players_databases.csv')
    print(f"   ✅ Loaded {len(df)} players")
    
    print(f"\n🔍 Analyzing db_yt_Yname column...")
    
    # Show some examples of the current data
    print(f"📋 Sample of db_yt_Yname data:")
    sample_data = df['db_yt_Yname'].dropna().head(10)
    for i, value in enumerate(sample_data):
        print(f"   {i+1}. {value}")
    
    print(f"\n🔧 Processing youth club information...")
    
    # Apply the extraction function to each row
    youth_info = df['db_yt_Yname'].apply(extract_youth_club_info)
    
    # Split the results into separate columns
    df['youth_club'] = [info[0] for info in youth_info]
    df['from_to'] = [info[1] for info in youth_info]
    df['year_in_the_club'] = [info[2] for info in youth_info]
    
    # Convert year_in_the_club to numeric for analysis
    df['year_in_the_club_numeric'] = pd.to_numeric(df['year_in_the_club'], errors='coerce')
    
    print(f"   ✅ Created three new columns: youth_club, from_to, year_in_the_club")
    
    # Show statistics
    print(f"\n📊 Statistics:")
    print(f"   Total players: {len(df)}")
    print(f"   Players with youth club info: {df['youth_club'].notna().sum()}")
    print(f"   Players with year range info: {df['from_to'].notna().sum()}")
    print(f"   Players with years calculated: {df['year_in_the_club_numeric'].notna().sum()}")
    
    # Show examples of cleaned data
    print(f"\n📋 Sample of cleaned youth club data:")
    sample_df = df[['full_name', 'db_yt_Yname', 'youth_club', 'from_to', 'year_in_the_club']].head(10)
    print(sample_df.to_string(index=False))
    
    # Show distribution of years in club
    print(f"\n📊 Distribution of years in youth clubs:")
    years_dist = df['year_in_the_club_numeric'].value_counts().sort_index()
    print(years_dist.head(15))
    
    # Show clubs with most players
    print(f"\n📊 Top 10 youth clubs by number of players:")
    top_clubs = df['youth_club'].value_counts().head(10)
    print(top_clubs)
    
    # Save the cleaned dataset
    output_file = 'merged_players_databases_cleaned.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved cleaned dataset to: {output_file}")
    print(f"📊 Total players in cleaned dataset: {len(df)}")
    
    # Show summary of changes
    print(f"\n📋 Summary of changes:")
    print(f"   ✅ Added 'youth_club' column - clean club names")
    print(f"   ✅ Added 'from_to' column - year ranges (e.g., 2009-2015)")
    print(f"   ✅ Added 'year_in_the_club' column - calculated years")
    print(f"   ✅ Added 'year_in_the_club_numeric' column - for analysis")
    
    return df

def main():
    """Main function"""
    try:
        cleaned_df = clean_youth_clubs_data()
        
        if cleaned_df is not None:
            print(f"\n🎉 Successfully cleaned youth clubs data!")
            print(f"📁 Output file: merged_players_databases_cleaned.csv")
            print(f"📊 Total players: {len(cleaned_df)}")
        else:
            print(f"\n❌ Failed to clean youth clubs data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
