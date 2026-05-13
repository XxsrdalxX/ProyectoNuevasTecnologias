"""
routes/analytics.py
Endpoints de analytics (MongoDB) — persistencia políglota.

Rutas:
  POST   /api/analytics/pageview              → registrar visita
  POST   /api/analytics/session/start         → iniciar sesión
  POST   /api/analytics/session/update        → actualizar sesión
  POST   /api/analytics/interaction           → registrar interacción
  GET    /api/analytics/juego/<id>/stats      → stats MongoDB + datos SQL del juego
  GET    /api/analytics/juego/<id>/pageviews  → últimas visitas a un juego
  GET    /api/analytics/usuario/<id>/perfil   → perfil políglota (SQL + actividad MongoDB)
  GET    /api/analytics/dashboard             → métricas globales + top juegos enriquecidos
"""

from flask import Blueprint, jsonify, request
from database import db
from models import Juego, Usuario
import analytics_service as svc

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _bad_request(msg: str):
    return jsonify({"error": msg}), 400


def _get_body():
    return request.get_json(silent=True) or {}


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE VIEWS
# ═══════════════════════════════════════════════════════════════════════════════

@analytics_bp.post("/pageview")
def post_pageview():
    """
    Registra una visita a una página.
    También actualiza el documento de sesión correspondiente (si existe).

    Body JSON esperado:
      session_id      (str, requerido)
      tipo_pagina     (str, requerido)  — "catalogo" | "detalle_juego" | "inicio" | etc.
      idjuego         (int, opcional)
      idusuario       (int, opcional)
      tiempo_en_pagina_seg (int, opcional)
      scroll_porcentaje    (int, opcional)
      dispositivo     (str, opcional)
      pais            (str, opcional)
      referrer        (str, opcional)
    """
    data = _get_body()
    session_id = data.get("session_id")
    tipo_pagina = data.get("tipo_pagina")

    if not session_id or not tipo_pagina:
        return _bad_request("Los campos 'session_id' y 'tipo_pagina' son requeridos.")

    inserted_id = svc.registrar_page_view(
        session_id=session_id,
        tipo_pagina=tipo_pagina,
        idjuego=data.get("idjuego"),
        idusuario=data.get("idusuario"),
        tiempo_en_pagina_seg=data.get("tiempo_en_pagina_seg", 0),
        scroll_porcentaje=data.get("scroll_porcentaje", 0),
        dispositivo=data.get("dispositivo", "desktop"),
        pais=data.get("pais", "CO"),
        referrer=data.get("referrer", ""),
    )

    # Actualizar sesión en paralelo (fire-and-forget, no bloquea la respuesta)
    svc.actualizar_sesion(
        session_id=session_id,
        idjuego=data.get("idjuego"),
    )

    return jsonify({"inserted_id": inserted_id, "status": "ok"}), 201


# ═══════════════════════════════════════════════════════════════════════════════
# SESSIONS
# ═══════════════════════════════════════════════════════════════════════════════

@analytics_bp.post("/session/start")
def post_session_start():
    """
    Inicia o registra una nueva sesión de usuario.

    Body JSON:
      session_id  (str, requerido)
      idusuario   (int, opcional)
      dispositivo (str, opcional)
      utm_source  (str, opcional)
    """
    data = _get_body()
    session_id = data.get("session_id")
    if not session_id:
        return _bad_request("El campo 'session_id' es requerido.")

    svc.iniciar_sesion(
        session_id=session_id,
        idusuario=data.get("idusuario"),
        dispositivo=data.get("dispositivo", "desktop"),
        utm_source=data.get("utm_source", ""),
    )
    return jsonify({"session_id": session_id, "status": "iniciada"}), 201


@analytics_bp.post("/session/update")
def post_session_update():
    """
    Actualiza una sesión existente (marca que se escribió una reseña, etc.).

    Body JSON:
      session_id       (str, requerido)
      idjuego          (int, opcional)
      escribio_resena  (bool, opcional)
    """
    data = _get_body()
    session_id = data.get("session_id")
    if not session_id:
        return _bad_request("El campo 'session_id' es requerido.")

    svc.actualizar_sesion(
        session_id=session_id,
        idjuego=data.get("idjuego"),
        escribio_resena=data.get("escribio_resena", False),
    )
    return jsonify({"status": "actualizada"}), 200


# ═══════════════════════════════════════════════════════════════════════════════
# GAME INTERACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@analytics_bp.post("/interaction")
def post_interaction():
    """
    Registra un evento puntual en la página de un juego.

    Body JSON:
      session_id  (str, requerido)
      idjuego     (int, requerido)
      accion      (str, requerido)  — "click_escribir_resena" | "ver_trailer" | etc.
      idusuario   (int, opcional)
      valor       (any, opcional)   — útil cuando la acción es "puntuar"
    """
    data = _get_body()
    session_id = data.get("session_id")
    idjuego = data.get("idjuego")
    accion = data.get("accion")

    if not session_id or not idjuego or not accion:
        return _bad_request("Los campos 'session_id', 'idjuego' y 'accion' son requeridos.")

    inserted_id = svc.registrar_interaccion(
        session_id=session_id,
        idjuego=idjuego,
        accion=accion,
        idusuario=data.get("idusuario"),
        valor=data.get("valor"),
    )
    return jsonify({"inserted_id": inserted_id, "status": "ok"}), 201


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS POR JUEGO — lógica políglota
# ═══════════════════════════════════════════════════════════════════════════════

