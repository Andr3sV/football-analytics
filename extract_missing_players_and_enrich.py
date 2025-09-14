#!/usr/bin/env python3
"""
Extract Missing Players and Enrich - Find players from players_ALL_LEAGUES 
that are not in merged_players_databases_with_transfers.csv and enrich them
with data from Player table in dev 2.db
"""
import sqlite3
import pandas as pd
import re
from datetime import datetime

def extract_player_id_from_url(profile_url):
    """Extract player ID from Transfermarkt profile URL"""
    if pd.isna(profile_url):
        return None
    
    url_str = str(profile_url)
    match = re.search(r'/spieler/(\d+)', url_str)
    if match:
        return int(match.group(1))
    return None

def find_missing_players():
    """Find players from players_ALL_LEAGUES that are not in our current database"""
    print("🔄 Loading databases...")
    
    # Load our current database
    df_current = pd.read_csv('merged_players_databases_with_transfers.csv')
    print(f"   ✅ Current database: {len(df_current)} players")
    
    # Load players_ALL_LEAGUES
    df_all_leagues = pd.read_csv('players_ALL_LEAGUES.csv')
    print(f"   ✅ All leagues database: {len(df_all_leagues)} players")
    
    # Extract player IDs from both databases
    df_current['current_player_id'] = df_current['profile_url'].apply(extract_player_id_from_url)
    df_all_leagues['all_leagues_player_id'] = df_all_leagues['profile_url'].apply(extract_player_id_from_url)
    
    # Get unique player IDs
    current_ids = set(df_current['current_player_id'].dropna())
    all_leagues_ids = set(df_all_leagues['all_leagues_player_id'].dropna())
    
    print(f"   📊 Current database unique IDs: {len(current_ids)}")
    print(f"   📊 All leagues unique IDs: {len(all_leagues_ids)}")
    
    # Find missing players
    missing_ids = all_leagues_ids - current_ids
    print(f"   📊 Missing player IDs: {len(missing_ids)}")
    
    # Get the missing players from all_leagues
    df_missing = df_all_leagues[df_all_leagues['all_leagues_player_id'].isin(missing_ids)]
    
    print(f"   ✅ Found {len(df_missing)} missing players")
    
    # Show examples of missing players
    print(f"\n📋 EXAMPLES OF MISSING PLAYERS:")
    examples = df_missing[['full_name', 'team_name', 'competition']].head(10)
    for _, row in examples.iterrows():
        print(f"   • {row['full_name']} - {row['team_name']} ({row['competition']})")
    
    # Save missing players
    missing_file = 'missing_players_from_all_leagues.csv'
    df_missing.to_csv(missing_file, index=False)
    print(f"\n💾 Saved missing players to: {missing_file}")
    
    return df_missing

