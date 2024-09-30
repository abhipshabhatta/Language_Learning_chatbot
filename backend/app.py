from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Load configurations
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Extensions
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)  # Enable CORS to allow requests from frontend

# MongoDB Setup
client = MongoClient(os.getenv('MONGO_URI'))
mongo_db = client['chatbot_db']
users_collection = mongo_db['users']

#Signup
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

    # Check if user already exists
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Save user to MongoDB
    new_user = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": hashed_password
    }
    user_id = users_collection.insert_one(new_user).inserted_id

    # Generate access token
    access_token = create_access_token(identity=str(user_id))

    return jsonify({
        "message": "User created successfully",
        "access_token": access_token
    }), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)
