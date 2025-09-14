#!/usr/bin/env python3
"""
Monitor for Bulk Transfers Solidarity Scraper progress
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
        return 'transfers_solidarity_bulk.py' in out.stdout
    except Exception:
        return False

def get_bulk_transfers_stats():
    """Get bulk transfers solidarity scraper statistics"""
    stats = {
        'total_records': 0,
        'unique_players': 0,
        'latest_file': None,
        'last_update': None
    }
    
    # Check for bulk transfers solidarity data file
    if os.path.exists('bulk_transfers_solidarity_contributions.csv'):
        try:
            df = pd.read_csv('bulk_transfers_solidarity_contributions.csv')
            stats['total_records'] = len(df)
            stats['unique_players'] = df['player_name'].nunique() if 'player_name' in df.columns else 0
            stats['latest_file'] = 'bulk_transfers_solidarity_contributions.csv'
            stats['last_update'] = datetime.fromtimestamp(os.path.getmtime('bulk_transfers_solidarity_contributions.csv'))
        except Exception:
            pass
    
    # Check for individual timestamped files
    bulk_files = glob.glob('bulk_transfers_solidarity_*.csv')
    if bulk_files:
        latest_file = max(bulk_files, key=os.path.getctime)
        stats['latest_file'] = latest_file
        stats['last_update'] = datetime.fromtimestamp(os.path.getctime(latest_file))
    
    return stats

def show():
    clear_screen()
    print("🔄 BULK TRANSFERS SOLIDARITY CONTRIBUTION SCRAPER MONITOR")
    print("="*80)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"Status: {'RUNNING' if is_running() else 'NOT RUNNING'}")
    print()
    
    stats = get_bulk_transfers_stats()
    
    print("📊 BULK TRANSFERS SOLIDARITY DATA STATISTICS:")
    print(f"  📝 Total solidarity records: {stats['total_records']}")
    print(f"  👥 Unique players processed: {stats['unique_players']}")
    if stats['latest_file']:
        print(f"  📁 Latest file: {stats['latest_file']}")
    if stats['last_update']:
        print(f"  🕐 Last update: {stats['last_update'].strftime('%H:%M:%S')}")
    
    print()
    
    # Show recent solidarity data if available
    if os.path.exists('bulk_transfers_solidarity_contributions.csv'):
        try:
            df = pd.read_csv('bulk_transfers_solidarity_contributions.csv')
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
                    total_contributions = 0
                    for contribution in df['solidarity_contribution']:
                        try:
                            if 'm' in str(contribution):
                                value = float(str(contribution).replace('€', '').replace('m', '')) * 1000000
                            elif 'k' in str(contribution):
                                value = float(str(contribution).replace('€', '').replace('k', '')) * 1000
                            else:
                                value = float(str(contribution).replace('€', '')) if str(contribution) != '€0' else 0
                            total_contributions += value
                        except:
                            pass
                    print(f"💰 TOTAL CONTRIBUTIONS VALUE: €{total_contributions:,.0f}")
        except Exception:
            pass
    
    # Show main scraper progress for context
    print()
    print("📈 MAIN SCRAPER CONTEXT:")
    main_files = glob.glob('players_ALL_LEAGUES.csv')
    if main_files:
        try:
            main_df = pd.read_csv('players_ALL_LEAGUES.csv')
            print(f"  📊 Total players available: {len(main_df)}")
        except Exception:
            pass
    else:
        print("  ⏳ No main players file found")

if __name__ == '__main__':
    try:
        while True:
            show()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n👋 Monitor stopped.")
