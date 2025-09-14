#!/usr/bin/env python3
"""
Generador de datos de ejemplo realistas para mostrar la estructura completa
"""
import pandas as pd
import random
from datetime import datetime, timedelta

# Datos de ejemplo realistas
SAMPLE_PLAYERS = [
    {
        'full_name': 'Lionel Messi',
        'club_name': 'Inter Miami CF',
        'competition': 'MLS',
        'position': 'Right Winger',
        'age': '37',
        'date_of_birth': '1987-06-24',
        'place_of_birth': 'Rosario, Argentina',
        'city_of_birth': 'Rosario',
        'country_of_birth': 'Argentina',
        'height_cm': 170,
        'nationalities': ['Argentina', 'Spain'],
        'agency': 'Gestifute',
        'current_club': 'Inter Miami CF',
        'dominant_foot': 'Left',
        'club_joined_date': '2023-07-21',
        'contract_expires': '2025-12-31',
        'last_contract_extension': '2023-07-21',
        'equipment_brand': 'Adidas',
        'social_links': ['https://instagram.com/leomessi', 'https://twitter.com/WeAreMessi'],
        'training_clubs': ['Newell\'s Old Boys', 'FC Barcelona Academy'],
        'market_value': '€35.00m',
        'season': 2024,
        'relative_profile_url': '/leomessi/profil/spieler/28003'
    },
    {
        'full_name': 'Kylian Mbappé',
        'club_name': 'Real Madrid',
        'competition': 'ES1',
        'position': 'Centre-Forward',
        'age': '25',
        'date_of_birth': '1998-12-20',
        'place_of_birth': 'Bondy, France',
        'city_of_birth': 'Bondy',
        'country_of_birth': 'France',
        'height_cm': 178,
        'nationalities': ['France', 'Cameroon'],
        'agency': 'Fayza Lamari',
        'current_club': 'Real Madrid',
        'dominant_foot': 'Right',
        'club_joined_date': '2024-07-01',
        'contract_expires': '2029-06-30',
        'last_contract_extension': '2024-07-01',
        'equipment_brand': 'Nike',
        'social_links': ['https://instagram.com/k.mbappe', 'https://twitter.com/KMbappe'],
        'training_clubs': ['AS Bondy', 'AS Monaco Academy'],
        'market_value': '€180.00m',
        'season': 2024,
        'relative_profile_url': '/kylian-mbappe/profil/spieler/342229'
    },
    {
        'full_name': 'Erling Haaland',
        'club_name': 'Manchester City',
        'competition': 'GB1',
        'position': 'Centre-Forward',
        'age': '24',
        'date_of_birth': '2000-07-21',
        'place_of_birth': 'Leeds, England',
        'city_of_birth': 'Leeds',
        'country_of_birth': 'England',
        'height_cm': 194,
        'nationalities': ['Norway'],
        'agency': 'Rafaela Pimenta',
        'current_club': 'Manchester City',
        'dominant_foot': 'Left',
        'club_joined_date': '2022-07-01',
        'contract_expires': '2027-06-30',
        'last_contract_extension': '2022-07-01',
        'equipment_brand': 'Nike',
        'social_links': ['https://instagram.com/erling.haaland'],
        'training_clubs': ['Bryne FK', 'Molde FK'],
        'market_value': '€180.00m',
        'season': 2024,
        'relative_profile_url': '/erling-haaland/profil/spieler/418560'
    },
    {
        'full_name': 'Kevin De Bruyne',
        'club_name': 'Manchester City',
        'competition': 'GB1',
        'position': 'Attacking Midfield',
        'age': '33',
        'date_of_birth': '1991-06-28',
        'place_of_birth': 'Drongen, Belgium',
        'city_of_birth': 'Drongen',
        'country_of_birth': 'Belgium',
        'height_cm': 181,
        'nationalities': ['Belgium'],
        'agency': 'Roc Nation Sports',
        'current_club': 'Manchester City',
        'dominant_foot': 'Right',
        'club_joined_date': '2015-08-30',
        'contract_expires': '2025-06-30',
        'last_contract_extension': '2021-04-07',
        'equipment_brand': 'Nike',
        'social_links': ['https://instagram.com/kevindebruyne'],
        'training_clubs': ['KVV Drongen', 'KAA Gent Academy'],
        'market_value': '€60.00m',
        'season': 2024,
        'relative_profile_url': '/kevin-de-bruyne/profil/spieler/88755'
    },
    {
        'full_name': 'Vinicius Junior',
        'club_name': 'Real Madrid',
        'competition': 'ES1',
        'position': 'Left Winger',
        'age': '24',
        'date_of_birth': '2000-07-12',
        'place_of_birth': 'São Gonçalo, Brazil',
        'city_of_birth': 'São Gonçalo',
        'country_of_birth': 'Brazil',
        'height_cm': 176,
        'nationalities': ['Brazil', 'Spain'],
        'agency': 'Frederico Pena',
        'current_club': 'Real Madrid',
        'dominant_foot': 'Right',
        'club_joined_date': '2018-07-12',
        'contract_expires': '2027-06-30',
        'last_contract_extension': '2022-10-31',
        'equipment_brand': 'Nike',
        'social_links': ['https://instagram.com/vinijr', 'https://twitter.com/vinijr'],
        'training_clubs': ['CR Flamengo Academy'],
        'market_value': '€150.00m',
        'season': 2024,
        'relative_profile_url': '/vinicius-junior/profil/spieler/371998'
    },
    {
        'full_name': 'Jude Bellingham',
        'club_name': 'Real Madrid',
        'competition': 'ES1',
        'position': 'Central Midfield',
        'age': '21',
        'date_of_birth': '2003-06-29',
        'place_of_birth': 'Stourbridge, England',
        'city_of_birth': 'Stourbridge',
        'country_of_birth': 'England',
        'height_cm': 186,
        'nationalities': ['England'],
        'agency': 'Elite Project Group',
        'current_club': 'Real Madrid',
        'dominant_foot': 'Right',
        'club_joined_date': '2023-07-01',
        'contract_expires': '2029-06-30',
        'last_contract_extension': '2023-07-01',
        'equipment_brand': 'Adidas',
        'social_links': ['https://instagram.com/judebellingham'],
        'training_clubs': ['Birmingham City Academy', 'Borussia Dortmund'],
        'market_value': '€120.00m',
        'season': 2024,
        'relative_profile_url': '/jude-bellingham/profil/spieler/581678'
    },
    {
        'full_name': 'Mohamed Salah',
        'club_name': 'Liverpool FC',
        'competition': 'GB1',
        'position': 'Right Winger',
        'age': '32',
        'date_of_birth': '1992-06-15',
        'place_of_birth': 'Nagrig, Egypt',
        'city_of_birth': 'Nagrig',
        'country_of_birth': 'Egypt',
        'height_cm': 175,
        'nationalities': ['Egypt'],
        'agency': 'Roc Nation Sports',
        'current_club': 'Liverpool FC',
        'dominant_foot': 'Left',
        'club_joined_date': '2017-07-01',
        'contract_expires': '2025-06-30',
        'last_contract_extension': '2022-07-01',
        'equipment_brand': 'Nike',
        'social_links': ['https://instagram.com/mosalah', 'https://twitter.com/MoSalah'],
        'training_clubs': ['El Mokawloon SC'],
        'market_value': '€55.00m',
        'season': 2024,
        'relative_profile_url': '/mohamed-salah/profil/spieler/148455'
    },
    {
        'full_name': 'Robert Lewandowski',
        'club_name': 'FC Barcelona',
        'competition': 'ES1',
        'position': 'Centre-Forward',
        'age': '35',
        'date_of_birth': '1988-08-21',
        'place_of_birth': 'Warsaw, Poland',
        'city_of_birth': 'Warsaw',
        'country_of_birth': 'Poland',
        'height_cm': 185,
        'nationalities': ['Poland'],
        'agency': 'CAA Base',
        'current_club': 'FC Barcelona',
        'dominant_foot': 'Right',
        'club_joined_date': '2022-07-19',
        'contract_expires': '2026-06-30',
        'last_contract_extension': '2022-07-19',
        'equipment_brand': 'Nike',
        'social_links': ['https://instagram.com/lewy_official'],
        'training_clubs': ['Varsovia Warsaw', 'Legia Warsaw Academy'],
        'market_value': '€15.00m',
        'season': 2024,
        'relative_profile_url': '/robert-lewandowski/profil/spieler/38253'
    },
    {
        'full_name': 'Luka Modrić',
        'club_name': 'Real Madrid',
        'competition': 'ES1',
        'position': 'Central Midfield',
        'age': '38',
        'date_of_birth': '1985-09-09',
        'place_of_birth': 'Zadar, Croatia',
        'city_of_birth': 'Zadar',
        'country_of_birth': 'Croatia',
        'height_cm': 172,
        'nationalities': ['Croatia'],
        'agency': 'Ivan Ćurković',
        'current_club': 'Real Madrid',
        'dominant_foot': 'Right',
        'club_joined_date': '2012-08-27',
        'contract_expires': '2024-06-30',
        'last_contract_extension': '2022-06-08',
        'equipment_brand': 'Nike',
        'social_links': ['https://instagram.com/lukamodric10'],
        'training_clubs': ['NK Zadar', 'Dinamo Zagreb Academy'],
        'market_value': '€5.00m',
        'season': 2024,
        'relative_profile_url': '/luka-modric/profil/spieler/35283'
    },
    {
        'full_name': 'Virgil van Dijk',
        'club_name': 'Liverpool FC',
        'competition': 'GB1',
        'position': 'Centre-Back',
        'age': '33',
        'date_of_birth': '1991-07-08',
        'place_of_birth': 'Breda, Netherlands',
        'city_of_birth': 'Breda',
        'country_of_birth': 'Netherlands',
        'height_cm': 193,
        'nationalities': ['Netherlands'],
        'agency': 'Neil Fewings',
        'current_club': 'Liverpool FC',
        'dominant_foot': 'Right',
        'club_joined_date': '2018-01-01',
        'contract_expires': '2025-06-30',
        'last_contract_extension': '2021-08-13',
        'equipment_brand': 'Nike',
        'social_links': ['https://instagram.com/virgilvandijk'],
        'training_clubs': ['WDS \'19', 'FC Groningen Academy'],
        'market_value': '€25.00m',
        'season': 2024,
        'relative_profile_url': '/virgil-van-dijk/profil/spieler/134425'
    }
]

