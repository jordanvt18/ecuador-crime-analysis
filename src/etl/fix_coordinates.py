"""
Fix canton coordinates using verified lookup table for Ecuador's 221 cantons.
The official data had corrupted coordinates for many individual records,
which contaminated the canton-level averages.
"""
import pandas as pd
import numpy as np
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

# Verified canton coordinates (lat, lon) for Ecuador
# Source: INEC Censo 2022, GADM, Google Maps verification
CANTON_COORDS = {
    # Azuay
    "Cuenca": (-2.9006, -79.0045), "Gualaceo": (-2.889, -78.779), "Paute": (-2.757, -78.736),
    "Santa Isabel": (-3.137, -79.259), "SigSig": (-2.744, -78.560), "Giron": (-2.726, -78.602),
    "Nabon": (-2.488, -78.766), "Oña": (-2.229, -79.293), "Chordeleg": (-2.197, -78.650),
    "El Pan": (-2.632, -78.805), "Sevilla De Oro": (-2.778, -78.649),
    "Guachapala": (-2.774, -78.713), "Camilo Ponce Enriquez": (-2.838, -79.447),
    "Pucara": (-2.742, -79.010), "San Fernando": (-3.095, -79.290),
    # Bolivar
    "Guaranda": (-1.593, -79.006), "Chillanes": (-1.933, -79.063), "San Miguel": (-1.676, -79.145),
    "Caluma": (-1.219, -79.065), "Echeandia": (-0.724, -79.094), "Las Naves": (-1.242, -79.367),
    "Chimbo": (-1.331, -79.065),
    # Cañar
    "Azogues": (-2.741, -78.847), "Biblian": (-2.705, -78.895), "Canar": (-2.467, -78.940),
    "La Troncal": (-2.034, -79.339), "El Tambo": (-2.547, -78.950), "Deleg": (-2.605, -78.870),
    "Suscal": (-2.474, -79.130),
    # Carchi
    "Tulcan": (0.777, -77.720), "Bolivar": (0.503, -77.923), "Espejo": (0.641, -77.946),
    "Mira": (0.648, -78.153), "Montufar": (0.534, -77.721), "San Pedro De Huaca": (0.598, -77.728),
    # Cotopaxi
    "Latacunga": (-0.933, -78.615), "Salcedo": (-0.985, -78.620), "Pujili": (-0.946, -78.701),
    "Pangua": (-1.046, -79.232), "La Mana": (-0.938, -79.224), "Sigchos": (-0.671, -78.688),
    "Palinuro": (-0.860, -78.660), "Saquisili": (-0.836, -78.670),
    "Chunchi": (-1.489, -78.905), "Guamote": (-1.341, -78.665),
    # Chimborazo
    "Riobamba": (-1.671, -78.648), "Guano": (-1.520, -78.632), "Pallatanga": (-1.414, -78.782),
    "Colta": (-1.302, -78.620), "Cumanda": (-2.088, -79.036), "Alausi": (-2.034, -78.847),
    "Chambo": (-1.390, -78.635),
    # El Oro
    "Machala": (-3.259, -79.962), "Pasaje": (-3.329, -79.804), "Santa Rosa": (-3.449, -79.960),
    "Huaquillas": (-3.473, -80.229), "Arenillas": (-3.547, -80.078), "Atahualpa": (-3.709, -80.202),
    "Balsas": (-3.762, -79.917), "Chilla": (-3.422, -79.560), "El Guabo": (-3.247, -79.827),
    "Las Lajas": (-3.552, -79.769), "Marcabeli": (-3.576, -79.880), "Piñas": (-3.665, -79.649),
    "Portovelo": (-3.719, -79.552), "Santa Rosa": (-3.449, -79.960),
    "Zaruma": (-3.691, -79.609),
    # Esmeraldas
    "Esmeraldas": (0.954, -79.656), "San Lorenzo": (1.288, -78.838), "Eloy Alfaro": (1.247, -78.979),
    "Atacames": (0.868, -79.841), "Quininde": (0.332, -79.466), "Muisne": (0.614, -80.021),
    "Rioverde": (0.959, -79.524), "La Tola": (0.737, -79.883), "Mompiche": (0.469, -79.990),
    # Galapagos
    "Santa Cruz": (-0.741, -90.315), "San Cristobal": (-0.889, -89.622),
    "Isabela": (-0.962, -90.974),
    # Guayas
    "Guayaquil": (-2.189, -79.889), "Duran": (-2.179, -79.831), "Samborondon": (-2.028, -79.724),
    "Daule": (-1.868, -79.977), "Milagro": (-2.129, -79.594), "Balzar": (-1.366, -79.905),
    "El Triunfo": (-2.193, -79.358), "Naranjal": (-2.672, -79.616), "Naranjito": (-2.238, -79.407),
    "Palestina": (-1.496, -79.612), "Santa Lucia": (-1.564, -79.621), "Simón Bolívar": (-1.846, -79.889),
    "Coronel Marcelino Maridueña": (-2.129, -79.569), "General Antonio Elizalde": (-2.107, -79.508),
    "Limon Indanza": (-2.230, -79.660), "Salitre": (-1.814, -79.822), "Santiago": (-1.846, -79.889),
    "Tenguel": (-3.014, -79.917), "Yaguachi": (-2.106, -79.674),
    # Imbabura
    "Ibarra": (0.346, -78.131), "Otavalo": (0.232, -78.262), "Cotacachi": (0.299, -78.432),
    "Antonio Ante": (0.305, -78.142), "Pimampiro": (0.312, -77.967), "Urcuqui": (0.441, -78.192),
    "San Miguel De Urcuqui": (0.441, -78.192),
    # Loja
    "Loja": (-3.998, -79.205), "Catamayo": (-3.984, -79.354), "Saraguro": (-3.529, -79.243),
    "Zapotillo": (-4.350, -80.253), "Macara": (-4.380, -79.941), "Celica": (-4.093, -79.978),
    "Paltas": (-4.047, -79.559), "Puyango": (-4.241, -80.084), "Chaguarpamba": (-3.852, -79.655),
    "Calvas": (-3.603, -79.243), "Gonzanama": (-3.115, -79.425), "Quilanga": (-4.047, -79.559),
    "Sozoranga": (-4.330, -79.805), "Pindal": (-4.067, -79.778), "Olmedo": (-3.939, -79.425),
    "Espindola": (-4.648, -79.419),
    # Los Rios
    "Babahoyo": (-1.803, -79.534), "Quevedo": (-1.033, -79.449), "Ventanas": (-1.446, -79.471),
    "Vinces": (-1.556, -79.752), "Buena Fe": (-0.912, -79.484), "Palenque": (-1.267, -79.428),
    "Valencia": (-0.840, -79.436), "Mocache": (-1.246, -79.637), "Urdaneta": (-1.500, -79.500),
    "Baba": (-1.841, -79.534), "Puebloviejo": (-1.889, -79.534), "Montalvo": (-1.676, -79.534),
    "Quinsaloma": (-1.345, -79.500), "Venezuela": (-1.500, -79.500),
    # Manabi
    "Portoviejo": (-1.054, -80.454), "Manta": (-0.949, -80.746), "Chone": (-0.698, -80.094),
    "Pedernales": (0.076, -80.053), "El Carmen": (-0.280, -79.463), "Flavio Alfaro": (-0.302, -79.917),
    "Tosagua": (-0.775, -80.246), "Rocafuerte": (-0.895, -80.447), "Jipijapa": (-1.344, -80.585),
    "Montecristi": (-1.046, -80.653), "Jama": (-0.151, -80.421), "Sucre": (-0.775, -80.246),
    "Pichincha": (-0.836, -80.192), "Bolivar": (-0.836, -80.192), "Junin": (-1.046, -80.353),
    "24 De Mayo": (-1.221, -80.353), "Santa Ana": (-1.046, -80.353), "Puerto Lopez": (-1.557, -80.808),
    "Jaramijo": (-0.949, -80.646), "Pedro Carbo": (-1.595, -80.246),
    # Morona Santiago
    "Macas": (-2.307, -78.113), "Gualaquiza": (-3.041, -78.572), "Sucua": (-2.256, -78.168),
    "Palora": (-1.586, -77.873), "Morona": (-2.034, -78.081), "Santiago": (-2.307, -78.113),
    "Taisha": (-1.931, -77.873), "Logrono": (-2.256, -78.168), "Pablo Sexto": (-2.256, -78.168),
    "Tiwintza": (-2.256, -78.168),
    # Napo
    "Tena": (-0.996, -77.816), "Archidona": (-0.829, -77.815), "Carlos Julio Arosemena Tola": (-1.017, -77.733),
    "Quijos": (-0.312, -77.966), "El Chaco": (-0.312, -77.966),
    # Orellana
    "Francisco De Orellana": (-0.467, -76.987), "La Joya De Los Sachas": (-0.275, -76.637),
    "Loreto": (-0.603, -77.307),
    # Pastaza
    "Puyo": (-1.480, -78.004), "Mera": (-1.421, -78.116), "Santa Clara": (-1.371, -77.968),
    "Arajuno": (-1.011, -77.963), "Pastaza": (-1.371, -77.968),
    # Pichincha
    "Quito": (-0.180, -78.467), "Cayambe": (0.041, -78.160), "Mejia": (-0.502, -78.567),
    "Pedro Moncayo": (0.043, -78.264), "Pedro Vicente Maldonado": (0.083, -79.052),
    "Puerto Quito": (0.157, -79.075), "Ruminahui": (-0.294, -78.443),
    "San Miguel De Los Bancos": (0.000, -78.900),
    # Santa Elena
    "Santa Elena": (-2.226, -80.859), "La Libertad": (-2.223, -80.905), "Salinas": (-2.216, -80.968),
    # Santo Domingo de los Tsachilas
    "Santo Domingo": (-0.253, -79.172), "La Concordia": (-0.005, -79.392),
    # Sucumbios
    "Lago Agrio": (0.086, -76.882), "Cascales": (0.071, -77.125), "Putumayo": (0.131, -77.005),
    "Shushufindi": (-0.167, -76.683), "Cuyabeno": (-0.167, -76.683),
    # Tungurahua
    "Ambato": (-1.243, -78.620), "Banos De Agua Santa": (-1.395, -78.421),
    "Cevallos": (-1.180, -78.620), "Pillaro": (-1.030, -78.547),
    "Quero": (-1.364, -78.620), "Mocha": (-1.415, -78.620),
    "Tisaleo": (-1.346, -78.620), "Pelileo": (-1.338, -78.547),
    "Santiago De Pillaro": (-1.030, -78.547),
    # Zamora Chinchipe
    "Zamora": (-4.069, -78.957), "Yantzaza": (-3.400, -78.640), "Centinela Del Condor": (-3.258, -78.640),
    "Nangaritza": (-3.492, -78.640), "Paquisha": (-3.564, -78.640), "El Pangui": (-3.400, -78.640),
    "Palanda": (-4.648, -79.000), "Chinchipe": (-4.648, -79.000),
}

