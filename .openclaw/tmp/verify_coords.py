import pandas as pd
df = pd.read_csv('data/processed/cantons_official.csv', encoding='utf-8')
print('=== VERIFICACION DE COORDENADAS CORREGIDAS ===')
print()
for c in ['Guayaquil','Quito','Cuenca','Manta','Esmeraldas','Machala','Loja','Ambato','Riobamba','Santo Domingo']:
    row = df[df['canton'].str.contains(c, case=False, na=False)]
    if len(row) > 0:
        r = row.iloc[0]
        name = str(r['canton'])[:25]
        prov = str(r['provincia'])[:20]
        lat = float(r['latitud'])
        lon = float(r['longitud'])
        hom = int(r['homicidios_2025'])
        print(f'{name:25s} ({prov:20s}) lat={lat:8.4f} lon={lon:9.4f}  hom2025={hom:5d}')
print()
print(f'Total cantones: {len(df)}')
print(f'Lat range: {df["latitud"].min():.4f} to {df["latitud"].max():.4f}')
print(f'Lon range: {df["longitud"].min():.4f} to {df["longitud"].max():.4f}')
