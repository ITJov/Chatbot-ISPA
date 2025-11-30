from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Enable CORS agar Frontend (Next.js port 3000) bisa akses Backend (Port 5000)
    CORS(app) 

    from .routes import main
    app.register_blueprint(main)

    return app