from dotenv import load_dotenv
load_dotenv()

import os
from app.events import socketio
from app.handler.mongo import MongoHandler

from flask import Flask, request, send_from_directory
from flask_cors import CORS
from app.routes import main

import logging

app = Flask(__name__, static_folder="dist", static_url_path="")

app.config['DEBUG'] = os.environ.get('DEBUG', False)

CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "https://dev-depurador.devwil.com",
])

app.register_blueprint(main, url_prefix="/api")
# Configuración del logger

logger = logging.getLogger("mongo_handler")
logger.setLevel(logging.DEBUG)

log_handler = MongoHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

app.logger.addHandler(log_handler)
logger.addHandler(log_handler)

# Ruta para servir el archivo principal de React
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

# Ruta para manejar archivos estáticos y redirigir rutas desconocidas a React
@app.route('/<path:path>')
def serve_static_or_redirect(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        # Redirige al index.html si no es un archivo estático
        return send_from_directory(app.static_folder, 'index.html')
    
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

with app.app_context():
    socketio.init_app(app=app)

# Este bloque es solo para ejecutar la app directamente
if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host="0.0.0.0")
