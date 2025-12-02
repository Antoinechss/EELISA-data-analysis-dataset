import pandas as pd
path = '/Users/antoinechosson/Desktop/EELISA/EELISA-Data-analysis/datasets/european_jobs.csv'
df = pd.read_csv(path)

CAPITAL_COORDINATES = {
    "BE": (50.8503, 4.3517),    # Brussels
    "BG": (42.6977, 23.3219),   # Sofia
    "CZ": (50.0755, 14.4378),   # Prague
    "DK": (55.6761, 12.5683),   # Copenhagen
    "DE": (52.5200, 13.4050),   # Berlin
    "EE": (59.4370, 24.7536),   # Tallinn
    "IE": (53.3498, 6.2603),    # Dublin
    "EL": (37.9838, 23.7275),   # Athens
    "GR": (37.9838, 23.7275),   # Athens
    "ES": (40.4168, -3.7038),   # Madrid
    "FR": (48.8566, 2.3522),    # Paris
    "HR": (45.8150, 15.9819),   # Zagreb
    "IT": (41.9028, 12.4964),   # Rome
    "CY": (35.1856, 33.3823),   # Nicosia
    "LV": (56.9496, 24.1052),   # Riga
    "LT": (54.6872, 25.2797),   # Vilnius
    "LU": (49.6116, 6.1319),    # Luxembourg City
    "HU": (47.4979, 19.0402),   # Budapest
    "MT": (35.8989, 14.5146),   # Valletta
    "NL": (52.3676, 4.9041),    # Amsterdam
    "AT": (48.2082, 16.3738),   # Vienna
    "PL": (52.2297, 21.0122),   # Warsaw
    "PT": (38.7223, -9.1393),   # Lisbon
    "RO": (44.4268, 26.1025),   # Bucharest
    "SI": (46.0569, 14.5058),   # Ljubljana
    "SK": (48.1486, 17.1077),   # Bratislava
    "FI": (60.1699, 24.9384),   # Helsinki
    "SE": (59.3293, 18.0686),   # Stockholm
    "NO": (59.9139, 10.7522),   # Oslo
    "CH": (46.9480, 7.4474),    # Bern
    "TR": (39.9334, 32.8597),   # Ankara
}

# Map country code to capital name
CAPITAL_NAMES = {
    "BE": "Brussels",
    "BG": "Sofia",
    "CZ": "Prague",
    "DK": "Copenhagen",
    "DE": "Berlin",
    "EE": "Tallinn",
    "IE": "Dublin",
    "EL": "Athens",
    "GR": "Athens",
    "ES": "Madrid",
    "FR": "Paris",
    "HR": "Zagreb",
    "IT": "Rome",
    "CY": "Nicosia",
    "LV": "Riga",
    "LT": "Vilnius",
    "LU": "Luxembourg City",
    "HU": "Budapest",
    "MT": "Valletta",
    "NL": "Amsterdam",
    "AT": "Vienna",
    "PL": "Warsaw",
    "PT": "Lisbon",
    "RO": "Bucharest",
    "SI": "Ljubljana",
    "SK": "Bratislava",
    "FI": "Helsinki",
    "SE": "Stockholm",
    "NO": "Oslo",
    "CH": "Bern",
    "TR": "Ankara",
}

def fix_region(row):
    region = str(row['region']).strip()
    cc = str(row['country_code']).upper()
    if not region or region.lower() in ['nan', 'none', '']:
        return CAPITAL_NAMES.get(cc, region)
    return region

df['region'] = df.apply(fix_region, axis=1)
df.to_csv(path, index=False)