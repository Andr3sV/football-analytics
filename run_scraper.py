#!/usr/bin/env python3
"""
Script to run the optimized scraper with different options
"""
import subprocess
import sys
import time
import os

def show_menu():
    """Show the main menu"""
    print("=" * 60)
    print("🚀 OPTIMIZED TRANSFERMARKT SCRAPER")
    print("=" * 60)
    print("1. 🏃‍♂️ Run scraper in background (recommended)")
    print("2. 👀 Run scraper with live monitoring")
    print("3. 📊 Check current progress")
    print("4. 🛑 Stop any running scrapers")
    print("5. 📈 View statistics")
    print("6. ❌ Exit")
    print("=" * 60)

def run_scraper_background():
    """Run scraper in background"""
    print("🚀 Starting optimized scraper in background...")
    print("This will process all 9,962 players and may take 2-4 hours.")
    print("Progress will be saved every 500 players.")
    print("\nTo monitor progress, run: python monitor_progress.py")
    
    # Start the scraper in background
    process = subprocess.Popen([
        sys.executable, "optimized_scraper.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print(f"✅ Scraper started with PID: {process.pid}")
    print("📁 Progress files will be saved as: players_DETAILED_PROGRESS_*.csv")
    print("📁 Final result will be: players_ALL_DETAILED_FINAL.csv")
    
    return process

def run_scraper_with_monitoring():
    """Run scraper with live monitoring"""
    print("🚀 Starting optimized scraper with live monitoring...")
    print("This will show real-time progress updates.")
    
    # Run the scraper directly
    subprocess.run([sys.executable, "optimized_scraper.py"])

def check_progress():
    """Check current progress"""
    print("📊 Checking current progress...")
    subprocess.run([sys.executable, "monitor_progress.py"])

def stop_scrapers():
    """Stop any running scrapers"""
    print("🛑 Stopping any running scrapers...")
    
    try:
        # Find and kill Python processes running our scrapers
        result = subprocess.run([
            "pkill", "-f", "optimized_scraper.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Scrapers stopped successfully")
        else:
            print("ℹ️  No running scrapers found")
    except Exception as e:
        print(f"❌ Error stopping scrapers: {e}")

def view_statistics():
    """View statistics from progress files"""
    import glob
    import pandas as pd
    
    progress_files = glob.glob('players_DETAILED_PROGRESS_*.csv')
    
    if not progress_files:
        print("❌ No progress files found")
        return
    
    # Get the latest progress file
    latest_file = max(progress_files, key=os.path.getctime)
    
    try:
        df = pd.read_csv(latest_file)
        
        print(f"📈 STATISTICS FROM {latest_file}")
        print(f"Total players processed: {len(df)}")
        
        # Data quality statistics
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
        
        # Competition breakdown
        if 'competition' in df.columns:
            print(f"\n📊 BY COMPETITION:")
            comp_counts = df['competition'].value_counts()
            for comp, count in comp_counts.head(10).items():
                print(f"  {comp}: {count} players")
        
    except Exception as e:
        print(f"❌ Error reading statistics: {e}")

def main():
    """Main function"""
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                run_scraper_background()
                print("\n✅ Scraper started in background!")
                print("💡 Tip: Run 'python monitor_progress.py' in another terminal to monitor progress")
                break
                
            elif choice == '2':
                run_scraper_with_monitoring()
                break
                
            elif choice == '3':
                check_progress()
                
            elif choice == '4':
                stop_scrapers()
                
            elif choice == '5':
                view_statistics()
                
            elif choice == '6':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
