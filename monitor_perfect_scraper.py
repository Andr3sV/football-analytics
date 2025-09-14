#!/usr/bin/env python3
"""
Monitor the progress of the perfect detailed scraper
"""
import pandas as pd
import os
import time
import glob
from datetime import datetime

def check_progress():
    """Check the current progress of scraping"""
    # Look for progress files
    progress_files = glob.glob('players_PERFECT_DETAILED_PROGRESS_*.csv')
    
    if progress_files:
        # Get the latest progress file
        latest_file = max(progress_files, key=os.path.getctime)
        
        try:
            df = pd.read_csv(latest_file)
            
            print(f"=== PERFECT SCRAPER PROGRESS ===")
            print(f"Latest progress file: {latest_file}")
            print(f"Players processed: {len(df)}/9,962")
            print(f"Progress: {len(df)/9962*100:.1f}%")
            print(f"Last updated: {datetime.fromtimestamp(os.path.getctime(latest_file)).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show data quality
            print(f"\n=== DATA QUALITY ===")
            if 'age' in df.columns:
                age_count = df['age'].notna().sum()
                print(f"Players with age: {age_count}/{len(df)} ({age_count/len(df)*100:.1f}%)")
            
            if 'nationality' in df.columns:
                nationality_count = df['nationality'].notna().sum()
                print(f"Players with nationality: {nationality_count}/{len(df)} ({nationality_count/len(df)*100:.1f}%)")
            
            if 'position' in df.columns:
                position_count = df['position'].notna().sum()
                print(f"Players with position: {position_count}/{len(df)} ({position_count/len(df)*100:.1f}%)")
            
            if 'market_value' in df.columns:
                value_count = df['market_value'].notna().sum()
                print(f"Players with market value: {value_count}/{len(df)} ({value_count/len(df)*100:.1f}%)")
            
            if 'dominant_foot' in df.columns:
                foot_count = df['dominant_foot'].notna().sum()
                print(f"Players with dominant foot: {foot_count}/{len(df)} ({foot_count/len(df)*100:.1f}%)")
            
            if 'agent' in df.columns:
                agent_count = df['agent'].notna().sum()
                print(f"Players with agent: {agent_count}/{len(df)} ({agent_count/len(df)*100:.1f}%)")
            
            # Show recent players
            print(f"\n=== RECENT PLAYERS ===")
            sample_cols = ['full_name', 'team_name', 'competition', 'age', 'nationality', 'position', 'market_value']
            available_cols = [col for col in sample_cols if col in df.columns]
            if available_cols:
                print(df[available_cols].tail(5).to_string())
            
            return df
        except Exception as e:
            print(f"Error reading progress file: {e}")
            return None
    else:
        print("No progress files found yet. Scraper may still be starting...")
        return None

def estimate_completion_time():
    """Estimate completion time based on progress"""
    progress_files = glob.glob('players_PERFECT_DETAILED_PROGRESS_*.csv')
    
    if len(progress_files) >= 2:
        # Get the two most recent files
        files_with_time = [(f, os.path.getctime(f)) for f in progress_files]
        files_with_time.sort(key=lambda x: x[1], reverse=True)
        
        if len(files_with_time) >= 2:
            latest_file, latest_time = files_with_time[0]
            previous_file, previous_time = files_with_time[1]
            
            try:
                latest_df = pd.read_csv(latest_file)
                previous_df = pd.read_csv(previous_file)
                
                players_processed = len(latest_df) - len(previous_df)
                time_elapsed = latest_time - previous_time
                
                if players_processed > 0 and time_elapsed > 0:
                    rate = players_processed / time_elapsed  # players per second
                    remaining_players = 9962 - len(latest_df)
                    estimated_seconds = remaining_players / rate
                    estimated_hours = estimated_seconds / 3600
                    
                    print(f"\n=== ESTIMATED COMPLETION ===")
                    print(f"Processing rate: {rate:.2f} players/second")
                    print(f"Remaining players: {remaining_players}")
                    print(f"Estimated time remaining: {estimated_hours:.2f} hours")
                    
            except Exception as e:
                print(f"Error calculating completion time: {e}")

def main():
    """Monitor progress"""
    print("Monitoring perfect detailed scraper progress...")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            check_progress()
            estimate_completion_time()
            print("\n" + "="*60)
            print("Waiting 60 seconds before next check...")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
