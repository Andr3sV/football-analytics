#!/usr/bin/env python3
"""
Expand Youth Clubs - Extract youth club data from dev 2.db and expand the database
so each player has one row per youth club they played for
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

def expand_youth_clubs():
    """Expand the database with youth club data from dev 2.db"""
    print("🔄 Loading final combined database...")
    
    # Load the final database
    df_final = pd.read_csv('all_players_combined_database_final_fixed.csv')
    print(f"   ✅ Loaded {len(df_final)} players from final database")
    
    # Extract player IDs
    df_final['player_id'] = df_final['profile_url'].apply(extract_player_id_from_url)
    player_ids = df_final['player_id'].dropna().astype(int).tolist()
    
    print(f"   📊 Player IDs to check: {len(player_ids)}")
    
    try:
        print("🔍 Connecting to dev 2.db...")
        conn = sqlite3.connect('db-old/dev 2.db')
        cursor = conn.cursor()
        
        print("🔍 Extracting youth club data from YouthClub table...")
        
        # Query to get youth club data
        query = """
        SELECT 
            player_id,
            name as youth_club_name
        FROM YouthClub 
        WHERE player_id IN ({})
        ORDER BY player_id
        """.format(','.join(['?' for _ in player_ids]))
        
        cursor.execute(query, player_ids)
        results = cursor.fetchall()
        
        print(f"   📊 Found {len(results)} youth club records")
        
        # Process results
        youth_clubs = {}
        for player_id, youth_club_name in results:
            if player_id not in youth_clubs:
                youth_clubs[player_id] = []
            youth_clubs[player_id].append(youth_club_name)
        
        print(f"   ✅ Processed {len(youth_clubs)} players with youth club data")
        
        # Analyze youth club distribution
        players_with_multiple_clubs = {pid: clubs for pid, clubs in youth_clubs.items() if len(clubs) > 1}
        players_with_single_club = {pid: clubs for pid, clubs in youth_clubs.items() if len(clubs) == 1}
        
        print(f"\n📊 YOUTH CLUB ANALYSIS:")
        print(f"   Players with youth club data: {len(youth_clubs)}")
        print(f"   Players with single youth club: {len(players_with_single_club)}")
        print(f"   Players with multiple youth clubs: {len(players_with_multiple_clubs)}")
        
        # Show examples of players with multiple youth clubs
        print(f"\n📋 EXAMPLES OF PLAYERS WITH MULTIPLE YOUTH CLUBS:")
        examples = list(players_with_multiple_clubs.items())[:10]
        for player_id, clubs in examples:
            player_info = df_final[df_final['player_id'] == player_id]
            if len(player_info) > 0:
                player_name = player_info.iloc[0]['full_name']
                print(f"   • {player_name} (ID: {player_id}): {len(clubs)} clubs - {', '.join(clubs)}")
        
        # Top youth clubs
        print(f"\n📋 TOP YOUTH CLUBS BY PLAYER COUNT:")
        all_youth_clubs = [club for clubs in youth_clubs.values() for club in clubs]
        club_counts = pd.Series(all_youth_clubs).value_counts().head(15)
        for club, count in club_counts.items():
            print(f"   {club}: {count} players")
        
        # Expand the database
        print(f"\n🔧 Expanding database with youth club data...")
        
        expanded_rows = []
        players_expanded = 0
        total_new_rows = 0
        
        for idx, row in df_final.iterrows():
            player_id = row['player_id']
            
            if pd.isna(player_id):
                # Keep players without player_id as is
                expanded_rows.append(row)
                continue
            
            player_id = int(player_id)
            
            if player_id in youth_clubs:
                clubs = youth_clubs[player_id]
                
                if len(clubs) > 1:
                    # Player has multiple youth clubs - create multiple rows
                    for club in clubs:
                        new_row = row.copy()
                        new_row['youth_club'] = club
                        expanded_rows.append(new_row)
                    
                    players_expanded += 1
                    total_new_rows += len(clubs) - 1  # -1 because we replace 1 row with len(clubs) rows
                
                elif len(clubs) == 1:
                    # Player has one youth club - update the existing row
                    new_row = row.copy()
                    new_row['youth_club'] = clubs[0]
                    expanded_rows.append(new_row)
                
                else:
                    # Player has no youth clubs - keep as is
                    expanded_rows.append(row)
            
            else:
                # Player not found in youth clubs table - keep as is
                expanded_rows.append(row)
        
        # Create expanded dataframe
        df_expanded = pd.DataFrame(expanded_rows)
        
        print(f"   ✅ Database expanded:")
        print(f"      Players with multiple youth clubs: {players_expanded}")
        print(f"      Additional rows created: {total_new_rows}")
        print(f"      Original rows: {len(df_final)}")
        print(f"      Final rows: {len(df_expanded)}")
        
        # Statistics after expansion
        print(f"\n📊 EXPANSION STATISTICS:")
        youth_club_coverage = df_expanded['youth_club'].notna().sum()
        print(f"   Players with youth club data: {youth_club_coverage}")
        print(f"   Coverage: {youth_club_coverage}/{len(df_expanded)} ({youth_club_coverage/len(df_expanded)*100:.1f}%)")
        
        # Show examples of expanded players
        print(f"\n📋 EXAMPLES OF EXPANDED PLAYERS:")
        expanded_examples = df_expanded[
            df_expanded['player_id'].isin([pid for pid, clubs in list(players_with_multiple_clubs.items())[:5]])
        ][
            ['full_name', 'team_name', 'competition', 'youth_club', 'player_id']
        ]
        
        for _, row in expanded_examples.iterrows():
            print(f"   • {row['full_name']} ({row['team_name']}, {row['competition']}) - Youth Club: {row['youth_club']}")
        
        # Analyze youth club distribution in expanded data
        print(f"\n📊 YOUTH CLUB DISTRIBUTION IN EXPANDED DATA:")
        expanded_youth_counts = df_expanded['youth_club'].value_counts().head(10)
        for club, count in expanded_youth_counts.items():
            if pd.notna(club):
                print(f"   {club}: {count} players")
        
        conn.close()
        
        # Save the expanded database
        output_file = 'all_players_combined_database_expanded_youth_clubs.csv'
        df_expanded.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved expanded database to: {output_file}")
        print(f"📊 Total rows: {len(df_expanded)}")
        print(f"📊 Players with youth club data: {youth_club_coverage}")
        
        return df_expanded
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting youth clubs expansion...")
    
    try:
        expanded_df = expand_youth_clubs()
        
        if expanded_df is not None:
            print(f"\n🎉 Successfully expanded database with youth club data!")
            print(f"📁 Output file: all_players_combined_database_expanded_youth_clubs.csv")
            print(f"📊 Total rows: {len(expanded_df)}")
        else:
            print(f"\n❌ Failed to expand database")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