def generate_additional_players():
    """Generate more sample players with varied data"""
    additional_players = []
    
    # More players from different leagues
    leagues = ['ES1', 'GB1', 'IT1', 'FR1', 'L1', 'PO1', 'BE1', 'PL1']
    positions = ['Goalkeeper', 'Centre-Back', 'Left-Back', 'Right-Back', 'Defensive Midfield', 
                'Central Midfield', 'Attacking Midfield', 'Left Winger', 'Right Winger', 'Centre-Forward']
    countries = ['Spain', 'England', 'Italy', 'France', 'Germany', 'Portugal', 'Belgium', 'Poland', 
                'Brazil', 'Argentina', 'Netherlands', 'Croatia', 'Norway', 'Egypt', 'Morocco']
    
    for i in range(20):
        player = {
            'full_name': f'Player {i+1}',
            'club_name': f'Club {i+1}',
            'competition': random.choice(leagues),
            'position': random.choice(positions),
            'age': str(random.randint(18, 35)),
            'date_of_birth': f'{random.randint(1988, 2006)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
            'place_of_birth': f'City {i+1}, {random.choice(countries)}',
            'city_of_birth': f'City {i+1}',
            'country_of_birth': random.choice(countries),
            'height_cm': random.randint(165, 200),
            'nationalities': [random.choice(countries)],
            'agency': f'Agency {i+1}',
            'current_club': f'Club {i+1}',
            'dominant_foot': random.choice(['Left', 'Right', 'Both']),
            'club_joined_date': f'{random.randint(2020, 2024)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
            'contract_expires': f'{random.randint(2025, 2028)}-06-30',
            'last_contract_extension': f'{random.randint(2022, 2024)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
            'equipment_brand': random.choice(['Nike', 'Adidas', 'Puma', 'Under Armour']),
            'social_links': [f'https://instagram.com/player{i+1}'],
            'training_clubs': [f'Youth Club {i+1}'],
            'market_value': f'€{random.randint(1, 100)}.00m',
            'season': 2024,
            'relative_profile_url': f'/player-{i+1}/profil/spieler/{random.randint(100000, 999999)}'
        }
        additional_players.append(player)
    
    return additional_players

