#!/usr/bin/env python3
"""
Monitor for Transfers-Based Solidarity Scraper progress
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
        return 'transfers_solidarity_improved.py' in out.stdout
    except Exception:
        return False

def get_transfers_solidarity_stats():
    """Get transfers solidarity scraper statistics"""
    stats = {
        'total_records': 0,
        'unique_players': 0,
        'latest_file': None,
        'last_update': None
    }
    
    # Check for transfers solidarity data file
    if os.path.exists('transfers_solidarity_contributions.csv'):
        try:
            df = pd.read_csv('transfers_solidarity_contributions.csv')
            stats['total_records'] = len(df)
            stats['unique_players'] = df['player_name'].nunique() if 'player_name' in df.columns else 0
            stats['latest_file'] = 'transfers_solidarity_contributions.csv'
            stats['last_update'] = datetime.fromtimestamp(os.path.getmtime('transfers_solidarity_contributions.csv'))
        except Exception:
            pass
    
    # Check for individual timestamped files
    transfers_files = glob.glob('transfers_solidarity_data_*.csv')
    if transfers_files:
        latest_file = max(transfers_files, key=os.path.getctime)
        stats['latest_file'] = latest_file
        stats['last_update'] = datetime.fromtimestamp(os.path.getctime(latest_file))
    
    return stats

def show():
    clear_screen()
    print("🔄 TRANSFERS-BASED SOLIDARITY CONTRIBUTION SCRAPER MONITOR")
    print("="*70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"Status: {'RUNNING' if is_running() else 'NOT RUNNING'}")
    print()
    
    stats = get_transfers_solidarity_stats()
    
    print("📊 TRANSFERS SOLIDARITY DATA STATISTICS:")
    print(f"  📝 Total solidarity records: {stats['total_records']}")
    print(f"  👥 Unique players processed: {stats['unique_players']}")
    if stats['latest_file']:
        print(f"  📁 Latest file: {stats['latest_file']}")
    if stats['last_update']:
        print(f"  🕐 Last update: {stats['last_update'].strftime('%H:%M:%S')}")
    
    print()
    
    # Show recent solidarity data if available
    if os.path.exists('transfers_solidarity_contributions.csv'):
        try:
            df = pd.read_csv('transfers_solidarity_contributions.csv')
            if len(df) > 0:
                print("🔄 RECENT SOLIDARITY CONTRIBUTIONS:")
                recent_cols = ['player_name', 'club', 'player_age_at_transfer', 'solidarity_contribution']
                available_cols = [col for col in recent_cols if col in df.columns]
                if available_cols:
                    print(df[available_cols].tail(5).to_string(index=False))
                print()
                
                # Show summary by age
                if 'player_age_at_transfer' in df.columns:
                    age_summary = df['player_age_at_transfer'].value_counts().sort_index().head(10)
                    print("👶 TOP AGES AT TRANSFER:")
                    for age, count in age_summary.items():
                        print(f"  Age {age}: {count} contributions")
                print()
                
                # Show summary by club
                if 'club' in df.columns:
                    club_summary = df['club'].value_counts().head(5)
                    print("🏆 TOP CLUBS BY CONTRIBUTIONS:")
                    for club, count in club_summary.items():
                        print(f"  {club}: {count} contributions")
                print()
                
                # Show total contribution amounts
                if 'solidarity_contribution' in df.columns:
                    total_contributions = df['solidarity_contribution'].apply(lambda x: 
                        float(x.replace('€', '').replace('m', '')) * 1000000 if 'm' in x else 
                        float(x.replace('€', '').replace('k', '')) * 1000 if 'k' in x else 
                        float(x.replace('€', '')) if x != '€0' else 0
                    ).sum()
                    print(f"💰 TOTAL CONTRIBUTIONS VALUE: €{total_contributions:,.0f}")
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
