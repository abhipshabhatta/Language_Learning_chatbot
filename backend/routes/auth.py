from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt, check_password_hash
from db import get_postgres_connection, return_postgres_connection
import re

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# Password validation function
def is_password_valid(password):
    # At least one uppercase, one lowercase, one number, one special character, and min length of 8
    return re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$', password)

# Signup Endpoint
@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        from db import get_postgres_connection 

        data = request.get_json()
        print("Received signup data:", data)  # Log the incoming request data

        if not data or not 'username' in data or not 'password' in data:
            return jsonify({"message": "Invalid request data"}), 400

        username = data['username']
        password = data['password']

        # Check if user already exists in PostgreSQL
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        print("User lookup result:", user)  # Log the lookup result

        if user:
            return jsonify({"message": "User already exists"}), 400

        # Hash password and create a new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()
        print("User created successfully")  # Log success

        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        print(f"Error during signup: {e}")  # Log the exception
        return jsonify({"message": "Internal server error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            return_postgres_connection(conn)


# Signin Endpoint
@auth_bp.route('/signin', methods=['POST'])
def signin():
    from db import get_postgres_connection 

    data = request.get_json()
    username = data.get('username') 
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            stored_password = user[1]
            if bcrypt.check_password_hash(stored_password, password):  # Validate password
                access_token = create_access_token(identity=username)
                return jsonify({"token": access_token}), 200
            else:
                print("Invalid password")  # Debugging log
                return jsonify({"message": "Invalid credentials"}), 401

        print("User not found")  # Debugging log
        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Error during signin: {e}")  # Debugging log
        return jsonify({"message": "Internal server error"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            return_postgres_connection(conn)
