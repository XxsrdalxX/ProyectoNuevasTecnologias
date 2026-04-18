"""
analytics_service.py
Capa de servicio para todas las operaciones de analytics en MongoDB.
Aquí vive la lógica que vincula los datos SQL (idjuego, idusuario)
con los eventos almacenados en MongoDB.
"""

from datetime import datetime, timezone
from bson import ObjectId
from mongo_database import get_mongo_db


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _serialize(doc: dict) -> dict:
    """Convierte ObjectId y datetime a tipos serializables por JSON."""
    if doc is None:
        return None
    doc = dict(doc)
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    for key, val in doc.items():
        if isinstance(val, datetime):
            doc[key] = val.isoformat()
    return doc


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE VIEWS
# ═══════════════════════════════════════════════════════════════════════════════

def registrar_page_view(
    session_id: str,
    tipo_pagina: str,
    idjuego: int | None = None,
    idusuario: int | None = None,
    tiempo_en_pagina_seg: int = 0,
    scroll_porcentaje: int = 0,
    dispositivo: str = "desktop",
    pais: str = "CO",
    referrer: str = "",
) -> str:
    """
    Inserta un documento page_view en MongoDB.
    Retorna el _id del documento insertado como string.
    """
    db = get_mongo_db()
    doc = {
        "timestamp": _now(),
        "session_id": session_id,
        "idusuario": idusuario,       # FK al modelo SQL (puede ser null)
        "idjuego": idjuego,            # FK al modelo SQL (puede ser null)
        "tipo_pagina": tipo_pagina,
        "tiempo_en_pagina_seg": tiempo_en_pagina_seg,
        "scroll_porcentaje": scroll_porcentaje,
        "dispositivo": dispositivo,
        "pais": pais,
        "referrer": referrer,
    }
    result = db.page_views.insert_one(doc)
    return str(result.inserted_id)


def get_page_views_por_juego(idjuego: int, limite: int = 50) -> list[dict]:
    """Últimas N visitas a la página de un juego específico."""
    db = get_mongo_db()
    docs = (
        db.page_views
        .find({"idjuego": idjuego})
        .sort("timestamp", -1)
        .limit(limite)
    )
    return [_serialize(d) for d in docs]


