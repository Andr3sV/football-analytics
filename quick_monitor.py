#!/usr/bin/env python3
"""
Quick monitor for the perfect scraper
"""
import os
import time
import glob
from datetime import datetime

def check_scraper_status():
    """Check if scraper is running and show progress"""
    print("🔍 CHECKING SCRAPER STATUS")
    print("=" * 50)
    
    # Check if scraper process is running
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'final_perfect_scraper.py' in result.stdout:
            print("✅ Scraper is running")
        else:
            print("❌ Scraper is not running")
            return
    except:
        print("❌ Could not check process status")
        return
    
    # Check for progress files
    progress_files = glob.glob('players_PERFECT_DETAILED_PROGRESS_*.csv')
    
    if progress_files:
        # Get the latest progress file
        latest_file = max(progress_files, key=os.path.getctime)
        
        try:
            import pandas as pd
            df = pd.read_csv(latest_file)
            
            print(f"📁 Latest progress file: {latest_file}")
            print(f"👥 Players processed: {len(df)}/9,962")
            print(f"📊 Progress: {len(df)/9962*100:.1f}%")
            print(f"⏰ Last updated: {datetime.fromtimestamp(os.path.getctime(latest_file)).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show data quality
            print(f"\n📋 DATA QUALITY:")
            key_fields = ['age', 'nationality', 'position', 'market_value', 'dominant_foot', 'agent']
            for field in key_fields:
                if field in df.columns:
                    count = df[field].notna().sum()
                    percentage = count / len(df) * 100
                    print(f"  {field}: {count}/{len(df)} ({percentage:.1f}%)")
            
            # Show recent players
            print(f"\n👥 RECENT PLAYERS:")
            sample_cols = ['full_name', 'team_name', 'age', 'nationality', 'position', 'market_value']
            available_cols = [col for col in sample_cols if col in df.columns]
            if available_cols:
                print(df[available_cols].tail(3).to_string())
            
        except Exception as e:
            print(f"❌ Error reading progress file: {e}")
    else:
        print("⏳ No progress files yet - scraper is still starting...")
        print("💡 Progress files are saved every 100 players")
        print("⏰ Estimated time to first progress file: 10-15 minutes")

def main():
    """Main monitoring function"""
    print("🚀 PERFECT SCRAPER MONITOR")
    print("=" * 50)
    
    while True:
        check_scraper_status()
        print("\n" + "=" * 50)
        print("⏳ Waiting 30 seconds before next check...")
        print("Press Ctrl+C to stop monitoring")
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped.")
