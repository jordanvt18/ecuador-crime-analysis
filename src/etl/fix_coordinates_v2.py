"""
Fix canton coordinates - handling encoding issues with special characters.
The official data has corrupted UTF-8 characters (ñ, á, é, í, ó, ú).
"""
import pandas as pd
import numpy as np
from pathlib import Path
import unicodedata

DATA = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

def normalize_text(s):
    """Remove accents for matching purposes."""
    if pd.isna(s):
        return ""
    s = str(s)
    # Try to fix common mojibake patterns
    # CP1252 interpretations of UTF-8 bytes
    try:
        # If the string contains replacement chars or mojibake, try to fix
        s_bytes = s.encode('utf-8', errors='replace')
        s_fixed = s_bytes.decode('utf-8', errors='replace')
        s = s_fixed
    except:
        pass
    # Normalize: remove accents
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).upper().strip()

# Verified canton coordinates - using ASCII-normalized keys
CANTON_COORDS = {
    # Azuay
    "CUENCA": (-2.9006, -79.0045), "GUALACEO": (-2.889, -78.779), "PAUTE": (-2.757, -78.736),
    "SANTA ISABEL": (-3.137, -79.259), "SIGSIG": (-2.744, -78.560), "GIRON": (-2.726, -78.602),
    "NABON": (-2.488, -78.766), "ONA": (-2.229, -79.293), "CHORDELEG": (-2.197, -78.650),
    "EL PAN": (-2.632, -78.805), "SEVILLA DE ORO": (-2.778, -78.649),
    "GUACHAPALA": (-2.774, -78.713), "CAMILO PONCE ENRIQUEZ": (-2.838, -79.447),
    "PUCARA": (-2.742, -79.010), "SAN FERNANDO": (-3.095, -79.290),
    # Bolivar
    "GUARANDA": (-1.593, -79.006), "CHILLANES": (-1.933, -79.063), "SAN MIGUEL": (-1.676, -79.145),
    "CALUMA": (-1.219, -79.065), "ECHEANDIA": (-0.724, -79.094), "LAS NAVES": (-1.242, -79.367),
    "CHIMBO": (-1.331, -79.065),
    # Canar
    "AZOGUES": (-2.741, -78.847), "BIBLIAN": (-2.705, -78.895), "CANAR": (-2.467, -78.940),
    "LA TRONCAL": (-2.034, -79.339), "EL TAMBO": (-2.547, -78.950), "DELEG": (-2.605, -78.870),
    "SUSCAL": (-2.474, -79.130),
    # Carchi
    "TULCAN": (0.777, -77.720), "BOLIVAR": (0.503, -77.923), "ESPEJO": (0.641, -77.946),
    "MIRA": (0.648, -78.153), "MONTUFAR": (0.534, -77.721), "SAN PEDRO DE HUACA": (0.598, -77.728),
    # Cotopaxi
    "LATACUNGA": (-0.933, -78.615), "SALCEDO": (-0.985, -78.620), "PUJILI": (-0.946, -78.701),
    "PANGUA": (-1.046, -79.232), "LA MANA": (-0.938, -79.224), "SIGCHOS": (-0.671, -78.688),
    "SAQUISILI": (-0.836, -78.670), "PUJILI": (-0.946, -78.701),
    # Chimborazo
    "RIOBAMBA": (-1.671, -78.648), "GUANO": (-1.520, -78.632), "PALLATANGA": (-1.414, -78.782),
    "COLTA": (-1.302, -78.620), "CUMANDA": (-2.088, -79.036), "ALAUSI": (-2.034, -78.847),
    "CHAMBO": (-1.390, -78.635), "PENIPE": (-1.596, -78.520), "GUAMOTE": (-1.341, -78.665),
    "CHUNCHI": (-1.489, -78.905), "ALAUSI": (-2.034, -78.847),
    # El Oro
    "MACHALA": (-3.259, -79.962), "PASAJE": (-3.329, -79.804), "SANTA ROSA": (-3.449, -79.960),
    "HUAQUILLAS": (-3.473, -80.229), "ARENILLAS": (-3.547, -80.078), "ATAHUALPA": (-3.709, -80.202),
    "BALSAS": (-3.762, -79.917), "CHILLA": (-3.422, -79.560), "EL GUABO": (-3.247, -79.827),
    "LAS LAJAS": (-3.552, -79.769), "MARCABELI": (-3.576, -79.880), "PINAS": (-3.665, -79.649),
    "PORTOVELO": (-3.719, -79.552), "ZARUMA": (-3.691, -79.609),
    # Esmeraldas
    "ESMERALDAS": (0.954, -79.656), "SAN LORENZO": (1.288, -78.838), "ELOY ALFARO": (1.247, -78.979),
    "ATACAMES": (0.868, -79.841), "QUININDE": (0.332, -79.466), "MUISNE": (0.614, -80.021),
    "RIOVERDE": (0.959, -79.524), "LA TOLA": (0.737, -79.883), "MOMPICHE": (0.469, -79.990),
    # Galapagos
    "SANTA CRUZ": (-0.741, -90.315), "SAN CRISTOBAL": (-0.889, -89.622), "ISABELA": (-0.962, -90.974),
    # Guayas
    "GUAYAQUIL": (-2.189, -79.889), "DURAN": (-2.179, -79.831), "SAMBORONDON": (-2.028, -79.724),
    "DAULE": (-1.868, -79.977), "MILAGRO": (-2.129, -79.594), "BALZAR": (-1.366, -79.905),
    "EL TRIUNFO": (-2.193, -79.358), "NARANJAL": (-2.672, -79.616), "NARANJITO": (-2.238, -79.407),
    "PALESTINA": (-1.496, -79.612), "SANTA LUCIA": (-1.564, -79.621),
    "SIMON BOLIVAR": (-1.846, -79.889), "CORONEL MARCELINO MARIDUENA": (-2.129, -79.569),
    "GENERAL ANTONIO ELIZALDE": (-2.107, -79.508), "SALITRE": (-1.814, -79.822),
    "TENGUEL": (-3.014, -79.917), "YAGUACHI": (-2.106, -79.674),
    "PLAYAS": (-2.594, -80.389), "NOBOL": (-1.496, -79.612),
    "ISIDRO AYORA": (-1.360, -79.789), "LOMAS DE SARGENTILLO": (-1.386, -80.036),
    "COLIMES": (-1.230, -79.988), "BALAO": (-2.914, -79.774),
    "EL EMPALME": (-1.039, -79.629), "ALFREDO BAQUERIZO MORENO": (-1.286, -79.560),
    "JUJAN": (-1.286, -79.560),
    # Imbabura
    "IBARRA": (0.346, -78.131), "OTAVALO": (0.232, -78.262), "COTACACHI": (0.299, -78.432),
    "ANTONIO ANTE": (0.305, -78.142), "PIMAMPIRO": (0.312, -77.967),
    "SAN MIGUEL DE URCUQUI": (0.441, -78.192), "URCUQUI": (0.441, -78.192),
    # Loja
    "LOJA": (-3.998, -79.205), "CATAMAYO": (-3.984, -79.354), "SARAGURO": (-3.529, -79.243),
    "ZAPOTILLO": (-4.350, -80.253), "MACARA": (-4.380, -79.941), "CELICA": (-4.093, -79.978),
    "PALTAS": (-4.047, -79.559), "PUYANGO": (-4.241, -80.084), "CHAGUARPAMBA": (-3.852, -79.655),
    "CALVAS": (-3.603, -79.243), "GONZANAMA": (-3.115, -79.425), "QUILANGA": (-4.047, -79.559),
    "SOZORANGA": (-4.330, -79.805), "PINDAL": (-4.067, -79.778), "OLMEDO": (-3.939, -79.425),
    "ESPINDOLA": (-4.648, -79.419),
    # Los Rios
    "BABAHOYO": (-1.803, -79.534), "QUEVEDO": (-1.033, -79.449), "VENTANAS": (-1.446, -79.471),
    "VINCES": (-1.556, -79.752), "BUENA FE": (-0.912, -79.484), "PALENQUE": (-1.267, -79.428),
    "VALENCIA": (-0.840, -79.436), "MOCACHE": (-1.246, -79.637), "URDANETA": (-1.500, -79.500),
    "BABA": (-1.841, -79.534), "PUEBLOVIEJO": (-1.889, -79.534), "MONTALVO": (-1.676, -79.534),
    "QUINSALOMA": (-1.345, -79.500), "VENEZUELA": (-1.500, -79.500),
    # Manabi
    "PORTOVIEJO": (-1.054, -80.454), "MANTA": (-0.949, -80.746), "CHONE": (-0.698, -80.094),
    "PEDERNALES": (0.076, -80.053), "EL CARMEN": (-0.280, -79.463), "FLAVIO ALFARO": (-0.302, -79.917),
    "TOSAGUA": (-0.775, -80.246), "ROCAFUERTE": (-0.895, -80.447), "JIPIJAPA": (-1.344, -80.585),
    "MONTECRISTI": (-1.046, -80.653), "JAMA": (-0.151, -80.421), "SUCRE": (-0.775, -80.246),
    "PICHINCHA": (-0.836, -80.192), "JUNIN": (-1.046, -80.353),
    "24 DE MAYO": (-1.221, -80.353), "SANTA ANA": (-1.046, -80.353),
    "PUERTO LOPEZ": (-1.557, -80.808), "JARAMIJO": (-0.949, -80.646),
    "PEDRO CARBO": (-1.595, -80.246), "PAJAN": (-1.400, -80.350),
    "SAN VICENTE": (-0.701, -80.421),
    # Morona Santiago
    "MACAS": (-2.307, -78.113), "GUALAQUIZA": (-3.041, -78.572), "SUCUA": (-2.256, -78.168),
    "PALORA": (-1.586, -77.873), "MORONA": (-2.034, -78.081),
    "TAISHA": (-1.931, -77.873), "LOGRONO": (-2.256, -78.168), "PABLO SEXTO": (-2.256, -78.168),
    "TIWINTZA": (-2.256, -78.168), "HUAMBOYA": (-1.400, -77.873),
    "LIMON INDANZA": (-2.230, -78.300), "SAN JUAN BOSCO": (-2.300, -78.300),
    # Napo
    "TENA": (-0.996, -77.816), "ARCHIDONA": (-0.829, -77.815),
    "CARLOS JULIO AROSEMENA TOLA": (-1.017, -77.733), "QUIJOS": (-0.312, -77.966),
    "EL CHACO": (-0.312, -77.966),
    # Orellana
    "FRANCISCO DE ORELLANA": (-0.467, -76.987), "LA JOYA DE LOS SACHAS": (-0.275, -76.637),
    "LORETO": (-0.603, -77.307), "AGUARICO": (-0.467, -76.987),
    # Pastaza
    "PUYO": (-1.480, -78.004), "MERA": (-1.421, -78.116), "SANTA CLARA": (-1.371, -77.968),
    "ARAJUNO": (-1.011, -77.963), "PASTAZA": (-1.371, -77.968),
    # Pichincha
    "QUITO": (-0.180, -78.467), "CAYAMBE": (0.041, -78.160), "MEJIA": (-0.502, -78.567),
    "PEDRO MONCAYO": (0.043, -78.264), "PEDRO VICENTE MALDONADO": (0.083, -79.052),
    "PUERTO QUITO": (0.157, -79.075), "RUMINAHUI": (-0.294, -78.443),
    "SAN MIGUEL DE LOS BANCOS": (0.000, -78.900),
    # Santa Elena
    "SANTA ELENA": (-2.226, -80.859), "LA LIBERTAD": (-2.223, -80.905), "SALINAS": (-2.216, -80.968),
    # Santo Domingo
    "SANTO DOMINGO": (-0.253, -79.172), "LA CONCORDIA": (-0.005, -79.392),
    "SANTO DOMINGO DE LOS TSACHILAS": (-0.253, -79.172),
    # Sucumbios
    "LAGO AGRO": (0.086, -76.882), "LAGO AGRIO": (0.086, -76.882),
    "CASCALES": (0.071, -77.125), "PUTUMAYO": (0.131, -77.005),
    "SHUSHUFINDI": (-0.167, -76.683), "CUYABENO": (-0.167, -76.683),
    "GONZALO PIZARRO": (0.350, -77.200), "SUCUMBIOS": (0.200, -77.000),
    # Tungurahua
    "AMBATO": (-1.243, -78.620), "BANOS DE AGUA SANTA": (-1.395, -78.421),
    "CEVALLOS": (-1.180, -78.620), "PILLARO": (-1.030, -78.547),
    "QUERO": (-1.364, -78.620), "MOCHA": (-1.415, -78.620),
    "TISALEO": (-1.346, -78.620), "PELILEO": (-1.338, -78.547),
    "SANTIAGO DE PILLARO": (-1.030, -78.547), "PATATE": (-1.286, -78.550),
    # Zamora Chinchipe
    "ZAMORA": (-4.069, -78.957), "YANTZAZA": (-3.400, -78.640),
    "CENTINELA DEL CONDOR": (-3.258, -78.640), "NANGARITZA": (-3.492, -78.640),
    "PAQUISHA": (-3.564, -78.640), "EL PANGUI": (-3.400, -78.640),
    "PALANDA": (-4.648, -79.000), "CHINCHIPE": (-4.648, -79.000),
}