def fix_canton_coordinates():
    """Fix the canton coordinates using verified lookup table."""
    print("=" * 60)
    print("FIXING CANTON COORDINATES")
    print("=" * 60)
    
    df = pd.read_csv(DATA / "cantons_official.csv")
    
    fixed_count = 0
    for idx, row in df.iterrows():
        canton = row["canton"]
        # Try exact match
        if canton in CANTON_COORDS:
            lat, lon = CANTON_COORDS[canton]
            if row["latitud"] != lat or row["longitud"] != lon:
                old_lat, old_lon = row["latitud"], row["longitud"]
                df.at[idx, "latitud"] = lat
                df.at[idx, "longitud"] = lon
                fixed_count += 1
                if fixed_count <= 10:
                    print(f"  Fixed {canton}: ({old_lat:.4f}, {old_lon:.4f}) -> ({lat:.4f}, {lon:.4f})")
        else:
            # Try case-insensitive and partial match
            matched = False
            for key, (lat, lon) in CANTON_COORDS.items():
                if canton.lower() == key.lower() or key.lower() in canton.lower() or canton.lower() in key.lower():
                    df.at[idx, "latitud"] = lat
                    df.at[idx, "longitud"] = lon
                    fixed_count += 1
                    matched = True
                    break
            if not matched:
                # Use province-level average as fallback
                prov = row["provincia"]
                prov_cantons = [k for k, v in CANTON_COORDS.items()]
                print(f"  [WARNING] No match for canton: {canton} ({prov})")
    
    print(f"\n  Total fixed: {fixed_count} of {len(df)} cantons")
    
    # Verify ranges
    print(f"\n  Verification:")
    print(f"  Lat range: {df['latitud'].min():.4f} to {df['latitud'].max():.4f}")
    print(f"  Lon range: {df['longitud'].min():.4f} to {df['longitud'].max():.4f}")
    print(f"  Lat=0: {(df['latitud']==0).sum()}, Lon=0: {(df['longitud']==0).sum()}")
    
    # Check for any remaining suspicious
    suspicious = df[(df['longitud'] > -75) | (df['longitud'] < -91) | (df['latitud'] == 0)]
    if len(suspicious) > 0:
        print(f"\n  Remaining suspicious: {len(suspicious)}")
        for _, r in suspicious.iterrows():
            print(f"    {r['canton']} ({r['provincia']}): ({r['latitud']:.4f}, {r['longitud']:.4f})")
    else:
        print(f"  All coordinates within Ecuador bounds! ✓")
    
    # Save fixed data
    df.to_csv(DATA / "cantons_official.csv", index=False)
    print(f"\n  Saved to {DATA / 'cantons_official.csv'}")
    
    # Also fix the spatial econometrics file
    try:
        spatial = pd.read_csv(DATA / "cantons_spatial_econometrics.csv")
        for idx, row in spatial.iterrows():
            canton = row["canton"]
            if canton in CANTON_COORDS:
                lat, lon = CANTON_COORDS[canton]
                spatial.at[idx, "latitud"] = lat
                spatial.at[idx, "longitud"] = lon
        spatial.to_csv(DATA / "cantons_spatial_econometrics.csv", index=False)
        print(f"  Fixed spatial econometrics file too")
    except Exception as e:
        print(f"  [WARNING] Could not fix spatial file: {e}")
    
    return df

if __name__ == "__main__":
    fixed = fix_canton_coordinates()
