from flask import Blueprint, jsonify
from database import db
from models import Usuario

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


@usuarios_bp.get("")
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([u.to_dict() for u in usuarios])


@usuarios_bp.get("/<int:id>")
def get_usuario(id):
    usuario = db.get_or_404(Usuario, id)
    return jsonify(usuario.to_dict())
