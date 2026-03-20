from flask import Blueprint, jsonify, request
from database import db
from models import Resena, Usuario, Juego
from datetime import date

resenas_bp = Blueprint("resenas", __name__, url_prefix="/api/resenas")


@resenas_bp.get("")
def get_resenas():
    resenas = (
        db.session.query(Resena)
        .join(Resena.usuario)
        .join(Resena.juego)
        .all()
    )
    return jsonify([r.to_dict() for r in resenas])


@resenas_bp.get("/<int:id>")
def get_resena(id):
    resena = db.get_or_404(Resena, id)
    return jsonify(resena.to_dict())


@resenas_bp.get("/juego/<int:id_juego>")
def get_resenas_por_juego(id_juego):
    resenas = Resena.query.filter_by(idjuego=id_juego).all()
    return jsonify([r.to_dict() for r in resenas])


@resenas_bp.get("/juego/<int:id_juego>/recientes")
def get_resenas_recientes(id_juego):
    resenas = (
        Resena.query
        .filter_by(idjuego=id_juego)
        .order_by(Resena.fecharesena.desc())
        .all()
    )
    return jsonify([r.to_dict() for r in resenas])


@resenas_bp.get("/juego/<int:id_juego>/top")
def get_resenas_top(id_juego):
    resenas = (
        Resena.query
        .filter_by(idjuego=id_juego)
        .order_by(Resena.puntuacion.desc())
        .all()
    )
    return jsonify([r.to_dict() for r in resenas])


@resenas_bp.get("/usuario/<int:id_usuario>")
def get_resenas_por_usuario(id_usuario):
    resenas = Resena.query.filter_by(idusuario=id_usuario).all()
    return jsonify([r.to_dict() for r in resenas])


@resenas_bp.post("")
def create_resena():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud requerido"}), 400

    for field in ["usuarioId", "juegoId", "puntuacion"]:
        if data.get(field) is None:
            return jsonify({"error": f"El campo '{field}' es requerido"}), 400

    puntuacion = data["puntuacion"]
    if not isinstance(puntuacion, int) or not (1 <= puntuacion <= 10):
        return jsonify({"error": "La puntuación debe ser un número entero entre 1 y 10"}), 400

    if not db.session.get(Usuario, data["usuarioId"]):
        return jsonify({"error": "Usuario no encontrado"}), 404
    if not db.session.get(Juego, data["juegoId"]):
        return jsonify({"error": "Juego no encontrado"}), 404

    fecha = date.today()
    if data.get("fechaResena"):
        try:
            fecha = date.fromisoformat(data["fechaResena"])
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido, use yyyy-MM-dd"}), 400

    resena = Resena(
        comentario=data.get("comentario"),
        puntuacion=puntuacion,
        fecharesena=fecha,
        idusuario=data["usuarioId"],
        idjuego=data["juegoId"],
    )
    db.session.add(resena)
    db.session.commit()
    return jsonify(resena.to_dict()), 201


@resenas_bp.put("/<int:id>")
def update_resena(id):
    resena = db.get_or_404(Resena, id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud requerido"}), 400

    if "comentario" in data:
        resena.comentario = data["comentario"]
    if "puntuacion" in data:
        puntuacion = data["puntuacion"]
        if not isinstance(puntuacion, int) or not (1 <= puntuacion <= 10):
            return jsonify({"error": "La puntuación debe ser un número entero entre 1 y 10"}), 400
        resena.puntuacion = puntuacion
    if "fechaResena" in data:
        try:
            resena.fecharesena = date.fromisoformat(data["fechaResena"])
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido, use yyyy-MM-dd"}), 400

    db.session.commit()
    return jsonify(resena.to_dict())


@resenas_bp.delete("/<int:id>")
def delete_resena(id):
    resena = db.get_or_404(Resena, id)
    db.session.delete(resena)
    db.session.commit()
    return "", 204
