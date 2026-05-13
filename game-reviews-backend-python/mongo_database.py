"""
mongo_database.py
Conexión a MongoDB para el módulo de analytics (persistencia políglota).
Maneja las colecciones: page_views, sessions, game_interactions.
"""

from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.errors import ConnectionFailure
import os

# ─── Configuración ────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "db_GameReviews_Analytics")

_client: MongoClient | None = None


def get_mongo_db():
    """
    Devuelve la instancia de la base de datos MongoDB.
    Implementa un patrón singleton para reutilizar la conexión.
    """
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client[MONGO_DB_NAME]


def init_mongo_indexes():
    """
    Crea los índices necesarios en las colecciones de analytics.
    Se llama una vez al iniciar la aplicación.
    """
    db = get_mongo_db()

    # ── page_views ──────────────────────────────────────────────────────────
    db.page_views.create_index([("timestamp", DESCENDING)])
    db.page_views.create_index([("session_id", ASCENDING)])
    db.page_views.create_index([("idjuego", ASCENDING)])
    db.page_views.create_index([("idusuario", ASCENDING)])

    # ── sessions ────────────────────────────────────────────────────────────
    db.sessions.create_index([("idusuario", ASCENDING)])
    db.sessions.create_index([("inicio", DESCENDING)])

    # ── game_interactions ───────────────────────────────────────────────────
    db.game_interactions.create_index([("idjuego", ASCENDING)])
    db.game_interactions.create_index([("session_id", ASCENDING)])
    db.game_interactions.create_index([("timestamp", DESCENDING)])
    db.game_interactions.create_index([("accion", ASCENDING)])

    print("[MongoDB] Índices inicializados correctamente.")


def check_mongo_connection() -> bool:
    """Verifica que la conexión con MongoDB esté activa."""
    try:
        get_mongo_db().command("ping")
        return True
    except ConnectionFailure:
        return False
