from flask import Blueprint, jsonify
from database import db
from models import Usuario, Juego, Resena, Estudio, Genero, Plataforma

test_bp = Blueprint("test", __name__, url_prefix="/api/test")


@test_bp.get("/health")
def health():
    return jsonify({"status": "UP"})


@test_bp.get("/repositories")
def repositories():
    return jsonify({
        "totalUsuarios": db.session.query(Usuario).count(),
        "totalJuegos": db.session.query(Juego).count(),
        "totalResenas": db.session.query(Resena).count(),
        "totalEstudios": db.session.query(Estudio).count(),
        "totalGeneros": db.session.query(Genero).count(),
        "totalPlataformas": db.session.query(Plataforma).count(),
    })
