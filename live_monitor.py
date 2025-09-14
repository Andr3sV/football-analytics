#!/usr/bin/env python3
"""
Live monitor for the perfect scraper with real-time progress
"""
import os
import time
import glob
import subprocess
from datetime import datetime
import pandas as pd

def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def get_scraper_status():
    """Get scraper process status"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return 'final_perfect_scraper.py' in result.stdout
    except:
        return False

def get_latest_progress():
    """Get latest progress information"""
    progress_files = glob.glob('players_PERFECT_DETAILED_PROGRESS_*.csv')
    
    if not progress_files:
        return None
    
    latest_file = max(progress_files, key=os.path.getctime)
    
    try:
        df = pd.read_csv(latest_file)
        return {
            'file': latest_file,
            'count': len(df),
            'timestamp': os.path.getctime(latest_file),
            'data': df
        }
    except:
        return None

def get_log_tail():
    """Get last few lines from scraper log"""
    try:
        result = subprocess.run(['tail', '-10', 'scraper.log'], capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "No log available"

def display_progress():
    """Display current progress"""
    clear_screen()
    
    print("🚀 PERFECT SCRAPER LIVE MONITOR")
    print("=" * 60)
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if scraper is running
    is_running = get_scraper_status()
    if is_running:
        print("✅ Scraper Status: RUNNING")
    else:
        print("❌ Scraper Status: NOT RUNNING")
        return
    
    print()
    
    # Get progress information
    progress = get_latest_progress()
    
    if progress:
        print("📊 PROGRESS INFORMATION")
        print("-" * 40)
        print(f"📁 Latest file: {progress['file']}")
        print(f"👥 Players processed: {progress['count']:,}/9,962")
        print(f"📈 Progress: {progress['count']/9962*100:.2f}%")
        print(f"⏰ Last update: {datetime.fromtimestamp(progress['timestamp']).strftime('%H:%M:%S')}")
        
        # Calculate estimated completion
        if progress['count'] > 0:
            # Estimate based on 5-8 seconds per player
            avg_time_per_player = 6.5  # seconds
            remaining_players = 9962 - progress['count']
            estimated_seconds = remaining_players * avg_time_per_player
            estimated_hours = estimated_seconds / 3600
            
            print(f"⏳ Estimated time remaining: {estimated_hours:.1f} hours")
            print(f"🎯 Estimated completion: {datetime.fromtimestamp(time.time() + estimated_seconds).strftime('%H:%M:%S')}")
        
        print()
        
        # Show data quality
        print("📋 DATA QUALITY")
        print("-" * 40)
        df = progress['data']
        key_fields = ['age', 'nationality', 'position', 'market_value', 'dominant_foot', 'agent']
        for field in key_fields:
            if field in df.columns:
                count = df[field].notna().sum()
                percentage = count / len(df) * 100
                status = "✅" if percentage >= 90 else "⚠️" if percentage >= 70 else "❌"
                print(f"  {status} {field}: {count}/{len(df)} ({percentage:.1f}%)")
        
        print()
        
        # Show recent players
        print("👥 RECENT PLAYERS")
        print("-" * 40)
        sample_cols = ['full_name', 'team_name', 'age', 'nationality', 'position', 'market_value']
        available_cols = [col for col in sample_cols if col in df.columns]
        if available_cols:
            recent_players = df[available_cols].tail(3)
            for _, player in recent_players.iterrows():
                name = player.get('full_name', 'Unknown')
                team = player.get('team_name', 'Unknown')
                age = player.get('age', 'N/A')
                nationality = player.get('nationality', 'N/A')
                position = player.get('position', 'N/A')
                value = player.get('market_value', 'N/A')
                print(f"  • {name} ({age}) - {team} - {position} - {value}")
        
        print()
        
        # Show competition breakdown
        if 'competition' in df.columns:
            print("🏆 COMPETITION BREAKDOWN")
            print("-" * 40)
            comp_counts = df['competition'].value_counts().head(5)
            for comp, count in comp_counts.items():
                print(f"  {comp}: {count} players")
        
    else:
        print("⏳ No progress files yet - scraper is starting...")
        print("💡 Progress files are saved every 100 players")
        print("⏰ Estimated time to first progress file: 10-15 minutes")
    
    print()
    
    # Show recent log entries
    print("📝 RECENT LOG ENTRIES")
    print("-" * 40)
    log_tail = get_log_tail()
    if log_tail:
        lines = log_tail.split('\n')
        for line in lines[-5:]:  # Show last 5 lines
            if line.strip():
                print(f"  {line}")
    else:
        print("  No log entries available")
    
    print()
    print("=" * 60)
    print("Press Ctrl+C to stop monitoring")

def main():
    """Main monitoring function"""
    try:
        while True:
            display_progress()
            time.sleep(30)  # Update every 30 seconds
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped.")
        print("💡 The scraper continues running in the background.")
        print("📁 Check 'scraper.log' for detailed logs.")
        print("📊 Progress files: players_PERFECT_DETAILED_PROGRESS_*.csv")

if __name__ == "__main__":
    main()
