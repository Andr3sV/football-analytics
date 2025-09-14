#!/usr/bin/env python3
"""
Check Market Value Correction - Verify if the correction affected players 
who already had correct market values
"""
import pandas as pd
import numpy as np

def check_market_value_correction():
    """Check if the correction affected players who already had correct values"""
    print("🔄 Loading databases for comparison...")
    
    # Load the database before the latest correction
    df_before = pd.read_csv('all_players_combined_database_final.csv')
    print(f"   ✅ Before correction: {len(df_before)} players")
    
    # Load the database after the latest correction
    df_after = pd.read_csv('all_players_combined_database_final_fixed.csv')
    print(f"   ✅ After correction: {len(df_after)} players")
    
    # Convert market values to numeric
    df_before['latest_market_value'] = pd.to_numeric(df_before['latest_market_value'], errors='coerce')
    df_after['latest_market_value'] = pd.to_numeric(df_after['latest_market_value'], errors='coerce')
    
    print("\n🔍 Analyzing market value changes...")
    
    # Find players with market values in both databases
    before_with_mv = df_before['latest_market_value'].notna()
    after_with_mv = df_after['latest_market_value'].notna()
    
    # Players that had market values before
    players_before = df_before[before_with_mv]
    print(f"   📊 Players with market values before: {len(players_before)}")
    
    # Players that have market values after
    players_after = df_after[after_with_mv]
    print(f"   📊 Players with market values after: {len(players_after)}")
    
    # Compare values for players that had them in both
    merged = df_before.merge(
        df_after[['player_id', 'latest_market_value']], 
        on='player_id', 
        suffixes=('_before', '_after')
    )
    
    # Only players that had market values before
    players_with_before = merged[merged['latest_market_value_before'].notna()]
    print(f"   📊 Players that had market values before: {len(players_with_before)}")
    
    # Check if values changed
    players_with_before['value_changed'] = (
        players_with_before['latest_market_value_before'] != players_with_before['latest_market_value_after']
    )
    
    changed_players = players_with_before[players_with_before['value_changed']]
    print(f"   📊 Players whose values changed: {len(changed_players)}")
    
    if len(changed_players) > 0:
        print(f"\n📋 EXAMPLES OF PLAYERS WHOSE VALUES CHANGED:")
        examples = changed_players.head(10)[
            ['full_name', 'team_name', 'latest_market_value_before', 'latest_market_value_after']
        ]
        for _, row in examples.iterrows():
            print(f"   • {row['full_name']} ({row['team_name']}) - "
                  f"Before: €{row['latest_market_value_before']:,.0f} → "
                  f"After: €{row['latest_market_value_after']:,.0f}")
        
        # Check if the changes were the division by 100 (correction)
        print(f"\n🔍 Checking if changes were corrections (division by 100)...")
        
        correction_count = 0
        for _, row in changed_players.iterrows():
            before_val = row['latest_market_value_before']
            after_val = row['latest_market_value_after']
            
            # Check if after = before / 100 (allowing for small floating point differences)
            if pd.notna(before_val) and pd.notna(after_val) and before_val > 0:
                expected_after = before_val / 100
                if abs(after_val - expected_after) < 1:  # Allow small floating point differences
                    correction_count += 1
        
        print(f"   📊 Players whose values were corrected (divided by 100): {correction_count}")
        print(f"   📊 Players whose values changed for other reasons: {len(changed_players) - correction_count}")
        
        # Show statistics
        print(f"\n📊 VALUE CHANGE STATISTICS:")
        before_stats = players_with_before['latest_market_value_before'].describe()
        after_stats = players_with_before['latest_market_value_after'].describe()
        
        print(f"   Before correction:")
        print(f"      Max: €{before_stats['max']:,.0f}")
        print(f"      Average: €{before_stats['mean']:,.0f}")
        print(f"      Median: €{before_stats['50%']:,.0f}")
        
        print(f"   After correction:")
        print(f"      Max: €{after_stats['max']:,.0f}")
        print(f"      Average: €{after_stats['mean']:,.0f}")
        print(f"      Median: €{after_stats['50%']:,.0f}")
        
        # Check if we over-corrected players who already had correct values
        print(f"\n⚠️  CHECKING FOR OVER-CORRECTION:")
        
        # Players who had values under 1M before (likely already correct)
        already_correct = players_with_before[
            players_with_before['latest_market_value_before'] < 1000000
        ]
        
        over_corrected = already_correct[already_correct['value_changed']]
        print(f"   📊 Players with values under €1M before (likely already correct): {len(already_correct)}")
        print(f"   📊 Players with values under €1M that were changed: {len(over_corrected)}")
        
        if len(over_corrected) > 0:
            print(f"   ⚠️  WARNING: {len(over_corrected)} players may have been over-corrected!")
            print(f"   📋 Examples of potentially over-corrected players:")
            examples = over_corrected.head(5)[
                ['full_name', 'team_name', 'latest_market_value_before', 'latest_market_value_after']
            ]
            for _, row in examples.iterrows():
                print(f"      • {row['full_name']} ({row['team_name']}) - "
                      f"Before: €{row['latest_market_value_before']:,.0f} → "
                      f"After: €{row['latest_market_value_after']:,.0f}")
        else:
            print(f"   ✅ No over-correction detected for players with values under €1M")
    
    else:
        print(f"   ✅ No players had their market values changed")
    
    return len(changed_players), len(over_corrected) if 'over_corrected' in locals() else 0

def main():
    """Main function"""
    print("🚀 Checking market value correction impact...")
    
    try:
        changed_count, over_corrected_count = check_market_value_correction()
        
        print(f"\n🎯 CONCLUSION:")
        if changed_count == 0:
            print(f"   ✅ No market values were changed - correction was safe")
        elif over_corrected_count == 0:
            print(f"   ✅ Correction was applied correctly - no over-correction")
        else:
            print(f"   ⚠️  WARNING: {over_corrected_count} players may have been over-corrected")
            print(f"   💡 Recommendation: Review and potentially restore original values for these players")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
