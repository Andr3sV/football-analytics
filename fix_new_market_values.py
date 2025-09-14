#!/usr/bin/env python3
"""
Fix New Market Values - Apply the same fix to newly added market values
Remove two zeros from the right for values with 7+ digits
"""
import pandas as pd
import numpy as np

def fix_new_market_values():
    """Fix newly added market values by removing two zeros from values with 7+ digits"""
    print("🔄 Loading final combined database...")
    
    # Load the final database
    df = pd.read_csv('all_players_combined_database_final.csv')
    print(f"   ✅ Loaded {len(df)} players")
    
    # Check current market value statistics
    market_value_col = 'latest_market_value'
    original_values = df[market_value_col].dropna()
    print(f"   📊 Current values count: {len(original_values)}")
    
    if len(original_values) > 0:
        print(f"   📊 Original statistics:")
        print(f"      Max: €{original_values.max():,}")
        print(f"      Min: €{original_values.min():,}")
        print(f"      Average: €{original_values.mean():,.0f}")
        print(f"      Median: €{original_values.median():,.0f}")
    
    # Find values with 7 or more digits
    print(f"\n🔍 Analyzing values with 7+ digits...")
    
    # Convert to numeric, handling any string values
    df[market_value_col] = pd.to_numeric(df[market_value_col], errors='coerce')
    
    # Count values with 7+ digits
    values_7plus_digits = df[market_value_col] >= 1000000  # 7 digits = 1,000,000
    count_7plus = values_7plus_digits.sum()
    
    print(f"   📊 Values with 7+ digits: {count_7plus}")
    
    if count_7plus > 0:
        # Show examples before fixing
        print(f"\n📋 Examples of values to be fixed:")
        examples = df[values_7plus_digits].nlargest(10, market_value_col)[
            ['full_name', market_value_col, 'latest_transfer_date']
        ]
        for _, row in examples.iterrows():
            print(f"   {row['full_name']}: €{row[market_value_col]:,}")
        
        # Fix the values by dividing by 100 (removing two zeros from the right)
        print(f"\n🔧 Fixing values with 7+ digits...")
        
        # Create a copy for the fix
        df_fixed = df.copy()
        
        # Apply the fix: divide by 100 for values with 7+ digits
        mask_to_fix = df_fixed[market_value_col] >= 1000000
        df_fixed.loc[mask_to_fix, market_value_col] = df_fixed.loc[mask_to_fix, market_value_col] / 100
        
        print(f"   ✅ Fixed {count_7plus} values")
        
        # Show statistics after fixing
        fixed_values = df_fixed[market_value_col].dropna()
        print(f"\n📊 Fixed statistics:")
        print(f"   Max: €{fixed_values.max():,}")
        print(f"   Min: €{fixed_values.min():,}")
        print(f"   Average: €{fixed_values.mean():,.0f}")
        print(f"   Median: €{fixed_values.median():,.0f}")
        
        # Show examples after fixing
        print(f"\n📋 Examples of fixed values:")
        examples_fixed = df_fixed[df_fixed[market_value_col] >= 1000000].nlargest(10, market_value_col)[
            ['full_name', market_value_col, 'latest_transfer_date']
        ]
        for _, row in examples_fixed.iterrows():
            print(f"   {row['full_name']}: €{row[market_value_col]:,}")
        
        # Show some examples of the fix in action
        print(f"\n📋 Examples of the fix applied:")
        fix_examples = df[values_7plus_digits].nlargest(5, market_value_col)
        for _, row in fix_examples.iterrows():
            original = row[market_value_col]
            fixed = original / 100
            print(f"   {row['full_name']}: €{original:,} → €{fixed:,}")
        
        # Calculate total market value
        total_mv = df_fixed[market_value_col].sum()
        print(f"\n💰 TOTAL MARKET VALUE AFTER FIX:")
        print(f"   Total: €{total_mv:,.0f}")
        
        # Show top players after fix
        print(f"\n🏆 TOP 10 PLAYERS BY MARKET VALUE (AFTER FIX):")
        top_players = df_fixed.nlargest(10, market_value_col)[
            ['full_name', 'team_name', 'competition', market_value_col]
        ]
        
        for i, (_, row) in enumerate(top_players.iterrows(), 1):
            mv_str = f"€{row[market_value_col]:,.0f}" if pd.notna(row[market_value_col]) else "N/A"
            print(f"   {i:2d}. {row['full_name']} ({row['team_name']}) - {mv_str}")
        
        # Market value distribution after fix
        print(f"\n📊 MARKET VALUE DISTRIBUTION (AFTER FIX):")
        if df_fixed[market_value_col].notna().any():
            # Define value ranges
            ranges = [
                (0, 1000000, "Under €1M"),
                (1000000, 5000000, "€1M - €5M"),
                (5000000, 10000000, "€5M - €10M"),
                (10000000, 25000000, "€10M - €25M"),
                (25000000, 50000000, "€25M - €50M"),
                (50000000, 100000000, "€50M - €100M"),
                (100000000, float('inf'), "Over €100M")
            ]
            
            for min_val, max_val, label in ranges:
                count = df_fixed[
                    (df_fixed[market_value_col] >= min_val) & 
                    (df_fixed[market_value_col] < max_val)
                ].shape[0]
                percentage = (count / len(df_fixed)) * 100
                print(f"   {label}: {count:,} players ({percentage:.1f}%)")
        
        # Save the fixed database
        output_file = 'all_players_combined_database_final_fixed.csv'
        df_fixed.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved fixed database to: {output_file}")
        print(f"📊 Total players: {len(df_fixed)}")
        print(f"📊 Players with market values: {df_fixed[market_value_col].notna().sum()}")
        
        return df_fixed
        
    else:
        print(f"   ✅ No values with 7+ digits found. No fixing needed.")
        return df

def main():
    """Main function"""
    print("🚀 Starting new market values fix...")
    
    try:
        fixed_df = fix_new_market_values()
        
        if fixed_df is not None:
            print(f"\n🎉 Successfully fixed new market values!")
            print(f"📁 Fixed database: all_players_combined_database_final_fixed.csv")
        else:
            print(f"\n❌ Failed to fix market values")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
