from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_jwt_extended import get_jwt
from pymongo import MongoClient
import openai
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
from db import get_postgres_connection, return_postgres_connection

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Flask Blueprint
chat_bp = Blueprint('chat', __name__)

# MongoDB connection
try:
    client = MongoClient(os.getenv('MONGO_URI'))
    mongo_db = client['chatbot_db']
    chat_collection = mongo_db['chat_logs']
    logger.info("Connected to MongoDB.")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")

# OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

@chat_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask():
    data = request.get_json()
    question = data.get('question', '').strip().lower()

    if not question:
        return jsonify({"error": "Question cannot be empty."}), 400

    try:
        # Connect to the database
        conn = get_postgres_connection()
        cursor = conn.cursor()

        # Fetch the response from the database
        cursor.execute("SELECT answer FROM responses WHERE question = %s", (question,))
        result = cursor.fetchone()

        if result:
            answer = result[0]
        else:
            answer = "I'm sorry, I don't have an answer to that."

        # Close the database connection
        cursor.close()
        return_postgres_connection(conn)

        # Return the response
        return jsonify({"answer": answer}), 200

    except Exception as e:
        print(f"Error during chatbot query: {e}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500