from flask import Blueprint, jsonify
from database import db
from models import Usuario
from auth_helpers import solo_admin

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


@usuarios_bp.get("")
@solo_admin
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([u.to_dict() for u in usuarios])


@usuarios_bp.get("/<int:id>")
@solo_admin
def get_usuario(id):
    usuario = db.get_or_404(Usuario, id)
    return jsonify(usuario.to_dict())


@usuarios_bp.delete("/<int:id>")
@solo_admin
def delete_usuario(id):
    usuario = db.get_or_404(Usuario, id)
    db.session.delete(usuario)
    db.session.commit()
    return "", 204
