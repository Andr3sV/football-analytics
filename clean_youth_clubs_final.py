#!/usr/bin/env python3
"""
Clean Youth Clubs Final - Clean the youth_club column in the final database
to ensure no years remain in parentheses and extract them to from_to and year_in_the_club_numeric
"""
import pandas as pd
import numpy as np
import re

def clean_youth_clubs_final():
    """Clean youth club data in the final database"""
    print("🔄 Loading final database...")
    
    # Load the final database
    df = pd.read_csv('all_players_combined_database_complete_transfer_fields.csv')
    print(f"   ✅ Loaded {len(df)} records from final database")
    
    # Check current youth_club data
    youth_club_count = df['youth_club'].notna().sum()
    print(f"   📊 Records with youth_club data: {youth_club_count}")
    
    print("🔍 Analyzing youth_club data patterns...")
    
    # Show examples of youth_club data with parentheses
    examples_with_parentheses = df[
        df['youth_club'].str.contains(r'\(', na=False)
    ]['youth_club'].head(15).tolist()
    
    print(f"\n📋 EXAMPLES OF YOUTH_CLUB DATA WITH PARENTHESES:")
    for i, club in enumerate(examples_with_parentheses, 1):
        print(f"   {i}. {club}")
    
    # Count records with parentheses
    records_with_parentheses = df['youth_club'].str.contains(r'\(', na=False).sum()
    print(f"\n📊 Records with parentheses in youth_club: {records_with_parentheses}")
    
    if records_with_parentheses == 0:
        print("   ✅ No parentheses found in youth_club column - already clean!")
        return df
    
    print("🔧 Cleaning youth_club data...")
    
    # Create new columns if they don't exist
    if 'from_to' not in df.columns:
        df['from_to'] = None
    if 'year_in_the_club_numeric' not in df.columns:
        df['year_in_the_club_numeric'] = None
    
    # Process each record
    cleaned_count = 0
    errors_count = 0
    
    for idx, row in df.iterrows():
        youth_club = row['youth_club']
        
        if pd.isna(youth_club):
            continue
        
        youth_club_str = str(youth_club).strip()
        
        # Look for year patterns in parentheses
        # Pattern: Club Name (YYYY-YYYY) or Club Name (YYYY)
        year_pattern = r'\(([^)]+)\)'
        year_match = re.search(year_pattern, youth_club_str)
        
        if year_match:
            years_text = year_match.group(1)
            cleaned_count += 1
            
            # Extract the club name (remove everything in parentheses)
            club_name = re.sub(r'\s*\([^)]*\)\s*', '', youth_club_str).strip()
            df.at[idx, 'youth_club'] = club_name
            df.at[idx, 'from_to'] = years_text
            
            # Calculate years in club
            try:
                if '-' in years_text:
                    # Range format: 1998-2004
                    start_year, end_year = years_text.split('-')
                    start_year = int(start_year.strip())
                    end_year = int(end_year.strip())
                    years_in_club = end_year - start_year
                else:
                    # Single year format
                    year = int(years_text.strip())
                    years_in_club = 1
                
                df.at[idx, 'year_in_the_club_numeric'] = years_in_club
                
            except (ValueError, IndexError):
                # If we can't parse the years, set to None
                df.at[idx, 'year_in_the_club_numeric'] = None
                errors_count += 1
                print(f"   ⚠️  Could not parse years: {years_text}")
        
        else:
            # No parentheses found, keep the original club name
            df.at[idx, 'youth_club'] = youth_club_str
            # Keep existing from_to and year_in_the_club_numeric values
    
    print(f"   ✅ Cleaned {cleaned_count} records with parentheses")
    if errors_count > 0:
        print(f"   ⚠️  {errors_count} records had parsing errors")
    
    # Statistics after cleaning
    print(f"\n📊 CLEANING RESULTS:")
    youth_club_cleaned_count = df['youth_club'].notna().sum()
    from_to_count = df['from_to'].notna().sum()
    years_count = df['year_in_the_club_numeric'].notna().sum()
    
    print(f"   Records with youth_club data: {youth_club_cleaned_count}")
    print(f"   Records with from_to data: {from_to_count}")
    print(f"   Records with year_in_the_club_numeric: {years_count}")
    
    # Show examples of cleaned data
    print(f"\n📋 EXAMPLES OF CLEANED DATA:")
    cleaned_examples = df[
        df['from_to'].notna()
    ][
        ['full_name', 'youth_club', 'from_to', 'year_in_the_club_numeric']
    ].head(15)
    
    for _, row in cleaned_examples.iterrows():
        print(f"   • {row['full_name']}: {row['youth_club']} ({row['from_to']}) - {row['year_in_the_club_numeric']} years")
    
    # Analyze year distribution
    if years_count > 0:
        print(f"\n📊 YEAR DISTRIBUTION:")
        years_stats = df['year_in_the_club_numeric'].describe()
        print(f"   Average years in youth club: {years_stats.get('mean', 'N/A'):.1f}" if 'mean' in years_stats else "   Average years in youth club: N/A")
        print(f"   Median years: {years_stats.get('50%', 'N/A'):.1f}" if '50%' in years_stats else "   Median years: N/A")
        print(f"   Min years: {years_stats.get('min', 'N/A'):.0f}" if 'min' in years_stats else "   Min years: N/A")
        print(f"   Max years: {years_stats.get('max', 'N/A'):.0f}" if 'max' in years_stats else "   Max years: N/A")
        
        # Year ranges
        year_ranges = [
            (0, 2, "1-2 years"),
            (2, 5, "3-5 years"),
            (5, 8, "6-8 years"),
            (8, 15, "9+ years")
        ]
        
        print(f"\n📊 YEARS IN CLUB DISTRIBUTION:")
        for min_years, max_years, label in year_ranges:
            count = df[
                (df['year_in_the_club_numeric'] >= min_years) & 
                (df['year_in_the_club_numeric'] < max_years)
            ].shape[0]
            percentage = (count / len(df)) * 100
            print(f"   {label}: {count:,} records ({percentage:.1f}%)")
    
    # Show examples of different year patterns
    if from_to_count > 0:
        print(f"\n📋 EXAMPLES OF DIFFERENT YEAR PATTERNS:")
        year_examples = df[
            df['from_to'].notna()
        ]['from_to'].value_counts().head(15)
        
        for years, count in year_examples.items():
            print(f"   {years}: {count} records")
    
    # Verify no parentheses remain
    remaining_parentheses = df['youth_club'].str.contains(r'\(', na=False).sum()
    print(f"\n✅ VERIFICATION:")
    print(f"   Records still with parentheses in youth_club: {remaining_parentheses}")
    
    if remaining_parentheses == 0:
        print("   🎉 SUCCESS: All parentheses removed from youth_club column!")
    else:
        print(f"   ⚠️  WARNING: {remaining_parentheses} records still have parentheses")
    
    # Save the cleaned database
    output_file = 'all_players_combined_database_final_cleaned_youth_clubs.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved cleaned database to: {output_file}")
    print(f"📊 Total records: {len(df)}")
    print(f"📊 Records with youth_club data: {youth_club_cleaned_count}")
    print(f"📊 Records with year data: {years_count}")
    
    return df

def main():
    """Main function"""
    print("🚀 Starting final youth clubs cleaning...")
    
    try:
        cleaned_df = clean_youth_clubs_final()
        
        if cleaned_df is not None:
            print(f"\n🎉 Successfully cleaned youth clubs data!")
            print(f"📁 Output file: all_players_combined_database_final_cleaned_youth_clubs.csv")
        else:
            print(f"\n❌ Failed to clean youth clubs data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
