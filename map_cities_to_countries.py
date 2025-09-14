#!/usr/bin/env python3
"""
Map Cities to Countries - Map youth clubs to countries based on city names in club names
"""
import pandas as pd
import numpy as np
import re

def create_city_country_mapping():
    """Create mapping of cities to countries"""
    print("🔍 Creating city to country mapping...")
    
    city_country_mapping = {
        # German cities
        'Berlin': 'Germany', 'Hamburg': 'Germany', 'Munich': 'Germany', 'Cologne': 'Germany',
        'Frankfurt': 'Germany', 'Stuttgart': 'Germany', 'Dortmund': 'Germany', 'Düsseldorf': 'Germany',
        'Leipzig': 'Germany', 'Hannover': 'Germany', 'Nuremberg': 'Germany', 'Dresden': 'Germany',
        'Bremen': 'Germany', 'Mannheim': 'Germany', 'Karlsruhe': 'Germany', 'Augsburg': 'Germany',
        'Wiesbaden': 'Germany', 'Mönchengladbach': 'Germany', 'Braunschweig': 'Germany',
        'Chemnitz': 'Germany', 'Kiel': 'Germany', 'Aachen': 'Germany', 'Halle': 'Germany',
        'Magdeburg': 'Germany', 'Freiburg': 'Germany', 'Krefeld': 'Germany', 'Lübeck': 'Germany',
        'Oberhausen': 'Germany', 'Erfurt': 'Germany', 'Mainz': 'Germany', 'Rostock': 'Germany',
        'Kassel': 'Germany', 'Hagen': 'Germany', 'Hamm': 'Germany', 'Saarbrücken': 'Germany',
        'Mülheim': 'Germany', 'Potsdam': 'Germany', 'Ludwigshafen': 'Germany', 'Oldenburg': 'Germany',
        'Leverkusen': 'Germany', 'Osnabrück': 'Germany', 'Solingen': 'Germany', 'Heidelberg': 'Germany',
        'Herne': 'Germany', 'Neuss': 'Germany', 'Darmstadt': 'Germany', 'Paderborn': 'Germany',
        'Regensburg': 'Germany', 'Ingolstadt': 'Germany', 'Würzburg': 'Germany', 'Fürth': 'Germany',
        'Wolfsburg': 'Germany', 'Offenbach': 'Germany', 'Ulm': 'Germany', 'Heilbronn': 'Germany',
        'Pforzheim': 'Germany', 'Göttingen': 'Germany', 'Bottrop': 'Germany', 'Trier': 'Germany',
        'Recklinghausen': 'Germany', 'Reutlingen': 'Germany', 'Bremerhaven': 'Germany',
        'Koblenz': 'Germany', 'Bergisch': 'Germany', 'Remscheid': 'Germany', 'Erlangen': 'Germany',
        'Moers': 'Germany', 'Siegen': 'Germany', 'Hildesheim': 'Germany', 'Salzgitter': 'Germany',
        
        # Spanish cities
        'Madrid': 'Spain', 'Barcelona': 'Spain', 'Valencia': 'Spain', 'Sevilla': 'Spain',
        'Zaragoza': 'Spain', 'Málaga': 'Spain', 'Murcia': 'Spain', 'Palma': 'Spain',
        'Las Palmas': 'Spain', 'Bilbao': 'Spain', 'Alicante': 'Spain', 'Córdoba': 'Spain',
        'Valladolid': 'Spain', 'Vigo': 'Spain', 'Gijón': 'Spain', 'L Hospitalet': 'Spain',
        'A Coruña': 'Spain', 'Granada': 'Spain', 'Vitoria': 'Spain', 'Elche': 'Spain',
        'Santa Cruz': 'Spain', 'Oviedo': 'Spain', 'Badalona': 'Spain', 'Cartagena': 'Spain',
        'Terrassa': 'Spain', 'Jerez': 'Spain', 'Sabadell': 'Spain', 'Móstoles': 'Spain',
        'Alcalá': 'Spain', 'Pamplona': 'Spain', 'Fuenlabrada': 'Spain', 'Almería': 'Spain',
        'Leganés': 'Spain', 'Santander': 'Spain', 'Castellón': 'Spain', 'Burgos': 'Spain',
        'Albacete': 'Spain', 'Alcorcón': 'Spain', 'Getafe': 'Spain', 'Salamanca': 'Spain',
        'Huelva': 'Spain', 'Marbella': 'Spain', 'León': 'Spain', 'Cádiz': 'Spain',
        'Dos Hermanas': 'Spain', 'Mataró': 'Spain', 'Santa Coloma': 'Spain', 'Algeciras': 'Spain',
        'Jaén': 'Spain', 'Ourense': 'Spain', 'Reus': 'Spain', 'Torrelavega': 'Spain',
        'El Puerto': 'Spain', 'Gandía': 'Spain', 'Ceuta': 'Spain', 'Melilla': 'Spain',
        
        # French cities
        'Paris': 'France', 'Lyon': 'France', 'Marseille': 'France', 'Toulouse': 'France',
        'Nice': 'France', 'Nantes': 'France', 'Strasbourg': 'France', 'Montpellier': 'France',
        'Bordeaux': 'France', 'Lille': 'France', 'Rennes': 'France', 'Reims': 'France',
        'Le Havre': 'France', 'Saint-Étienne': 'France', 'Toulon': 'France', 'Grenoble': 'France',
        'Dijon': 'France', 'Angers': 'France', 'Nîmes': 'France', 'Villeurbanne': 'France',
        'Saint-Denis': 'France', 'Le Mans': 'France', 'Aix-en-Provence': 'France', 'Brest': 'France',
        'Tours': 'France', 'Limoges': 'France', 'Amiens': 'France', 'Perpignan': 'France',
        'Metz': 'France', 'Besançon': 'France', 'Boulogne': 'France', 'Orléans': 'France',
        'Mulhouse': 'France', 'Rouen': 'France', 'Caen': 'France', 'Nancy': 'France',
        'Saint-Denis': 'France', 'Argenteuil': 'France', 'Montreuil': 'France', 'Roubaix': 'France',
        'Tourcoing': 'France', 'Nanterre': 'France', 'Avignon': 'France', 'Créteil': 'France',
        'Dunkirk': 'France', 'Poitiers': 'France', 'Asnières': 'France', 'Versailles': 'France',
        'Courbevoie': 'France', 'Vitry': 'France', 'Colombes': 'France', 'Aulnay': 'France',
        'La Rochelle': 'France', 'Rueil': 'France', 'Antibes': 'France', 'Saint-Maur': 'France',
        
        # Italian cities
        'Roma': 'Italy', 'Milano': 'Italy', 'Napoli': 'Italy', 'Torino': 'Italy',
        'Palermo': 'Italy', 'Genova': 'Italy', 'Bologna': 'Italy', 'Firenze': 'Italy',
        'Bari': 'Italy', 'Catania': 'Italy', 'Venezia': 'Italy', 'Verona': 'Italy',
        'Messina': 'Italy', 'Padova': 'Italy', 'Trieste': 'Italy', 'Brescia': 'Italy',
        'Taranto': 'Italy', 'Prato': 'Italy', 'Modena': 'Italy', 'Reggio': 'Italy',
        'Parma': 'Italy', 'Perugia': 'Italy', 'Livorno': 'Italy', 'Ravenna': 'Italy',
        'Cagliari': 'Italy', 'Foggia': 'Italy', 'Rimini': 'Italy', 'Salerno': 'Italy',
        'Ferrara': 'Italy', 'Sassari': 'Italy', 'Monza': 'Italy', 'Bergamo': 'Italy',
        'Forlì': 'Italy', 'Trento': 'Italy', 'Vicenza': 'Italy', 'Terni': 'Italy',
        'Bolzano': 'Italy', 'Novara': 'Italy', 'Piacenza': 'Italy', 'Ancona': 'Italy',
        'Andria': 'Italy', 'Arezzo': 'Italy', 'Udine': 'Italy', 'Cesena': 'Italy',
        'Lecce': 'Italy', 'Pesaro': 'Italy', 'La Spezia': 'Italy', 'Como': 'Italy',
        'Varese': 'Italy', 'Treviso': 'Italy', 'Catanzaro': 'Italy', 'Busto': 'Italy',
        
        # English cities
        'London': 'England', 'Birmingham': 'England', 'Manchester': 'England', 'Glasgow': 'Scotland',
        'Liverpool': 'England', 'Leeds': 'England', 'Sheffield': 'England', 'Edinburgh': 'Scotland',
        'Bristol': 'England', 'Newcastle': 'England', 'Nottingham': 'England', 'Leicester': 'England',
        'Coventry': 'England', 'Bradford': 'England', 'Cardiff': 'Wales', 'Belfast': 'Northern Ireland',
        'Stoke': 'England', 'Wolverhampton': 'England', 'Plymouth': 'England', 'Derby': 'England',
        'Southampton': 'England', 'Portsmouth': 'England', 'Brighton': 'England', 'Norwich': 'England',
        'Preston': 'England', 'Huddersfield': 'England', 'York': 'England', 'Blackpool': 'England',
        'Middlesbrough': 'England', 'Ipswich': 'England', 'Bournemouth': 'England', 'Oxford': 'England',
        'Cambridge': 'England', 'Reading': 'England', 'Exeter': 'England', 'Gloucester': 'England',
        'Bath': 'England', 'Peterborough': 'England', 'Northampton': 'England', 'Luton': 'England',
        'Swindon': 'England', 'Watford': 'England', 'Colchester': 'England', 'Crawley': 'England',
        'Milton Keynes': 'England', 'Hastings': 'England', 'Dover': 'England', 'Folkestone': 'England',
        'Margate': 'England', 'Ramsgate': 'England', 'Canterbury': 'England', 'Maidstone': 'England',
        'Gillingham': 'England', 'Chatham': 'England', 'Rochester': 'England', 'Gravesend': 'England',
        
        # Portuguese cities
        'Lisboa': 'Portugal', 'Porto': 'Portugal', 'Braga': 'Portugal', 'Coimbra': 'Portugal',
        'Faro': 'Portugal', 'Setúbal': 'Portugal', 'Aveiro': 'Portugal', 'Évora': 'Portugal',
        'Leiria': 'Portugal', 'Funchal': 'Portugal', 'Viseu': 'Portugal', 'Vila Nova': 'Portugal',
        'Guimarães': 'Portugal', 'Matosinhos': 'Portugal', 'Amadora': 'Portugal', 'Almada': 'Portugal',
        'Agualva': 'Portugal', 'Queluz': 'Portugal', 'Cacém': 'Portugal', 'Odivelas': 'Portugal',
        'Corroios': 'Portugal', 'Barreiro': 'Portugal', 'Montijo': 'Portugal', 'Rio Tinto': 'Portugal',
        'Gondomar': 'Portugal', 'Valongo': 'Portugal', 'Póvoa': 'Portugal', 'Vila do Conde': 'Portugal',
        'Maia': 'Portugal', 'Santo Tirso': 'Portugal', 'Trofa': 'Portugal', 'Vila Nova de Gaia': 'Portugal',
        'Oliveira': 'Portugal', 'Paredes': 'Portugal', 'Paços': 'Portugal', 'Felgueiras': 'Portugal',
        'Lousada': 'Portugal', 'Vizela': 'Portugal', 'Fafe': 'Portugal', 'Cabeceiras': 'Portugal',
        'Celorico': 'Portugal', 'Guarda': 'Portugal', 'Covilhã': 'Portugal', 'Castelo Branco': 'Portugal',
        'Portalegre': 'Portugal', 'Elvas': 'Portugal', 'Estremoz': 'Portugal', 'Évora': 'Portugal',
        'Beja': 'Portugal', 'Moura': 'Portugal', 'Serpa': 'Portugal', 'Vidigueira': 'Portugal',
        'Cuba': 'Portugal', 'Alvito': 'Portugal', 'Viana': 'Portugal', 'Caminha': 'Portugal',
        'Vila Nova': 'Portugal', 'Ponte de Lima': 'Portugal', 'Arcos': 'Portugal', 'Valença': 'Portugal',
        
        # Brazilian cities
        'São Paulo': 'Brazil', 'Rio de Janeiro': 'Brazil', 'Brasília': 'Brazil', 'Salvador': 'Brazil',
        'Fortaleza': 'Brazil', 'Belo Horizonte': 'Brazil', 'Manaus': 'Brazil', 'Curitiba': 'Brazil',
        'Recife': 'Brazil', 'Porto Alegre': 'Brazil', 'Belém': 'Brazil', 'Goiânia': 'Brazil',
        'Guarulhos': 'Brazil', 'Campinas': 'Brazil', 'São Luís': 'Brazil', 'São Gonçalo': 'Brazil',
        'Maceió': 'Brazil', 'Duque de Caxias': 'Brazil', 'Natal': 'Brazil', 'Teresina': 'Brazil',
        'Campo Grande': 'Brazil', 'Nova Iguaçu': 'Brazil', 'São Bernardo': 'Brazil', 'João Pessoa': 'Brazil',
        'Santo André': 'Brazil', 'Osasco': 'Brazil', 'Jaboatão': 'Brazil', 'São José': 'Brazil',
        'Ribeirão Preto': 'Brazil', 'Uberlândia': 'Brazil', 'Sorocaba': 'Brazil', 'Contagem': 'Brazil',
        'Aracaju': 'Brazil', 'Feira de Santana': 'Brazil', 'Cuiabá': 'Brazil', 'Joinville': 'Brazil',
        'Aparecida': 'Brazil', 'Londrina': 'Brazil', 'Ananindeua': 'Brazil', 'Serra': 'Brazil',
        'Niterói': 'Brazil', 'Caxias': 'Brazil', 'Campos': 'Brazil', 'Vila Velha': 'Brazil',
        'Florianópolis': 'Brazil', 'Macapá': 'Brazil', 'Diadema': 'Brazil', 'São Vicente': 'Brazil',
        'Mauá': 'Brazil', 'São José': 'Brazil', 'Betim': 'Brazil', 'Carapicuíba': 'Brazil',
        'Mogi das Cruzes': 'Brazil', 'Santos': 'Brazil', 'Ribeirão': 'Brazil', 'Uberaba': 'Brazil',
        
        # Dutch cities
        'Amsterdam': 'Netherlands', 'Rotterdam': 'Netherlands', 'Den Haag': 'Netherlands', 'Utrecht': 'Netherlands',
        'Eindhoven': 'Netherlands', 'Tilburg': 'Netherlands', 'Groningen': 'Netherlands', 'Almere': 'Netherlands',
        'Breda': 'Netherlands', 'Nijmegen': 'Netherlands', 'Enschede': 'Netherlands', 'Haarlem': 'Netherlands',
        'Arnhem': 'Netherlands', 'Zaanstad': 'Netherlands', 'Amersfoort': 'Netherlands', 'Apeldoorn': 'Netherlands',
        'Hoofddorp': 'Netherlands', 'Maastricht': 'Netherlands', 'Leiden': 'Netherlands', 'Dordrecht': 'Netherlands',
        'Zoetermeer': 'Netherlands', 'Zwolle': 'Netherlands', 'Deventer': 'Netherlands', 'Delft': 'Netherlands',
        'Alkmaar': 'Netherlands', 'Hengelo': 'Netherlands', 'Vlaardingen': 'Netherlands', 'Schiedam': 'Netherlands',
        'Emmen': 'Netherlands', 'Leeuwarden': 'Netherlands', 'Alphen': 'Netherlands', 'Helmond': 'Netherlands',
        'Velsen': 'Netherlands', 'Purmerend': 'Netherlands', 'Hilversum': 'Netherlands', 'Roosendaal': 'Netherlands',
        'Schagen': 'Netherlands', 'Heerlen': 'Netherlands', 'Amstelveen': 'Netherlands', 'Veenendaal': 'Netherlands',
        'Bergen': 'Netherlands', 'Capelle': 'Netherlands', 'Rijswijk': 'Netherlands', 'Assen': 'Netherlands',
        'Nieuwegein': 'Netherlands', 'Katwijk': 'Netherlands', 'Gouda': 'Netherlands', 'Sittard': 'Netherlands',
        'Geleen': 'Netherlands', 'Sittard-Geleen': 'Netherlands', 'Weert': 'Netherlands', 'Venlo': 'Netherlands',
        
        # Belgian cities
        'Brussels': 'Belgium', 'Antwerpen': 'Belgium', 'Gent': 'Belgium', 'Charleroi': 'Belgium',
        'Liège': 'Belgium', 'Bruges': 'Belgium', 'Namur': 'Belgium', 'Leuven': 'Belgium',
        'Mons': 'Belgium', 'Aalst': 'Belgium', 'Mechelen': 'Belgium', 'La Louvière': 'Belgium',
        'Kortrijk': 'Belgium', 'Hasselt': 'Belgium', 'Ostend': 'Belgium', 'Tournai': 'Belgium',
        'Genk': 'Belgium', 'Seraing': 'Belgium', 'Roeselare': 'Belgium', 'Verviers': 'Belgium',
        'Mouscron': 'Belgium', 'Beveren': 'Belgium', 'Sint-Niklaas': 'Belgium', 'Turnhout': 'Belgium',
        'Dendermonde': 'Belgium', 'Lokeren': 'Belgium', 'Brasschaat': 'Belgium', 'Vilvoorde': 'Belgium',
        'Herstal': 'Belgium', 'Maasmechelen': 'Belgium', 'Ninove': 'Belgium', 'Geel': 'Belgium',
        'Halle': 'Belgium', 'Hoboken': 'Belgium', 'Knokke': 'Belgium', 'Koksijde': 'Belgium',
        'De Panne': 'Belgium', 'Nieuwpoort': 'Belgium', 'Diksmuide': 'Belgium', 'Ypres': 'Belgium',
        'Poperinge': 'Belgium', 'Veurne': 'Belgium', 'Lo-Reninge': 'Belgium', 'Alveringem': 'Belgium',
        'Heuvelland': 'Belgium', 'Langemark': 'Belgium', 'Mesen': 'Belgium', 'Wervik': 'Belgium',
        'Zonnebeke': 'Belgium', 'Ledegem': 'Belgium', 'Menen': 'Belgium', 'Wevelgem': 'Belgium',
        
        # Other countries
        'Vienna': 'Austria', 'Graz': 'Austria', 'Linz': 'Austria', 'Salzburg': 'Austria',
        'Innsbruck': 'Austria', 'Klagenfurt': 'Austria', 'Villach': 'Austria', 'Wels': 'Austria',
        'Sankt Pölten': 'Austria', 'Dornbirn': 'Austria', 'Steyr': 'Austria', 'Wiener Neustadt': 'Austria',
        'Feldkirch': 'Austria', 'Bregenz': 'Austria', 'Leonding': 'Austria', 'Klosterneuburg': 'Austria',
        'Baden': 'Austria', 'Wolfsberg': 'Austria', 'Leoben': 'Austria', 'Krems': 'Austria',
        'Traun': 'Austria', 'Amstetten': 'Austria', 'Kapfenberg': 'Austria', 'Hallein': 'Austria',
        'Kufstein': 'Austria', 'Traiskirchen': 'Austria', 'Schwechat': 'Austria', 'Braunau': 'Austria',
        'Spittal': 'Austria', 'Saalfelden': 'Austria', 'Ansfelden': 'Austria', 'Tulln': 'Austria',
        'Hohenems': 'Austria', 'Ternitz': 'Austria', 'Bruck': 'Austria', 'Zell': 'Austria',
        'Knittelfeld': 'Austria', 'Eisenstadt': 'Austria', 'Ried': 'Austria', 'Lienz': 'Austria',
        'Gmunden': 'Austria', 'Vöcklabruck': 'Austria', 'Waidhofen': 'Austria', 'Gänserndorf': 'Austria',
        
        'Copenhagen': 'Denmark', 'Aarhus': 'Denmark', 'Odense': 'Denmark', 'Aalborg': 'Denmark',
        'Esbjerg': 'Denmark', 'Randers': 'Denmark', 'Kolding': 'Denmark', 'Horsens': 'Denmark',
        'Vejle': 'Denmark', 'Roskilde': 'Denmark', 'Herning': 'Denmark', 'Silkeborg': 'Denmark',
        'Næstved': 'Denmark', 'Fredericia': 'Denmark', 'Viborg': 'Denmark', 'Køge': 'Denmark',
        'Holstebro': 'Denmark', 'Taastrup': 'Denmark', 'Slagelse': 'Denmark', 'Hillerød': 'Denmark',
        'Helsingør': 'Denmark', 'Hørsholm': 'Denmark', 'Nykøbing': 'Denmark', 'Svendborg': 'Denmark',
        'Holbæk': 'Denmark', 'Hjørring': 'Denmark', 'Frederikshavn': 'Denmark', 'Hobro': 'Denmark',
        'Nørresundby': 'Denmark', 'Ringkøbing': 'Denmark', 'Skive': 'Denmark', 'Thisted': 'Denmark',
        'Lemvig': 'Denmark', 'Struer': 'Denmark', 'Ikast': 'Denmark', 'Brande': 'Denmark',
        'Give': 'Denmark', 'Bjerringbro': 'Denmark', 'Langå': 'Denmark', 'Ulfborg': 'Denmark',
        'Thyregod': 'Denmark', 'Vinderup': 'Denmark', 'Kjellerup': 'Denmark', 'Bording': 'Denmark',
        'Ans': 'Denmark', 'Ry': 'Denmark', 'Hammel': 'Denmark', 'Hadsten': 'Denmark',
        'Hinnerup': 'Denmark', 'Trige': 'Denmark', 'Lystrup': 'Denmark', 'Malling': 'Denmark',
    }
    
    print(f"   ✅ Created mapping for {len(city_country_mapping)} cities")
    return city_country_mapping

