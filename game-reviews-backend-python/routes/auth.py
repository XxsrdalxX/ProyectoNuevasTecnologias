from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity
from database import db
from models import Usuario
from auth_helpers import jwt_requerido

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/registro")
def registro():
    """
    Registra un nuevo usuario con rol 'cliente'.
    Body JSON: { nombre, correo, contrasena }
    """
    data = request.get_json(silent=True) or {}

    nombre = data.get("nombre", "").strip()
    correo = data.get("correo", "").strip().lower()
    contrasena = data.get("contrasena", "")

    if not nombre:
        return jsonify({"error": "El campo 'nombre' es requerido"}), 400
    if not correo:
        return jsonify({"error": "El campo 'correo' es requerido"}), 400
    if not contrasena or len(contrasena) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "Ya existe una cuenta con ese correo"}), 409

    usuario = Usuario(
        nombre=nombre,
        correo=correo,
        contrasenahash=generate_password_hash(contrasena),
        rol="cliente",
    )
    db.session.add(usuario)
    db.session.commit()

    return jsonify({
        "mensaje": "Usuario registrado exitosamente",
        "usuario": usuario.to_dict(),
    }), 201


@auth_bp.post("/login")
def login():
    """
    Inicia sesión y devuelve un token JWT.
    Body JSON: { correo, contrasena }
    El token incluye el id del usuario y su rol en los claims.
    """
    data = request.get_json(silent=True) or {}

    correo = data.get("correo", "").strip().lower()
    contrasena = data.get("contrasena", "")

    if not correo or not contrasena:
        return jsonify({"error": "Los campos 'correo' y 'contrasena' son requeridos"}), 400

    usuario = Usuario.query.filter_by(correo=correo).first()
    if not usuario or not check_password_hash(usuario.contrasenahash, contrasena):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = create_access_token(
        identity=usuario.idusuario,
        additional_claims={"rol": usuario.rol, "nombre": usuario.nombre},
    )

    return jsonify({
        "token": token,
        "usuario": usuario.to_dict(),
    }), 200


@auth_bp.get("/me")
@jwt_requerido
def me():
    """Devuelve el perfil del usuario autenticado. Útil para validar el token."""
    idusuario = get_jwt_identity()
    usuario = db.session.get(Usuario, idusuario)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(usuario.to_dict()), 200
