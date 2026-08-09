import pandas as pd
import numpy as np

df = pd.read_csv('data/processed/cantons_official.csv')
print('=== COORDENADAS POR CANTON (primeros 30) ===')
print(df[['canton','provincia','latitud','longitud','homicidios_2025','homicide_rate_2025']].head(30).to_string())
print()

print('=== CANTONES CON COORDENADAS SOSPECHOSAS ===')
# Ecuador: lat approx -5 to +1, lon approx -81 to -75
suspicious = df[(df['latitud'].abs() > 5) | (df['longitud'] > -75) | (df['longitud'] < -81) | (df['latitud'] == 0) | (df['longitud'] == 0)]
print(f'Total sospechosos: {len(suspicious)}')
if len(suspicious) > 0:
    print(suspicious[['canton','provincia','latitud','longitud']].to_string())
print()

print('=== ESTADISTICAS ===')
print(f'Lat range: {df["latitud"].min():.4f} to {df["latitud"].max():.4f}')
print(f'Lon range: {df["longitud"].min():.4f} to {df["longitud"].max():.4f}')
print(f'Lat=0: {(df["latitud"]==0).sum()}, Lon=0: {(df["longitud"]==0).sum()}')
print(f'NaN lat: {df["latitud"].isna().sum()}, NaN lon: {df["longitud"].isna().sum()}')
print()

# Check for swapped lat/lon
print('=== POSIBLE LAT/LON INTERCAMBIADOS ===')
# If lat > -10 and lon < 0 but lat looks like longitude and vice versa
swapped = df[(df['latitud'] < -75) | (df['longitud'] > -10)]
print(f'Posibles intercambiados: {len(swapped)}')
if len(swapped) > 0:
    print(swapped[['canton','provincia','latitud','longitud']].to_string())
print()

# Check for duplicate coordinates
print('=== COORDENADAS DUPLICADAS ===')
dup = df[df.duplicated(subset=['latitud','longitud'], keep=False)]
if len(dup) > 0:
    print(f'{len(dup)} cantones con coordenadas duplicadas:')
    print(dup[['canton','provincia','latitud','longitud']].to_string())
else:
    print('No hay duplicados')
print()

# Check unique cantons vs count
print(f'Total cantones: {len(df)}')
print(f'Cantones unicos: {df["canton"].nunique()}')
print()

# Look at the raw data to understand the coordinate issue
print('=== COORDENADAS POR PROVINCIA (promedio) ===')
prov_coords = df.groupby('provincia')[['latitud','longitud']].mean()
print(prov_coords.to_string())
