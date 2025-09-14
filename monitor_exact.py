#!/usr/bin/env python3
"""
Monitor for FullExactScraper progress
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
        return 'full_exact_scraper.py' in out.stdout
    except Exception:
        return False

def latest_progress():
    files = glob.glob('players_EXACT_DETAILED_PROGRESS_*.csv')
    if not files:
        return None
    latest = max(files, key=os.path.getctime)
    try:
        df = pd.read_csv(latest)
        return latest, df
    except Exception:
        return latest, None

def show():
    clear_screen()
    print("🚀 EXACT SCRAPER MONITOR")
    print("="*60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"Status: {'RUNNING' if is_running() else 'NOT RUNNING'}")
    print()
    lp = latest_progress()
    if not lp:
        print("⏳ Waiting for first progress file (saved every 100 players)...")
        return
    fname, df = lp
    count = len(df) if df is not None else 'unknown'
    print("📦 Latest file:", fname)
    print("👥 Players processed:", count, "/ 9,962")
    if df is not None and 'market_value' in df.columns:
        filled = df['market_value'].notna().sum()
        pct = filled/len(df)*100 if len(df)>0 else 0
        print(f"💰 market_value filled: {filled}/{len(df)} ({pct:.1f}%)")
    if df is not None and len(df)>0:
        cols = [c for c in ['full_name','team_name','competition','market_value'] if c in df.columns]
        if cols:
            print()
            print("🧪 Recent players:")
            print(df[cols].tail(5).to_string(index=False))

if __name__ == '__main__':
    try:
        while True:
            show()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n👋 Monitor stopped.")
