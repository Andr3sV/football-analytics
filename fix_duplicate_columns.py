#!/usr/bin/env python3
"""
Fix Duplicate Columns - Remove year_in_the_club and keep year_in_the_club_numeric
"""
import pandas as pd

def fix_duplicate_columns():
    """Remove duplicate year_in_the_club column"""
    print("🔄 Loading cleaned dataset...")
    
    # Load the cleaned dataset
    df = pd.read_csv('merged_players_databases_cleaned.csv')
    print(f"   ✅ Loaded {len(df)} players")
    
    print(f"\n📋 Current columns:")
    for i, col in enumerate(df.columns):
        print(f"   {i+1}. {col}")
    
    # Check if both columns exist
    if 'year_in_the_club' in df.columns and 'year_in_the_club_numeric' in df.columns:
        print(f"\n🔧 Removing duplicate column 'year_in_the_club'...")
        
        # Remove the duplicate column
        df = df.drop('year_in_the_club', axis=1)
        
        print(f"   ✅ Removed 'year_in_the_club' column")
        print(f"   ✅ Kept 'year_in_the_club_numeric' column")
        
    else:
        print(f"\n⚠️  One or both columns not found:")
        print(f"   year_in_the_club: {'year_in_the_club' in df.columns}")
        print(f"   year_in_the_club_numeric: {'year_in_the_club_numeric' in df.columns}")
    
    print(f"\n📋 Updated columns:")
    for i, col in enumerate(df.columns):
        print(f"   {i+1}. {col}")
    
    # Save the fixed dataset
    output_file = 'merged_players_databases_cleaned.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved fixed dataset to: {output_file}")
    print(f"📊 Total players: {len(df)}")
    print(f"📊 Total columns: {len(df.columns)}")
    
    return df

def main():
    """Main function"""
    try:
        fixed_df = fix_duplicate_columns()
        
        if fixed_df is not None:
            print(f"\n🎉 Successfully fixed duplicate columns!")
            print(f"📁 Output file: merged_players_databases_cleaned.csv")
        else:
            print(f"\n❌ Failed to fix duplicate columns")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
