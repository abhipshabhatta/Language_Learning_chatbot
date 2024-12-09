from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv
import os
from db import setup_db, initialize_mongo_collections, initialize_postgres_tables
from .auth import auth_bp
from .chat import chat_bp


load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configure JWT Secret Key
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    if not app.config['JWT_SECRET_KEY']:
        raise Exception("JWT_SECRET_KEY is not set in environment variables.")

    # Initialize Extensions
    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)
    CORS(app)

    # Setup Databases
    setup_db()
    initialize_postgres_tables()
    initialize_mongo_collections()

    # register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chat_bp, url_prefix='/chat')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