def enrich_missing_players_with_player_data(df_missing):
    """Enrich missing players with data from Player table in dev 2.db"""
    print(f"\n🔍 Enriching {len(df_missing)} missing players with Player table data...")
    
    # Extract player IDs
    player_ids = df_missing['all_leagues_player_id'].dropna().astype(int).tolist()
    print(f"   📊 Player IDs to enrich: {len(player_ids)}")
    
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        print("🔍 Extracting player data from Player table...")
        
        # Query to get player data
        query = """
        SELECT 
            id,
            url,
            name,
            date_of_birth,
            is_retired,
            retired_since,
            foot,
            retrieved_at
        FROM Player 
        WHERE id IN ({})
        """.format(','.join(['?' for _ in player_ids]))
        
        cursor.execute(query, player_ids)
        results = cursor.fetchall()
        
        print(f"   📊 Found {len(results)} players in Player table")
        
        # Process results
        player_data = {}
        for row in results:
            player_id, url, name, date_of_birth, is_retired, retired_since, foot, retrieved_at = row
            
            # Convert timestamps to readable dates
            dob_readable = None
            if date_of_birth:
                try:
                    dob_readable = datetime.fromtimestamp(date_of_birth / 1000).strftime('%Y-%m-%d')
                except:
                    dob_readable = None
            
            retired_since_readable = None
            if retired_since:
                try:
                    retired_since_readable = datetime.fromtimestamp(retired_since / 1000).strftime('%Y-%m-%d')
                except:
                    retired_since_readable = None
            
            retrieved_at_readable = None
            if retrieved_at:
                try:
                    retrieved_at_readable = datetime.fromtimestamp(retrieved_at / 1000).strftime('%Y-%m-%d')
                except:
                    retrieved_at_readable = None
            
            player_data[player_id] = {
                'player_id': player_id,
                'player_url': url,
                'player_name': name,
                'player_date_of_birth': dob_readable,
                'is_retired': bool(is_retired) if is_retired is not None else None,
                'retired_since': retired_since_readable,
                'foot': foot,
                'data_retrieved_at': retrieved_at_readable
            }
        
        print(f"   ✅ Processed {len(player_data)} players")
        
        # Convert to DataFrame
        df_player_data = pd.DataFrame(list(player_data.values()))
        
        # Show statistics
        print(f"\n📊 PLAYER DATA STATISTICS:")
        print(f"   Players with date of birth: {df_player_data['player_date_of_birth'].notna().sum()}")
        print(f"   Active players: {(df_player_data['is_retired'] == False).sum()}")
        print(f"   Retired players: {(df_player_data['is_retired'] == True).sum()}")
        print(f"   Players with foot data: {df_player_data['foot'].notna().sum()}")
        
        # Analyze foot preferences
        foot_data = df_player_data['foot'].value_counts()
        print(f"\n📋 Foot preferences:")
        for foot, count in foot_data.items():
            print(f"   {foot}: {count}")
        
        # Show examples
        print(f"\n📋 EXAMPLES OF ENRICHED PLAYERS:")
        examples = df_player_data.head(10)[
            ['player_id', 'player_name', 'is_retired', 'foot', 'player_date_of_birth', 'retired_since']
        ]
        for _, row in examples.iterrows():
            status = "Retired" if row['is_retired'] else "Active"
            print(f"   ID: {row['player_id']}, Name: {row['player_name']}, Status: {status}, "
                  f"Foot: {row['foot']}, DOB: {row['player_date_of_birth']}, Retired: {row['retired_since']}")
        
        # Save player data
        player_data_file = 'missing_players_player_data.csv'
        df_player_data.to_csv(player_data_file, index=False)
        print(f"\n💾 Saved player data to: {player_data_file}")
        
        # Now merge with missing players
        print(f"\n🔧 Merging missing players with player data...")
        
        # Prepare missing players for merge
        df_missing_clean = df_missing.copy()
        df_missing_clean = df_missing_clean.rename(columns={'all_leagues_player_id': 'player_id'})
        
        # Merge the data
        df_enriched = df_missing_clean.merge(
            df_player_data,
            on='player_id',
            how='left'
        )
        
        # Statistics after merge
        enriched_with_data = df_enriched['player_name'].notna().sum()
        print(f"   📊 Missing players enriched with Player table data: {enriched_with_data}")
        
        # Show examples of final enriched data
        print(f"\n📋 EXAMPLES OF FINAL ENRICHED MISSING PLAYERS:")
        examples = df_enriched[df_enriched['player_name'].notna()][
            ['full_name', 'team_name', 'competition', 'player_name', 'is_retired', 'foot', 'player_date_of_birth']
        ].head(10)
        for _, row in examples.iterrows():
            status = "Retired" if row['is_retired'] else "Active"
            print(f"   {row['full_name']} ({row['team_name']}, {row['competition']}) - "
                  f"Name: {row['player_name']}, Status: {status}, Foot: {row['foot']}, DOB: {row['player_date_of_birth']}")
        
        # Save the final enriched missing players
        final_output = 'missing_players_enriched.csv'
        df_enriched.to_csv(final_output, index=False)
        
        print(f"\n💾 Saved enriched missing players to: {final_output}")
        print(f"📊 Total missing players: {len(df_enriched)}")
        print(f"📊 Enriched with Player table data: {enriched_with_data}")
        
        conn.close()
        
        return df_enriched
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting missing players extraction and enrichment...")
    
    try:
        # Step 1: Find missing players
        df_missing = find_missing_players()
        
        if len(df_missing) > 0:
            # Step 2: Enrich with Player table data
            df_enriched = enrich_missing_players_with_player_data(df_missing)
            
            if df_enriched is not None:
                print(f"\n🎉 Successfully extracted and enriched missing players!")
                print(f"📁 Missing players: missing_players_from_all_leagues.csv")
                print(f"📁 Player data: missing_players_player_data.csv")
                print(f"📁 Enriched missing players: missing_players_enriched.csv")
            else:
                print(f"\n❌ Failed to enrich missing players")
        else:
            print(f"\n✅ No missing players found - all players are already in the database!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
