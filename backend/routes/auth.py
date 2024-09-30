from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from models import User
from db import db
from datetime import timedelta
import re
import bcrypt as bcrypt_native

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# function for password validation
def is_password_valid(password):
    # At least one uppercase, one lowercase, one number, one special character, and min length of 8
    return re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$', password)

# Signup Endpoint
@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        from db import get_postgres_connection  # Lazy import to avoid circular import issues

        data = request.get_json()
        if not data or not 'username' in data or not 'password' in data:
            return jsonify({"message": "Invalid request data"}), 400

        username = data['username']
        password = data['password']

        # Check if user already exists in PostgreSQL
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user:
            return jsonify({"message": "User already exists"}), 400

        # Hash password and create a new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()

        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        print(f"Error during signup: {e}")
        return jsonify({"message": "Internal server error"}), 500
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/signin', methods=['POST'])
def signin():
    from db import get_postgres_connection  # Lazy import to avoid circular import issues

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            access_token = create_access_token(identity=user[1])
            return jsonify(token=access_token), 200

        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Error during signin: {e}")
        return jsonify({"message": "Internal server error"}), 500
    finally:
        cursor.close()
        conn.close()

# Token Refresh Endpoint
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user = get_jwt_identity()
        # Generate a new access token
        new_access_token = create_access_token(identity=current_user, expires_delta=timedelta(hours=1))
        return jsonify(access_token=new_access_token), 200
    except Exception as e:
        print(f"Error during token refresh: {e}")
        return jsonify({"message": "Internal server error"}), 500


# Password Reset Request Endpoint
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password_request():
    try:
        data = request.get_json()
        if not data or 'username' not in data:
            return jsonify({"message": "Invalid request data"}), 400

        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        reset_token = create_access_token(identity=user.username, expires_delta=timedelta(minutes=15))

        return jsonify({"message": "Password reset email sent", "reset_token": reset_token}), 200
    except Exception as e:
        print(f"Error during reset password request: {e}")
        return jsonify({"message": "Internal server error"}), 500


# Password Reset Endpoint
@auth_bp.route('/reset-password-confirm', methods=['POST'])
@jwt_required()
def reset_password_confirm():
    try:
        data = request.get_json()
        if not data or 'new_password' not in data:
            return jsonify({"message": "Invalid request data"}), 400

        new_password = data['new_password']

        # Validate password
        if not is_password_valid(new_password):
            return jsonify({"message": "Password must be at least 8 characters long, "
                                       "include an uppercase letter, a lowercase letter, a number, and a special character."}), 400

        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()

        if user:
            # Hash the new password
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.password = hashed_password
            db.session.commit()

            return jsonify({"message": "Password reset successfully"}), 200

        return jsonify({"message": "User not found"}), 404
    except Exception as e:
        print(f"Error during reset password confirm: {e}")
        return jsonify({"message": "Internal server error"}), 500


# Logout Endpoint
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        
        current_user = get_jwt_identity()
        return jsonify({"message": f"User {current_user} logged out successfully"}), 200
    except Exception as e:
        print(f"Error during logout: {e}")
        return jsonify({"message": "Internal server error"}), 500