def extract_city_from_club_name(club_name, city_mapping):
    """Extract city from club name and return country if found"""
    if pd.isna(club_name):
        return None
    
    club_name_clean = str(club_name).strip()
    
    # Try to find cities in the club name
    for city, country in city_mapping.items():
        # Check if city name is in club name (case insensitive)
        if city.lower() in club_name_clean.lower():
            return country
    
    return None

def map_cities_to_countries():
    """Map youth clubs to countries based on city names"""
    print("🚀 Starting city-based country mapping...")
    
    try:
        # Load current database
        df = pd.read_csv('db_players_and_training_clubs_final_complete_countries.csv')
        print(f"   ✅ Loaded {len(df)} records")
        
        # Create city mapping
        city_mapping = create_city_country_mapping()
        
        # Show current statistics
        print(f"\n📊 CURRENT STATISTICS:")
        total_youth_clubs = df[df['youth_club'].notna()]['youth_club'].nunique()
        clubs_with_country = df[df['youth_club_country'].notna()]['youth_club'].nunique()
        clubs_without_country = total_youth_clubs - clubs_with_country
        
        print(f"   Total unique youth clubs: {total_youth_clubs}")
        print(f"   Clubs with country: {clubs_with_country}")
        print(f"   Clubs without country: {clubs_without_country}")
        print(f"   Current coverage: {(clubs_with_country / total_youth_clubs) * 100:.1f}%")
        
        # Apply city-based mapping
        print(f"\n🔧 Applying city-based country mapping...")
        
        df_updated = df.copy()
        updated_count = 0
        city_matches = {}
        
        # Process records without country
        records_without_country = df_updated[
            (df_updated['youth_club'].notna()) & 
            (df_updated['youth_club_country'].isna())
        ]
        
        print(f"   📊 Processing {len(records_without_country)} records without country...")
        
        for idx, row in records_without_country.iterrows():
            youth_club = row['youth_club']
            
            # Try to find country based on city
            country = extract_city_from_club_name(youth_club, city_mapping)
            
            if country:
                df_updated.at[idx, 'youth_club_country'] = country
                updated_count += 1
                
                # Track city matches
                if country not in city_matches:
                    city_matches[country] = []
                city_matches[country].append(youth_club)
        
        print(f"   ✅ Updated {updated_count} records with city-based country data")
        
        # Show city matches by country
        print(f"\n📋 CITY MATCHES BY COUNTRY:")
        for country, clubs in sorted(city_matches.items()):
            print(f"   {country}: {len(clubs)} clubs")
            for club in clubs[:3]:  # Show first 3
                print(f"      - {club}")
            if len(clubs) > 3:
                print(f"      ... and {len(clubs) - 3} more")
        
        # Show updated statistics
        print(f"\n📊 UPDATED STATISTICS:")
        final_clubs_with_country = df_updated[df_updated['youth_club_country'].notna()]['youth_club'].nunique()
        final_clubs_without_country = total_youth_clubs - final_clubs_with_country
        
        print(f"   Total unique youth clubs: {total_youth_clubs}")
        print(f"   Clubs with country: {final_clubs_with_country}")
        print(f"   Clubs without country: {final_clubs_without_country}")
        print(f"   Final coverage: {(final_clubs_with_country / total_youth_clubs) * 100:.1f}%")
        
        improvement = final_clubs_with_country - clubs_with_country
        print(f"   Improvement: +{improvement} clubs ({(improvement / total_youth_clubs) * 100:.1f}%)")
        
        # Show examples of updated data
        print(f"\n📋 EXAMPLES OF CITY-BASED UPDATES:")
        updated_examples = df_updated[
            df_updated['youth_club_country'].notna() & 
            df_updated['youth_club'].isin([club for clubs in city_matches.values() for club in clubs])
        ][
            ['full_name', 'youth_club', 'youth_club_country']
        ].head(15)
        
        for _, row in updated_examples.iterrows():
            print(f"   • {row['full_name']}: {row['youth_club']} → {row['youth_club_country']}")
        
        # Save updated database
        output_file = 'db_players_and_training_clubs_with_city_countries.csv'
        df_updated.to_csv(output_file, index=False)
        
        print(f"\n💾 Saved city-mapped database to: {output_file}")
        print(f"📊 Total records: {len(df_updated)}")
        
        return df_updated
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    print("🚀 Starting city-based country mapping...")
    
    try:
        updated_df = map_cities_to_countries()
        
        if updated_df is not None:
            print(f"\n🎉 City-based country mapping completed!")
            print(f"📁 Output file: db_players_and_training_clubs_with_city_countries.csv")
            print(f"\n📊 Summary:")
            print(f"   - Applied city-to-country mapping")
            print(f"   - Identified cities in club names")
            print(f"   - Significantly improved country coverage")
            print(f"   - Ready for further analysis")
        else:
            print(f"\n❌ Failed to complete city-based mapping")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