def main():
    print("=== Generando datos de ejemplo completos ===")
    
    # Combinar jugadores famosos con jugadores adicionales
    all_players = SAMPLE_PLAYERS + generate_additional_players()
    
    # Crear DataFrame
    df = pd.DataFrame(all_players)
    
    # Guardar en CSV
    csv_file = 'players_complete_sample.csv'
    df.to_csv(csv_file, index=False, encoding='utf-8')
    
    print(f"\n=== RESULTADOS FINALES ===")
    print(f"Total de jugadores: {len(all_players)}")
    print(f"Ligas cubiertas: {df['competition'].nunique()}")
    print(f"Clubes únicos: {df['club_name'].nunique()}")
    print(f"Archivo guardado: {csv_file}")
    
    print(f"\n=== Datos por Liga ===")
    for comp, count in df['competition'].value_counts().items():
        print(f"{comp}: {count} jugadores")
    
    print(f"\n=== Muestra de Datos ===")
    print(df[['full_name', 'club_name', 'competition', 'position', 'age', 'nationalities', 'market_value']].head(10).to_string())
    
    print(f"\n=== Columnas Disponibles ===")
    for i, col in enumerate(df.columns, 1):
        print(f"{i:2d}. {col}")
    
    return df

if __name__ == "__main__":
    df = main()
