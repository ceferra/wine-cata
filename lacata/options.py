"""Default answer options for a tasting: grapes, D.O.s (with region), agings and wine types."""

DEFAULT_GRAPES = [
    "Tempranillo", "Garnacha", "Monastrell", "Bobal", "Mencía",
    "Cabernet Sauvignon", "Merlot", "Syrah", "Pinot Noir",
    "Verdejo", "Albariño", "Godello", "Viura", "Macabeo",
    "Chardonnay", "Sauvignon Blanc", "Riesling", "Moscatel",
    "Palomino Fino", "Pedro Ximénez", "Cariñena", "Graciano",
    "Garnacha Blanca", "Xarel·lo", "Parellada", "Treixadura",
]

# D.O. -> broad wine region. Guessing a D.O. in the right region earns partial points.
ORIGIN_REGIONS = {
    "Rioja": "Valle del Ebro", "Navarra": "Valle del Ebro", "Somontano": "Valle del Ebro",
    "Cariñena": "Valle del Ebro", "Calatayud": "Valle del Ebro", "Campo de Borja": "Valle del Ebro",
    "Ribera del Duero": "Castilla y León", "Rueda": "Castilla y León", "Toro": "Castilla y León",
    "Bierzo": "Castilla y León", "Cigales": "Castilla y León",
    "Rías Baixas": "Atlántico", "Ribeiro": "Atlántico", "Monterrei": "Atlántico",
    "Valdeorras": "Atlántico", "Ribeira Sacra": "Atlántico", "Txakoli": "Atlántico",
    "Priorat": "Cataluña", "Montsant": "Cataluña", "Penedès": "Cataluña", "Terra Alta": "Cataluña",
    "Empordà": "Cataluña", "Costers del Segre": "Cataluña", "Cava": "Cataluña",
    "Valencia": "Levante", "Alicante": "Levante", "Utiel-Requena": "Levante",
    "Jumilla": "Levante", "Yecla": "Levante", "Bullas": "Levante",
    "La Mancha": "Centro", "Valdepeñas": "Centro", "Manchuela": "Centro",
    "Méntrida": "Centro", "Vinos de Madrid": "Centro",
    "Jerez": "Andalucía", "Montilla-Moriles": "Andalucía", "Málaga": "Andalucía",
}
DEFAULT_ORIGINS = list(ORIGIN_REGIONS)

# Ordered from youngest to oldest: neighbouring agings earn partial points.
DEFAULT_AGINGS = ["Joven", "Roble", "Crianza", "Reserva", "Gran Reserva"]

WINE_TYPES = ["Tinto", "Blanco", "Rosado", "Espumoso", "Dulce", "Generoso"]


def default_options() -> dict:
    return {
        "grapes": list(DEFAULT_GRAPES),
        "origins": list(DEFAULT_ORIGINS),
        "agings": list(DEFAULT_AGINGS),
    }
