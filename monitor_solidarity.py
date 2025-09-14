#!/usr/bin/env python3
"""
Monitor for Solidarity Scraper progress
"""
import os
import time
import glob
import subprocess
from datetime import datetime
import pandas as pd

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def is_running():
    try:
        out = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return 'solidarity_scraper.py' in out.stdout
    except Exception:
        return False

def get_solidarity_stats():
    """Get solidarity scraper statistics"""
    stats = {
        'total_records': 0,
        'unique_players': 0,
        'latest_file': None,
        'last_update': None
    }
    
    # Check for solidarity data file
    if os.path.exists('solidarity_contributions.csv'):
        try:
            df = pd.read_csv('solidarity_contributions.csv')
            stats['total_records'] = len(df)
            stats['unique_players'] = df['player_name'].nunique() if 'player_name' in df.columns else 0
            stats['latest_file'] = 'solidarity_contributions.csv'
            stats['last_update'] = datetime.fromtimestamp(os.path.getmtime('solidarity_contributions.csv'))
        except Exception:
            pass
    
    # Check for individual timestamped files
    solidarity_files = glob.glob('solidarity_data_*.csv')
    if solidarity_files:
        latest_file = max(solidarity_files, key=os.path.getctime)
        stats['latest_file'] = latest_file
        stats['last_update'] = datetime.fromtimestamp(os.path.getctime(latest_file))
    
    return stats

def show():
    clear_screen()
    print("🤝 SOLIDARITY CONTRIBUTION SCRAPER MONITOR")
    print("="*60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"Status: {'RUNNING' if is_running() else 'NOT RUNNING'}")
    print()
    
    stats = get_solidarity_stats()
    
    print("📊 SOLIDARITY DATA STATISTICS:")
    print(f"  📝 Total solidarity records: {stats['total_records']}")
    print(f"  👥 Unique players processed: {stats['unique_players']}")
    if stats['latest_file']:
        print(f"  📁 Latest file: {stats['latest_file']}")
    if stats['last_update']:
        print(f"  🕐 Last update: {stats['last_update'].strftime('%H:%M:%S')}")
    
    print()
    
    # Show recent solidarity data if available
    if os.path.exists('solidarity_contributions.csv'):
        try:
            df = pd.read_csv('solidarity_contributions.csv')
            if len(df) > 0:
                print("🤝 RECENT SOLIDARITY CONTRIBUTIONS:")
                recent_cols = ['player_name', 'club', 'solidarity_contribution']
                available_cols = [col for col in recent_cols if col in df.columns]
                if available_cols:
                    print(df[available_cols].tail(5).to_string(index=False))
                print()
                
                # Show summary by club
                if 'club' in df.columns:
                    club_summary = df['club'].value_counts().head(5)
                    print("🏆 TOP CLUBS BY CONTRIBUTIONS:")
                    for club, count in club_summary.items():
                        print(f"  {club}: {count} contributions")
        except Exception:
            pass
    
    # Show main scraper progress for context
    print()
    print("📈 MAIN SCRAPER CONTEXT:")
    main_files = glob.glob('players_FAST_EXACT_PROGRESS_*.csv')
    if main_files:
        latest_main = max(main_files, key=os.path.getctime)
        try:
            main_df = pd.read_csv(latest_main)
            print(f"  📊 Main scraper: {len(main_df)} players processed")
            print(f"  📁 Latest file: {latest_main}")
        except Exception:
            pass
    else:
        print("  ⏳ No main scraper progress files found")

if __name__ == '__main__':
    try:
        while True:
            show()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n👋 Monitor stopped.")