def get_stats_juego(idjuego: int) -> dict:
    """
    Estadísticas agregadas de un juego cruzando page_views y game_interactions.
    Ejemplo de lógica de negocio políglota: se llama junto con datos SQL
    para enriquecer el perfil de un juego.
    """
    db = get_mongo_db()

    total_visitas = db.page_views.count_documents({"idjuego": idjuego})

    # Promedio de tiempo en página
    pipeline_tiempo = [
        {"$match": {"idjuego": idjuego, "tiempo_en_pagina_seg": {"$gt": 0}}},
        {"$group": {"_id": None, "promedio": {"$avg": "$tiempo_en_pagina_seg"}}},
    ]
    res_tiempo = list(db.page_views.aggregate(pipeline_tiempo))
    tiempo_promedio = round(res_tiempo[0]["promedio"], 1) if res_tiempo else 0

    # Conteo de interacciones por tipo de acción
    pipeline_acciones = [
        {"$match": {"idjuego": idjuego}},
        {"$group": {"_id": "$accion", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}},
    ]
    acciones = list(db.game_interactions.aggregate(pipeline_acciones))

    # Clicks en "escribir_resena" como indicador de intención
    clicks_resena = next(
        (a["total"] for a in acciones if a["_id"] == "click_escribir_resena"), 0
    )

    return {
        "idjuego": idjuego,
        "total_visitas": total_visitas,
        "tiempo_promedio_seg": tiempo_promedio,
        "interacciones": [{"accion": a["_id"], "total": a["total"]} for a in acciones],
        "clicks_escribir_resena": clicks_resena,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SESSIONS
# ═══════════════════════════════════════════════════════════════════════════════

def iniciar_sesion(
    session_id: str,
    idusuario: int | None = None,
    dispositivo: str = "desktop",
    utm_source: str = "",
) -> str:
    """
    Crea o actualiza el documento de sesión en MongoDB.
    El _id de la sesión es el session_id (string), no un ObjectId,
    para facilitar el join manual con page_views y game_interactions.
    """
    db = get_mongo_db()
    doc = {
        "_id": session_id,
        "inicio": _now(),
        "fin": None,
        "idusuario": idusuario,
        "paginas_vistas": 0,
        "juegos_vistos": [],
        "escribio_resena": False,
        "dispositivo": dispositivo,
        "utm_source": utm_source,
    }
    # upsert: crea si no existe
    db.sessions.update_one({"_id": session_id}, {"$setOnInsert": doc}, upsert=True)
    return session_id


def actualizar_sesion(
    session_id: str,
    idjuego: int | None = None,
    escribio_resena: bool = False,
) -> None:
    """
    Incrementa contadores de la sesión y registra juegos visitados.
    Diseñado para llamarse cada vez que se registra un page_view.
    """
    db = get_mongo_db()
    update = {
        "$inc": {"paginas_vistas": 1},
        "$set": {"fin": _now()},
    }
    if idjuego is not None:
        update["$addToSet"] = {"juegos_vistos": idjuego}
    if escribio_resena:
        update["$set"]["escribio_resena"] = True

    db.sessions.update_one({"_id": session_id}, update)


def get_sesiones_usuario(idusuario: int, limite: int = 10) -> list[dict]:
    """
    Últimas N sesiones de un usuario.
    Parte de la lógica políglota: se combina con datos del usuario desde SQL.
    """
    db = get_mongo_db()
    docs = (
        db.sessions
        .find({"idusuario": idusuario})
        .sort("inicio", -1)
        .limit(limite)
    )
    return [_serialize(d) for d in docs]


def get_actividad_reciente_usuario(idusuario: int, limite: int = 10) -> list[dict]:
    """
    Últimas N actividades (page_views + interactions) de un usuario.
    Este es el núcleo de la lógica políglota: los datos de actividad
    vienen de MongoDB, pero el perfil base del usuario viene de SQL.
    """
    db = get_mongo_db()

    # page_views recientes
    views = list(
        db.page_views
        .find({"idusuario": idusuario})
        .sort("timestamp", -1)
        .limit(limite)
    )

    # interacciones recientes
    interacciones = list(
        db.game_interactions
        .find({"idusuario": idusuario})
        .sort("timestamp", -1)
        .limit(limite)
    )

    # Unir y ordenar por timestamp descendente
    actividad = [
        {**_serialize(v), "tipo_evento": "page_view"} for v in views
    ] + [
        {**_serialize(i), "tipo_evento": "interaccion"} for i in interacciones
    ]
    actividad.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return actividad[:limite]


# ═══════════════════════════════════════════════════════════════════════════════
# GAME INTERACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def registrar_interaccion(
    session_id: str,
    idjuego: int,
    accion: str,
    idusuario: int | None = None,
    valor=None,
) -> str:
    """
    Registra un evento puntual dentro de la página de un juego.
    Acciones posibles: click_escribir_resena, ver_trailer,
    expandir_descripcion, puntuar, etc.
    """
    db = get_mongo_db()
    doc = {
        "timestamp": _now(),
        "session_id": session_id,
        "idusuario": idusuario,
        "idjuego": idjuego,
        "accion": accion,
        "valor": valor,
    }
    result = db.game_interactions.insert_one(doc)
    return str(result.inserted_id)


def get_interacciones_por_juego(idjuego: int, limite: int = 100) -> list[dict]:
    """Últimas N interacciones en la página de un juego."""
    db = get_mongo_db()
    docs = (
        db.game_interactions
        .find({"idjuego": idjuego})
        .sort("timestamp", -1)
        .limit(limite)
    )
    return [_serialize(d) for d in docs]


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD GLOBAL (lógica políglota de alto nivel)
# ═══════════════════════════════════════════════════════════════════════════════

def get_juegos_mas_visitados(limite: int = 10) -> list[dict]:
    """
    Top N juegos por número de visitas.
    Retorna idjuego + total_visitas para que el endpoint
    pueda enriquecer con datos SQL (título, imagen, etc.).
    """
    db = get_mongo_db()
    pipeline = [
        {"$match": {"idjuego": {"$ne": None}}},
        {"$group": {"_id": "$idjuego", "total_visitas": {"$sum": 1}}},
        {"$sort": {"total_visitas": -1}},
        {"$limit": limite},
        {"$project": {"idjuego": "$_id", "total_visitas": 1, "_id": 0}},
    ]
    return list(db.page_views.aggregate(pipeline))


def get_metricas_globales() -> dict:
    """Resumen global del sistema de analytics."""
    db = get_mongo_db()
    return {
        "total_page_views": db.page_views.count_documents({}),
        "total_sessions": db.sessions.count_documents({}),
        "total_interactions": db.game_interactions.count_documents({}),
        "sesiones_con_resena": db.sessions.count_documents({"escribio_resena": True}),
    }
