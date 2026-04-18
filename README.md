Instrucciones para ejecutar el proyecto:
0. Clonar el repositorio 
git clone https://github.com/XxsrdalxX/ProyectoNuevasTecnologias
cd game-reviews-backend-python
1. ir a la carpeta del backend
cd game-reviews-backend-python
2. Iniciar el entorno virtual en nuestro proyecto
con el comando python -m venv .venv
3. activar los scripts
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate
4. instalar librerias
pip install -r ./requirements.txt
5. Crear la DB
   En pgadmin4 o postrgres deberan crear una db llamada db_GameReviews
y luego ejecutar el archivo llamado db_GR.sql, seguido de eso insertaran los datos  del archivo datos_prueba.sql para insertar datos

Para NoSQL ejecutar este archivo py seed.py para poder crear las colecciones
 Importante: el seed de MongoDB referencia los IDs de juegos y usuarios de PostgreSQL. Asegúrate de tener al menos 5–10 juegos y 2–3 usuarios antes de continuar
 6. Iniciar MONGODB
 Este comando requiere PowerShell abierto como administrador:
tecla Windows → escribe "PowerShell" → clic derecho → "Ejecutar como administrador"
net start MongoDB
Respuesta esperada: El servicio MongoDB se está iniciando o El servicio solicitado ya ha sido iniciado
7. Datos de prueba para mongoDB:
py seed_mongo.py
Si sale ModuleNotFoundError: No module named 'pymongo', instálalo directamente y vuelve a intentar:
py -m pip install pymongo==4.7.3
py seed_mongo.py
8. Ejecutar el backend
   python app.py
9. verificar funcionamiento
GET http://localhost:8080/api/juegos
GET http://localhost:8080/api/juegos/1
GET http://localhost:8080/api/resenas
POST http://localhost:8080/api/analytics/pageview
Content-Type: application/json

{
  "session_id": "ses_prueba_001",
  "tipo_pagina": "detalle_juego",
  "idjuego": 1,
  "idusuario": 1,
  "tiempo_en_pagina_seg": 120,
  "scroll_porcentaje": 80,
  "dispositivo": "desktop",
  "pais": "CO"
}

POST http://localhost:8080/api/analytics/interaction
Content-Type: application/json

{
  "session_id": "ses_prueba_001",
  "idjuego": 1,
  "accion": "click_escribir_resena",
  "idusuario": 1
}

ENDPOINTS COMBINADOS NO SQL+SQL:
GET http://localhost:8080/api/analytics/juego/1/stats
GET http://localhost:8080/api/analytics/usuario/1/perfil
GET http://localhost:8080/api/analytics/dashboard

