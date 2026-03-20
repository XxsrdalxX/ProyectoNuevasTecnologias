Instrucciones para ejecutar el proyecto:
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
6. Ejecutar el backend
   python app.py
7. verificar funcionamiento
http://127.0.0.1:8080/
8. Verificar endpoints
   por ejemplo: http://127.0.0.1:8080/api/juegos
 