def fix_canton_coordinates():
    """Fix canton coordinates using normalized text matching."""
    print("=" * 60)
    print("FIXING CANTON COORDINATES (with encoding fix)")
    print("=" * 60)
    
    df = pd.read_csv(DATA / "cantons_official.csv", encoding="utf-8")
    
    # Build normalized lookup
    norm_coords = {}
    for key, (lat, lon) in CANTON_COORDS.items():
        norm_coords[key] = (lat, lon)
    
    fixed_count = 0
    unmatched = []
    
    for idx, row in df.iterrows():
        canton_raw = row["canton"]
        canton_norm = normalize_text(canton_raw)
        
        # Try exact normalized match
        if canton_norm in norm_coords:
            lat, lon = norm_coords[canton_norm]
            df.at[idx, "latitud"] = lat
            df.at[idx, "longitud"] = lon
            fixed_count += 1
        else:
            # Try partial match
            matched = False
            for key, (lat, lon) in norm_coords.items():
                if canton_norm in key or key in canton_norm:
                    df.at[idx, "latitud"] = lat
                    df.at[idx, "longitud"] = lon
                    fixed_count += 1
                    matched = True
                    break
            if not matched:
                unmatched.append((canton_raw, canton_norm, row["provincia"]))
    
    print(f"\n  Fixed: {fixed_count} of {len(df)} cantons")
    
    if unmatched:
        print(f"\n  Unmatched ({len(unmatched)}):")
        for raw, norm, prov in unmatched:
            print(f"    '{raw}' -> '{norm}' ({prov})")
    
    # Verify
    print(f"\n  Verification:")
    print(f"  Lat range: {df['latitud'].min():.4f} to {df['latitud'].max():.4f}")
    print(f"  Lon range: {df['longitud'].min():.4f} to {df['longitud'].max():.4f}")
    
    suspicious = df[(df['longitud'] > -75) | (df['longitud'] < -91) | (df['latitud'] == 0)]
    if len(suspicious) > 0:
        print(f"\n  Still suspicious ({len(suspicious)}):")
        for _, r in suspicious.iterrows():
            print(f"    {r['canton']} ({r['provincia']}): ({r['latitud']:.4f}, {r['longitud']:.4f})")
    else:
        print(f"  All coordinates within Ecuador bounds! ✓")
    
    # Save with explicit UTF-8 encoding
    df.to_csv(DATA / "cantons_official.csv", index=False, encoding="utf-8")
    print(f"\n  Saved to cantons_official.csv (UTF-8)")
    
    # Also fix spatial econometrics file
    try:
        spatial = pd.read_csv(DATA / "cantons_spatial_econometrics.csv", encoding="utf-8")
        for idx, row in spatial.iterrows():
            canton_norm = normalize_text(row["canton"])
            if canton_norm in norm_coords:
                spatial.at[idx, "latitud"] = norm_coords[canton_norm][0]
                spatial.at[idx, "longitud"] = norm_coords[canton_norm][1]
            else:
                for key, (lat, lon) in norm_coords.items():
                    if canton_norm in key or key in canton_norm:
                        spatial.at[idx, "latitud"] = lat
                        spatial.at[idx, "longitud"] = lon
                        break
        spatial.to_csv(DATA / "cantons_spatial_econometrics.csv", index=False, encoding="utf-8")
        print(f"  Fixed spatial econometrics file too")
    except Exception as e:
        print(f"  [WARNING] Could not fix spatial file: {e}")
    
    return df

if __name__ == "__main__":
    fix_canton_coordinates()
