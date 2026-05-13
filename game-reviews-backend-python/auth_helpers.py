from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity


def jwt_requerido(fn):
    """Requiere token JWT válido. Cualquier usuario autenticado puede acceder."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"error": "Token requerido o inválido"}), 401
        return fn(*args, **kwargs)
    return wrapper


def solo_admin(fn):
    """Requiere token JWT con rol 'admin'."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"error": "Token requerido o inválido"}), 401
        claims = get_jwt()
        if claims.get("rol") != "admin":
            return jsonify({"error": "Acceso restringido a administradores"}), 403
        return fn(*args, **kwargs)
    return wrapper


def propietario_o_admin(get_idusuario_fn):
    """
    Requiere que el usuario autenticado sea el propietario del recurso
    (determinado por get_idusuario_fn(kwargs)) o sea admin.

    Uso:
        @propietario_o_admin(lambda kw: Resena.query.get(kw['id']).idusuario)
        def mi_vista(id): ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                return jsonify({"error": "Token requerido o inválido"}), 401
            claims = get_jwt()
            if claims.get("rol") == "admin":
                return fn(*args, **kwargs)
            propietario_id = get_idusuario_fn(kwargs)
            if propietario_id is None:
                return jsonify({"error": "Recurso no encontrado"}), 404
            if get_jwt_identity() != propietario_id:
                return jsonify({"error": "No tienes permiso para modificar este recurso"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
