from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from routes.auth import auth_bp
from routes.chat import chat_bp
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from db import setup_db, get_mongo_db
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Load configurations
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Initialize database connections
setup_db()

# Extensions
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)

# MongoDB collections
mongo_db = get_mongo_db()
users_collection = mongo_db['users']

# Register the blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(chat_bp, url_prefix='/chat')

@app.route('/')
def home():
    return "Server is running!"

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    password = data.get('password')

    # Basic validation
    if not all([first_name, last_name, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": hashed_password
    }
    user_id = users_collection.insert_one(new_user).inserted_id

    access_token = create_access_token(identity=str(user_id))
    return jsonify({"message": "User created successfully", "access_token": access_token}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
