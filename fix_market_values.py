#!/usr/bin/env python3
"""
Fix Market Values - Remove two zeros from the right for values with 7+ digits
"""
import pandas as pd
import numpy as np

def fix_market_values():
    """Fix market values by removing two zeros from values with 7+ digits"""
    print("🔄 Loading database with latest market values...")
    
    # Load the database with latest market values
    df = pd.read_csv('merged_players_databases_with_latest_values.csv')
    print(f"   ✅ Loaded {len(df)} players")
    
    # Check current market value statistics
    market_value_col = 'latest_market_value'
    if market_value_col not in df.columns:
        market_value_col = 'market_value'
    
    original_values = df[market_value_col].dropna()
    print(f"   📊 Original values count: {len(original_values)}")
    
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
        
        # Save the fixed database
        output_file = 'merged_players_databases_fixed_values.csv'
        df_fixed.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved fixed database to: {output_file}")
        print(f"📊 Total players: {len(df_fixed)}")
        print(f"📊 Players with market values: {df_fixed[market_value_col].notna().sum()}")
        
        # Also update the latest_market_values.csv file
        latest_values_file = 'latest_market_values.csv'
        try:
            df_latest = pd.read_csv(latest_values_file)
            df_latest['latest_market_value'] = pd.to_numeric(df_latest['latest_market_value'], errors='coerce')
            
            # Apply the same fix
            mask_latest = df_latest['latest_market_value'] >= 1000000
            df_latest.loc[mask_latest, 'latest_market_value'] = df_latest.loc[mask_latest, 'latest_market_value'] / 100
            
            df_latest.to_csv(latest_values_file, index=False)
            print(f"💾 Updated {latest_values_file} with fixed values")
            
        except Exception as e:
            print(f"⚠️  Could not update {latest_values_file}: {e}")
        
        return df_fixed
        
    else:
        print(f"   ✅ No values with 7+ digits found. No fixing needed.")
        return df

def main():
    """Main function"""
    print("🚀 Starting market value fix...")
    
    try:
        fixed_df = fix_market_values()
        
        if fixed_df is not None:
            print(f"\n🎉 Successfully fixed market values!")
            print(f"📁 Fixed database: merged_players_databases_fixed_values.csv")
        else:
            print(f"\n❌ Failed to fix market values")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
