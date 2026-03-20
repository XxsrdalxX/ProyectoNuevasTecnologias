from flask import Blueprint, jsonify, request
from database import db
from models import Juego, Estudio, Genero, Plataforma
from datetime import date

juegos_bp = Blueprint("juegos", __name__, url_prefix="/api/juegos")


@juegos_bp.get("")
def get_juegos():
    juegos = Juego.query.all()
    return jsonify([j.to_dict() for j in juegos])


@juegos_bp.get("/<int:id>")
def get_juego(id):
    juego = db.get_or_404(Juego, id)
    return jsonify(juego.to_dict())


@juegos_bp.get("/buscar")
def buscar_juegos():
    titulo = request.args.get("titulo", "")
    juegos = Juego.query.filter(Juego.titulo.ilike(f"%{titulo}%")).all()
    if not juegos:
        return jsonify([]), 204
    return jsonify([j.to_dict() for j in juegos])


@juegos_bp.get("/genero/<int:id_genero>")
def get_juegos_por_genero(id_genero):
    juegos = Juego.query.filter_by(idgenero=id_genero).all()
    return jsonify([j.to_dict() for j in juegos])


@juegos_bp.get("/plataforma/<int:id_plataforma>")
def get_juegos_por_plataforma(id_plataforma):
    juegos = Juego.query.filter_by(idplataforma=id_plataforma).all()
    return jsonify([j.to_dict() for j in juegos])


@juegos_bp.get("/estudio/<int:id_estudio>")
def get_juegos_por_estudio(id_estudio):
    juegos = Juego.query.filter_by(idestudio=id_estudio).all()
    return jsonify([j.to_dict() for j in juegos])


@juegos_bp.get("/top")
def get_top_juegos():
    juegos = Juego.query.order_by(Juego.calificacionprom.desc()).all()
    return jsonify([j.to_dict() for j in juegos])


@juegos_bp.post("")
def create_juego():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud requerido"}), 400

    required = ["titulo", "idEstudio", "idGenero", "idPlataforma"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"El campo '{field}' es requerido"}), 400

    if not db.session.get(Estudio, data["idEstudio"]):
        return jsonify({"error": "Estudio no encontrado"}), 404
    if not db.session.get(Genero, data["idGenero"]):
        return jsonify({"error": "Género no encontrado"}), 404
    if not db.session.get(Plataforma, data["idPlataforma"]):
        return jsonify({"error": "Plataforma no encontrada"}), 404

    fecha = None
    if data.get("fechaLanzamiento"):
        try:
            fecha = date.fromisoformat(data["fechaLanzamiento"])
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido, use yyyy-MM-dd"}), 400

    juego = Juego(
        titulo=data["titulo"],
        descripcion=data.get("descripcion"),
        fechalanzamiento=fecha,
        precio=data.get("precio"),
        calificacionprom=data.get("calificacionProm"),
        urlimagen=data.get("urlImagen"),
        idestudio=data["idEstudio"],
        idgenero=data["idGenero"],
        idplataforma=data["idPlataforma"],
    )
    db.session.add(juego)
    db.session.commit()
    return jsonify(juego.to_dict()), 201


@juegos_bp.put("/<int:id>")
def update_juego(id):
    juego = db.get_or_404(Juego, id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de la solicitud requerido"}), 400

    if "titulo" in data:
        juego.titulo = data["titulo"]
    if "descripcion" in data:
        juego.descripcion = data["descripcion"]
    if "precio" in data:
        juego.precio = data["precio"]
    if "calificacionProm" in data:
        juego.calificacionprom = data["calificacionProm"]
    if "urlImagen" in data:
        juego.urlimagen = data["urlImagen"]
    if "fechaLanzamiento" in data:
        try:
            juego.fechalanzamiento = date.fromisoformat(data["fechaLanzamiento"])
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido, use yyyy-MM-dd"}), 400
    if "idEstudio" in data:
        if not db.session.get(Estudio, data["idEstudio"]):
            return jsonify({"error": "Estudio no encontrado"}), 404
        juego.idestudio = data["idEstudio"]
    if "idGenero" in data:
        if not db.session.get(Genero, data["idGenero"]):
            return jsonify({"error": "Género no encontrado"}), 404
        juego.idgenero = data["idGenero"]
    if "idPlataforma" in data:
        if not db.session.get(Plataforma, data["idPlataforma"]):
            return jsonify({"error": "Plataforma no encontrada"}), 404
        juego.idplataforma = data["idPlataforma"]

    db.session.commit()
    return jsonify(juego.to_dict())


@juegos_bp.delete("/<int:id>")
def delete_juego(id):
    juego = db.get_or_404(Juego, id)
    db.session.delete(juego)
    db.session.commit()
    return "", 204
