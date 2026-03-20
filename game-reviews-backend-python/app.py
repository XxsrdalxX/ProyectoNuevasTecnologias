from flask import Flask, jsonify
from flask_cors import CORS
from database import db

from routes.catalogo import catalogo_bp
from routes.juegos import juegos_bp
from routes.resenas import resenas_bp
from routes.usuarios import usuarios_bp
from routes.test import test_bp

app = Flask(__name__)

# Configuración de la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:08012007@localhost:5432/db_GameReviews"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# CORS — mismos orígenes que el backend Java
CORS(app, origins="*")

# Inicializar SQLAlchemy
db.init_app(app)

# Registrar blueprints
app.register_blueprint(catalogo_bp)
app.register_blueprint(juegos_bp)
app.register_blueprint(resenas_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(test_bp)


# Manejo de errores globales
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
