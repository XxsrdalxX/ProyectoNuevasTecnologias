import os
from dotenv import load_dotenv
load_dotenv()  # Debe ejecutarse antes de importar módulos que lean env vars

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database import db
from mongo_database import init_mongo_indexes, check_mongo_connection

from routes.auth import auth_bp
from routes.catalogo import catalogo_bp
from routes.juegos import juegos_bp
from routes.resenas import resenas_bp
from routes.usuarios import usuarios_bp
from routes.test import test_bp
from routes.analytics import analytics_bp

app = Flask(__name__)

# ─── Configuración PostgreSQL ─────────────────────────────────────────────────
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/db_GameReviews"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ─── Configuración JWT ────────────────────────────────────────────────────────
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-only-cambiar-en-produccion")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # 24 horas

# CORS
CORS(app, origins="*")

# Inicializar extensiones
db.init_app(app)
jwt = JWTManager(app)

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(catalogo_bp)
app.register_blueprint(juegos_bp)
app.register_blueprint(resenas_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(test_bp)
app.register_blueprint(analytics_bp)

# ─── Inicializar índices MongoDB al arrancar ──────────────────────────────────
with app.app_context():
    if check_mongo_connection():
        init_mongo_indexes()
        print("[MongoDB] Conectado y listo.")
    else:
        print("[MongoDB] ADVERTENCIA: No se pudo conectar a MongoDB. "
              "Los endpoints de analytics no estarán disponibles.")


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Recurso no encontrado"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Método no permitido"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Error interno del servidor"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