@analytics_bp.get("/juego/<int:idjuego>/stats")
def get_stats_juego(idjuego: int):
    """
    Combina datos SQL (título, calificación, estudio) con
    estadísticas de MongoDB (visitas, tiempo promedio, interacciones).
    Este endpoint es el ejemplo central de persistencia políglota.
    """
    # ── Datos SQL ──────────────────────────────────────────────────────────
    juego = db.session.get(Juego, idjuego)
    if juego is None:
        return jsonify({"error": "Juego no encontrado"}), 404

    datos_sql = {
        "titulo": juego.titulo,
        "calificacionProm": float(juego.calificacionprom) if juego.calificacionprom else None,
        "urlImagen": juego.urlimagen,
        "estudio": juego.estudio.nombre if juego.estudio else None,
        "genero": juego.genero.nombre if juego.genero else None,
        "plataforma": juego.plataforma.nombre if juego.plataforma else None,
    }

    # ── Datos MongoDB ──────────────────────────────────────────────────────
    datos_mongo = svc.get_stats_juego(idjuego)

    return jsonify({
        "idjuego": idjuego,
        **datos_sql,
        "analytics": datos_mongo,
    })


@analytics_bp.get("/juego/<int:idjuego>/pageviews")
def get_pageviews_juego(idjuego: int):
    """Últimas visitas registradas para un juego."""
    limite = min(int(request.args.get("limite", 50)), 200)
    views = svc.get_page_views_por_juego(idjuego, limite)
    return jsonify({"idjuego": idjuego, "total": len(views), "page_views": views})


@analytics_bp.get("/juego/<int:idjuego>/interacciones")
def get_interacciones_juego(idjuego: int):
    """Últimas interacciones registradas para un juego."""
    limite = min(int(request.args.get("limite", 100)), 500)
    interacciones = svc.get_interacciones_por_juego(idjuego, limite)
    return jsonify({"idjuego": idjuego, "total": len(interacciones), "interacciones": interacciones})


# ═══════════════════════════════════════════════════════════════════════════════
# PERFIL POLÍGLOTA DE USUARIO — el ejemplo más claro de persistencia políglota
# ═══════════════════════════════════════════════════════════════════════════════

@analytics_bp.get("/usuario/<int:idusuario>/perfil")
def get_perfil_poliglota(idusuario: int):
    """
    Perfil completo de un usuario combinando:
      - SQL: nombre, correo, cantidad de reseñas, datos estáticos
      - MongoDB: últimas 10 actividades, últimas sesiones, juegos más visitados

    Este es el ejemplo de lógica de negocio que vincula ambas bases de datos.
    """
    # ── Perfil base desde SQL ──────────────────────────────────────────────
    usuario = db.session.get(Usuario, idusuario)
    if usuario is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    perfil_sql = usuario.to_dict()

    # ── Actividad reciente desde MongoDB (últimas 10 actividades) ──────────
    actividad = svc.get_actividad_reciente_usuario(idusuario, limite=10)

    # ── Últimas 5 sesiones desde MongoDB ──────────────────────────────────
    sesiones = svc.get_sesiones_usuario(idusuario, limite=5)

    # ── Enriquecer actividad con títulos de juegos (datos SQL) ─────────────
    # Recolectar todos los idjuego únicos que aparecen en la actividad
    ids_juego = {
        a["idjuego"] for a in actividad if a.get("idjuego") is not None
    }
    juegos_map = {}
    if ids_juego:
        juegos_sql = Juego.query.filter(Juego.idjuego.in_(ids_juego)).all()
        juegos_map = {j.idjuego: {"titulo": j.titulo, "urlImagen": j.urlimagen} for j in juegos_sql}

    for evento in actividad:
        if evento.get("idjuego") and evento["idjuego"] in juegos_map:
            evento["juego_info"] = juegos_map[evento["idjuego"]]

    return jsonify({
        "perfil": perfil_sql,
        "ultimas_actividades": actividad,
        "ultimas_sesiones": sesiones,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD GLOBAL
# ═══════════════════════════════════════════════════════════════════════════════

@analytics_bp.get("/dashboard")
def get_dashboard():
    """
    Dashboard global de analytics.
    Combina métricas MongoDB con datos descriptivos de SQL
    para los juegos más visitados.
    """
    # ── Métricas globales desde MongoDB ───────────────────────────────────
    metricas = svc.get_metricas_globales()

    # ── Top 10 juegos más visitados (idjuego + conteo desde MongoDB) ──────
    top_mongo = svc.get_juegos_mas_visitados(limite=10)

    # ── Enriquecer con datos SQL ───────────────────────────────────────────
    ids_top = [item["idjuego"] for item in top_mongo]
    juegos_sql = {}
    if ids_top:
        juegos = Juego.query.filter(Juego.idjuego.in_(ids_top)).all()
        juegos_sql = {
            j.idjuego: {
                "titulo": j.titulo,
                "urlImagen": j.urlimagen,
                "calificacionProm": float(j.calificacionprom) if j.calificacionprom else None,
                "genero": j.genero.nombre if j.genero else None,
            }
            for j in juegos
        }

    top_juegos_enriquecidos = [
        {
            "idjuego": item["idjuego"],
            "total_visitas": item["total_visitas"],
            **(juegos_sql.get(item["idjuego"]) or {}),
        }
        for item in top_mongo
    ]

    return jsonify({
        "metricas_globales": metricas,
        "top_juegos_mas_visitados": top_juegos_enriquecidos,
    })
