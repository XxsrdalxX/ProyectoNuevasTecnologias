from flask import Blueprint, jsonify, request
from database import db
from models import Genero, Plataforma, Estudio

catalogo_bp = Blueprint("catalogo", __name__, url_prefix="/api/catalogo")


# ── Géneros ──────────────────────────────────────────────────────────────────

@catalogo_bp.get("/generos")
def get_generos():
    generos = Genero.query.all()
    return jsonify([g.to_dict() for g in generos])


@catalogo_bp.get("/generos/<int:id>")
def get_genero(id):
    genero = db.get_or_404(Genero, id)
    return jsonify(genero.to_dict())


@catalogo_bp.post("/generos")
def create_genero():
    data = request.get_json()
    if not data or not data.get("nombre"):
        return jsonify({"error": "El campo 'nombre' es requerido"}), 400
    genero = Genero(nombre=data["nombre"])
    db.session.add(genero)
    db.session.commit()
    return jsonify(genero.to_dict()), 201


# ── Plataformas ───────────────────────────────────────────────────────────────

@catalogo_bp.get("/plataformas")
def get_plataformas():
    plataformas = Plataforma.query.all()
    return jsonify([p.to_dict() for p in plataformas])


@catalogo_bp.get("/plataformas/<int:id>")
def get_plataforma(id):
    plataforma = db.get_or_404(Plataforma, id)
    return jsonify(plataforma.to_dict())


@catalogo_bp.post("/plataformas")
def create_plataforma():
    data = request.get_json()
    if not data or not data.get("nombre"):
        return jsonify({"error": "El campo 'nombre' es requerido"}), 400
    plataforma = Plataforma(nombre=data["nombre"])
    db.session.add(plataforma)
    db.session.commit()
    return jsonify(plataforma.to_dict()), 201


# ── Estudios ──────────────────────────────────────────────────────────────────

@catalogo_bp.get("/estudios")
def get_estudios():
    estudios = Estudio.query.all()
    return jsonify([e.to_dict() for e in estudios])


@catalogo_bp.get("/estudios/<int:id>")
def get_estudio(id):
    estudio = db.get_or_404(Estudio, id)
    return jsonify(estudio.to_dict())


@catalogo_bp.post("/estudios")
def create_estudio():
    data = request.get_json()
    if not data or not data.get("nombre"):
        return jsonify({"error": "El campo 'nombre' es requerido"}), 400
    estudio = Estudio(nombre=data["nombre"])
    db.session.add(estudio)
    db.session.commit()
    return jsonify(estudio.to_dict()), 201
