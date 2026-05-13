from flask import Blueprint, jsonify, request
from database import db
from models import Resena, Usuario, Juego
from datetime import date
from sqlalchemy import func
from auth_helpers import jwt_requerido, propietario_o_admin
from flask_jwt_extended import get_jwt_identity

resenas_bp = Blueprint("resenas", __name__, url_prefix="/api/resenas")


def _recalcular_calificacion(idjuego: int) -> None:
    """Recalcula y persiste el promedio de calificación de un juego."""
    resultado = db.session.query(func.avg(Resena.puntuacion)).filter_by(idjuego=idjuego).scalar()
    juego = db.session.get(Juego, idjuego)
    if juego:
        juego.calificacionprom = round(float(resultado), 2) if resultado else None


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
@jwt_requerido
def create_resena():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud requerido"}), 400

    # Usar identidad del JWT — ignora el usuarioId del body para evitar suplantación
    idusuario = get_jwt_identity()

    if data.get("juegoId") is None:
        return jsonify({"error": "El campo 'juegoId' es requerido"}), 400
    if data.get("puntuacion") is None:
        return jsonify({"error": "El campo 'puntuacion' es requerido"}), 400

    puntuacion = data["puntuacion"]
    if not isinstance(puntuacion, int) or not (1 <= puntuacion <= 10):
        return jsonify({"error": "La puntuación debe ser un número entero entre 1 y 10"}), 400

    usuario = db.session.get(Usuario, idusuario)
    if not usuario:
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
        idusuario=idusuario,
        idjuego=data["juegoId"],
    )
    db.session.add(resena)
    usuario.cantidadresenas = (usuario.cantidadresenas or 0) + 1
    db.session.commit()

    _recalcular_calificacion(data["juegoId"])
    db.session.commit()

    return jsonify(resena.to_dict()), 201


@resenas_bp.put("/<int:id>")
@propietario_o_admin(lambda kw: getattr(db.session.get(Resena, kw["id"]), "idusuario", None))
def update_resena(id):
    resena = db.get_or_404(Resena, id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud requerido"}), 400

    puntuacion_cambio = False
    if "comentario" in data:
        resena.comentario = data["comentario"]
    if "puntuacion" in data:
        puntuacion = data["puntuacion"]
        if not isinstance(puntuacion, int) or not (1 <= puntuacion <= 10):
            return jsonify({"error": "La puntuación debe ser un número entero entre 1 y 10"}), 400
        resena.puntuacion = puntuacion
        puntuacion_cambio = True
    if "fechaResena" in data:
        try:
            resena.fecharesena = date.fromisoformat(data["fechaResena"])
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido, use yyyy-MM-dd"}), 400

    db.session.commit()

    if puntuacion_cambio:
        _recalcular_calificacion(resena.idjuego)
        db.session.commit()

    return jsonify(resena.to_dict())


@resenas_bp.delete("/<int:id>")
@propietario_o_admin(lambda kw: getattr(db.session.get(Resena, kw["id"]), "idusuario", None))
def delete_resena(id):
    resena = db.get_or_404(Resena, id)
    idjuego = resena.idjuego
    idusuario = resena.idusuario

    db.session.delete(resena)

    usuario = db.session.get(Usuario, idusuario)
    if usuario and (usuario.cantidadresenas or 0) > 0:
        usuario.cantidadresenas -= 1

    db.session.commit()

    _recalcular_calificacion(idjuego)
    db.session.commit()

    return "", 204
