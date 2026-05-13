"""
seed_mongo.py
Pobla las colecciones de MongoDB con datos de prueba que referencian
los IDs del modelo SQL existente (juegos 1-10, usuarios 1-3).

Uso:
  python seed_mongo.py
"""

from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
import random

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "db_GameReviews_Analytics"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Limpiar colecciones anteriores
db.page_views.drop()
db.sessions.drop()
db.game_interactions.drop()
print("Colecciones limpiadas.")

def dt(minutes_ago: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)

DISPOSITIVOS = ["desktop", "mobile", "tablet"]
PAISES = ["CO", "MX", "AR", "ES", "CL"]
REFERRERS = ["google", "newsletter", "direct", "twitter", "youtube"]
ACCIONES = [
    "click_escribir_resena",
    "ver_trailer",
    "expandir_descripcion",
    "scroll_galeria",
    "puntuar",
]
TIPOS_PAGINA = ["inicio", "catalogo", "detalle_juego", "perfil_usuario", "registro"]

# IDs que existen en el modelo SQL de prueba
IDS_JUEGO = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
IDS_USUARIO = [1, 2, 3, 4]

# ─── Sesiones ────────────────────────────────────────────────────────────────
sesiones = []
for i in range(1, 16):
    session_id = f"ses_{i:03d}abc"
    idusuario = random.choice(IDS_USUARIO + [None, None])  # algunas anónimas
    juegos_vistos = random.sample(IDS_JUEGO, random.randint(1, 4))
    inicio = dt(random.randint(30, 600))
    fin = inicio + timedelta(minutes=random.randint(5, 45))
    sesiones.append({
        "_id": session_id,
        "inicio": inicio,
        "fin": fin,
        "idusuario": idusuario,
        "paginas_vistas": random.randint(2, 10),
        "juegos_vistos": juegos_vistos,
        "escribio_resena": random.choice([True, False, False]),
        "dispositivo": random.choice(DISPOSITIVOS),
        "utm_source": random.choice(REFERRERS),
    })

db.sessions.insert_many(sesiones)
print(f"  Insertadas {len(sesiones)} sesiones.")

# ─── Page Views ──────────────────────────────────────────────────────────────
page_views = []
for idx, ses in enumerate(sesiones):
    for _ in range(random.randint(2, 6)):
        idjuego = random.choice(ses["juegos_vistos"] + [None])
        page_views.append({
            "timestamp": ses["inicio"] + timedelta(seconds=random.randint(10, 1200)),
            "session_id": ses["_id"],
            "idusuario": ses["idusuario"],
            "idjuego": idjuego,
            "tipo_pagina": "detalle_juego" if idjuego else random.choice(TIPOS_PAGINA),
            "tiempo_en_pagina_seg": random.randint(10, 300),
            "scroll_porcentaje": random.randint(10, 100),
            "dispositivo": ses["dispositivo"],
            "pais": random.choice(PAISES),
            "referrer": ses["utm_source"],
        })

db.page_views.insert_many(page_views)
print(f"  Insertados {len(page_views)} page_views.")

# ─── Game Interactions ────────────────────────────────────────────────────────
interactions = []
for ses in sesiones:
    for idjuego in ses["juegos_vistos"]:
        for _ in range(random.randint(1, 3)):
            accion = random.choice(ACCIONES)
            valor = random.randint(1, 10) if accion == "puntuar" else None
            interactions.append({
                "timestamp": ses["inicio"] + timedelta(seconds=random.randint(30, 900)),
                "session_id": ses["_id"],
                "idusuario": ses["idusuario"],
                "idjuego": idjuego,
                "accion": accion,
                "valor": valor,
            })

db.game_interactions.insert_many(interactions)
print(f"  Insertadas {len(interactions)} game_interactions.")

print("\n✅ Seed de MongoDB completado.")
print(f"   DB: {DB_NAME}")
print(f"   Colecciones: page_views, sessions, game_interactions")
