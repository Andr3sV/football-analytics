#!/usr/bin/env python3
"""
Enrich Main Database - Add scraped data to the main cleaned database
Uses player ID from URL to match and enrich the main dataset
"""
import pandas as pd
import re
import numpy as np

def extract_player_id_from_url(profile_url):
    """Extract player ID from Transfermarkt profile URL"""
    if pd.isna(profile_url):
        return None
    
    url_str = str(profile_url)
    match = re.search(r'/spieler/(\d+)', url_str)
    if match:
        return int(match.group(1))
    return None

def enrich_main_database():
    """Enrich the main database with scraped data"""
    print("🔄 Loading main database...")
    
    # Load the main cleaned database
    df_main = pd.read_csv('merged_players_databases_cleaned.csv')
    print(f"   ✅ Loaded {len(df_main)} players from main database")
    
    print("🔄 Loading scraped data...")
    
    # Load the scraped data from both files
    df_stealth = pd.read_csv('players_FINAL_STEALTH_PROGRESS_3525.csv')
    print(f"   ✅ Loaded {len(df_stealth)} players from stealth scraper")
    
    df_robust = pd.read_csv('players_ROBUST_PROGRESS_2200.csv')
    print(f"   ✅ Loaded {len(df_robust)} players from robust scraper")
    
    # Extract player IDs from URLs in scraped data
    print("🔍 Extracting player IDs from scraped data...")
    
    df_stealth['scraped_player_id'] = df_stealth['profile_url'].apply(extract_player_id_from_url)
    df_robust['scraped_player_id'] = df_robust['profile_url'].apply(extract_player_id_from_url)
    
    # Combine both scraped datasets
    print("🔧 Combining scraped datasets...")
    
    # Remove duplicates from scraped data (keep the most recent one)
    df_stealth_clean = df_stealth.drop_duplicates(subset=['scraped_player_id'], keep='last')
    df_robust_clean = df_robust.drop_duplicates(subset=['scraped_player_id'], keep='last')
    
    # Combine both datasets
    df_scraped_combined = pd.concat([df_stealth_clean, df_robust_clean], ignore_index=True)
    
    # Remove duplicates again (in case there's overlap between the two files)
    df_scraped_combined = df_scraped_combined.drop_duplicates(subset=['scraped_player_id'], keep='last')
    
    print(f"   ✅ Combined scraped data: {len(df_scraped_combined)} unique players")
    
    # Show columns available for enrichment
    print(f"\n📋 Columns available for enrichment:")
    scraped_columns = [col for col in df_scraped_combined.columns if col not in ['full_name', 'profile_url', 'relative_profile_url', 'team_name', 'competition', 'season', 'scraped_player_id']]
    for i, col in enumerate(scraped_columns):
        print(f"   {i+1}. {col}")
    
    print(f"\n🔧 Enriching main database...")
    
    # Convert player_id in main database to int for matching
    df_main['player_id'] = pd.to_numeric(df_main['player_id'], errors='coerce').astype('Int64')
    
    # Prepare scraped data for merge
    df_scraped_for_merge = df_scraped_combined[['scraped_player_id'] + scraped_columns].copy()
    
    # Merge the data
    df_enriched = df_main.merge(
        df_scraped_for_merge,
        left_on='player_id',
        right_on='scraped_player_id',
        how='left',
        suffixes=('', '_scraped')
    )
    
    # Remove the temporary column
    df_enriched = df_enriched.drop('scraped_player_id', axis=1)
    
    # Update existing columns with scraped data where main data is missing
    columns_to_update = [
        'market_value', 'age', 'nationality', 'current_club', 'position', 
        'date_of_birth', 'city_of_birth', 'country_of_birth', 'place_of_birth', 
        'dominant_foot', 'agent', 'social_links'
    ]
    
    for col in columns_to_update:
        if col in df_enriched.columns and f'{col}_scraped' in df_enriched.columns:
            # Update where main data is missing but scraped data exists
            mask = df_enriched[col].isna() & df_enriched[f'{col}_scraped'].notna()
            df_enriched.loc[mask, col] = df_enriched.loc[mask, f'{col}_scraped']
            
            # Remove the scraped column
            df_enriched = df_enriched.drop(f'{col}_scraped', axis=1)
    
    # Count enriched players
    enriched_count = df_enriched['market_value'].notna().sum()
    original_count = df_main['market_value'].notna().sum() if 'market_value' in df_main.columns else 0
    
    print(f"   ✅ Enriched database created")
    print(f"   📊 Players with market value: {enriched_count}")
    print(f"   📊 Players with age: {df_enriched['age'].notna().sum()}")
    print(f"   📊 Players with nationality: {df_enriched['nationality'].notna().sum()}")
    print(f"   📊 Players with position: {df_enriched['position'].notna().sum()}")
    print(f"   📊 Players with date of birth: {df_enriched['date_of_birth'].notna().sum()}")
    print(f"   📊 Players with agent: {df_enriched['agent'].notna().sum()}")
    
    # Show examples of enriched data
    print(f"\n📋 Examples of enriched players:")
    enriched_sample = df_enriched[df_enriched['market_value'].notna()][
        ['full_name', 'market_value', 'age', 'nationality', 'position', 'current_club']
    ].head(10)
    print(enriched_sample.to_string(index=False))
    
    # Show statistics
    print(f"\n📊 Enrichment Statistics:")
    print(f"   Original players: {len(df_main)}")
    print(f"   Enriched players: {len(df_enriched)}")
    print(f"   Players with market value (before): {original_count}")
    print(f"   Players with market value (after): {enriched_count}")
    print(f"   Market value enrichment: +{enriched_count - original_count} players")
    
    # Save the enriched dataset
    output_file = 'merged_players_databases_enriched.csv'
    df_enriched.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved enriched dataset to: {output_file}")
    print(f"📊 Total players: {len(df_enriched)}")
    
    return df_enriched

def main():
    """Main function"""
    try:
        enriched_df = enrich_main_database()
        
        if enriched_df is not None:
            print(f"\n🎉 Successfully enriched main database!")
            print(f"📁 Output file: merged_players_databases_enriched.csv")
            print(f"📊 Total players: {len(enriched_df)}")
        else:
            print(f"\n❌ Failed to enrich main database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
