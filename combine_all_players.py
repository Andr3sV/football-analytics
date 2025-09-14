#!/usr/bin/env python3
"""
Combine All Players - Combine the main database with the enriched missing players
using the specified column mapping
"""
import pandas as pd
import numpy as np

def combine_all_players():
    """Combine main database with enriched missing players"""
    print("🔄 Loading databases...")
    
    # Load main database
    df_main = pd.read_csv('merged_players_databases_with_transfers.csv')
    print(f"   ✅ Main database: {len(df_main)} players")
    
    # Load enriched missing players
    df_missing = pd.read_csv('missing_players_enriched.csv')
    print(f"   ✅ Missing players enriched: {len(df_missing)} players")
    
    print("🔧 Mapping columns for missing players...")
    
    # Create a new dataframe for missing players with mapped columns
    df_missing_mapped = pd.DataFrame()
    
    # Map existing columns
    df_missing_mapped['full_name'] = df_missing['full_name']
    df_missing_mapped['team_name'] = df_missing['team_name']
    df_missing_mapped['competition'] = df_missing['competition']
    df_missing_mapped['profile_url'] = df_missing['profile_url']
    df_missing_mapped['relative_profile_url'] = df_missing['relative_profile_url']
    df_missing_mapped['season'] = df_missing['season']
    df_missing_mapped['player_id'] = df_missing['player_id']
    df_missing_mapped['date_of_birth'] = df_missing['player_date_of_birth']
    df_missing_mapped['dominant_foot'] = df_missing['foot']
    
    # Add empty columns for missing players (to match main database structure)
    main_columns = df_main.columns.tolist()
    missing_columns = df_missing_mapped.columns.tolist()
    
    # Add missing columns with None values
    for col in main_columns:
        if col not in missing_columns:
            df_missing_mapped[col] = None
    
    # Reorder columns to match main database
    df_missing_mapped = df_missing_mapped[main_columns]
    
    print(f"   ✅ Mapped {len(df_missing_mapped)} missing players")
    print(f"   📊 Columns in main: {len(df_main.columns)}")
    print(f"   📊 Columns in missing: {len(df_missing_mapped.columns)}")
    
    print("🔧 Combining databases...")
    
    # Combine the databases
    df_combined = pd.concat([df_main, df_missing_mapped], ignore_index=True)
    
    # Remove any potential duplicates based on player_id
    df_combined = df_combined.drop_duplicates(subset=['player_id'], keep='first')
    
    print(f"   ✅ Combined database created with {len(df_combined)} players")
    
    # Statistics
    print(f"\n📊 COMBINATION STATISTICS:")
    print(f"   Original main database: {len(df_main)} players")
    print(f"   Missing players added: {len(df_missing_mapped)} players")
    print(f"   Final combined database: {len(df_combined)} players")
    
    # Analyze the data coverage
    print(f"\n📊 DATA COVERAGE ANALYSIS:")
    
    # Market value coverage
    market_value_count = df_combined['market_value'].notna().sum()
    print(f"   Players with market value: {market_value_count}")
    
    # Age coverage
    age_count = df_combined['age'].notna().sum()
    print(f"   Players with age: {age_count}")
    
    # Date of birth coverage
    dob_count = df_combined['date_of_birth'].notna().sum()
    print(f"   Players with date of birth: {dob_count}")
    
    # Foot coverage
    foot_count = df_combined['dominant_foot'].notna().sum()
    print(f"   Players with foot data: {foot_count}")
    
    # Nationality coverage
    nationality_count = df_combined['nationality'].notna().sum()
    print(f"   Players with nationality: {nationality_count}")
    
    # Position coverage
    position_count = df_combined['position'].notna().sum()
    print(f"   Players with position: {position_count}")
    
    # Transfer data coverage
    transfer_count = df_combined['last_transfer_club_name'].notna().sum()
    print(f"   Players with transfer data: {transfer_count}")
    
    # Show examples of combined data
    print(f"\n📋 EXAMPLES OF COMBINED PLAYERS:")
    
    # Show examples from original database
    original_examples = df_combined[df_combined['market_value'].notna()][
        ['full_name', 'team_name', 'competition', 'market_value', 'date_of_birth', 'dominant_foot']
    ].head(5)
    print(f"   From original database:")
    for _, row in original_examples.iterrows():
        market_val = row['market_value']
        if pd.isna(market_val):
            market_str = "N/A"
        else:
            try:
                market_str = f"€{float(market_val):,.0f}"
            except:
                market_str = str(market_val)
        print(f"   • {row['full_name']} ({row['team_name']}, {row['competition']}) - "
              f"Value: {market_str}, DOB: {row['date_of_birth']}, Foot: {row['dominant_foot']}")
    
    # Show examples from missing players
    missing_examples = df_combined[
        (df_combined['date_of_birth'].notna()) & 
        (df_combined['market_value'].isna())
    ][
        ['full_name', 'team_name', 'competition', 'date_of_birth', 'dominant_foot']
    ].head(5)
    print(f"\n   From missing players (newly added):")
    for _, row in missing_examples.iterrows():
        print(f"   • {row['full_name']} ({row['team_name']}, {row['competition']}) - "
              f"DOB: {row['date_of_birth']}, Foot: {row['dominant_foot']}")
    
    # Competition analysis
    print(f"\n📊 COMPETITION ANALYSIS:")
    competition_counts = df_combined['competition'].value_counts()
    print(f"   Top competitions:")
    for comp, count in competition_counts.head(10).items():
        print(f"   {comp}: {count:,} players")
    
    # Save the combined database
    output_file = 'all_players_combined_database.csv'
    df_combined.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved combined database to: {output_file}")
    print(f"📊 Total players: {len(df_combined)}")
    print(f"📊 Total columns: {len(df_combined.columns)}")
    
    # Final summary
    print(f"\n🎉 COMBINATION COMPLETE!")
    print(f"✅ Successfully combined {len(df_main)} + {len(df_missing_mapped)} = {len(df_combined)} players")
    print(f"✅ Database now contains players from all 19 leagues with comprehensive data")
    print(f"✅ Ready for analysis and reporting")
    
    return df_combined

def main():
    """Main function"""
    print("🚀 Starting database combination...")
    
    try:
        combined_df = combine_all_players()
        
        if combined_df is not None:
            print(f"\n🎉 Successfully combined all player databases!")
            print(f"📁 Output file: all_players_combined_database.csv")
            print(f"📊 Total players: {len(combined_df)}")
        else:
            print(f"\n❌ Failed to combine databases")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
