from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
import openai
import os
from datetime import datetime
import logging

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Flask Blueprint
chat_bp = Blueprint('chat', __name__)

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
mongo_db = client['chatbot_db']
chat_collection = mongo_db['chat_logs']

# OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

@chat_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask():
    user_identity = get_jwt_identity()
    data = request.get_json()

    if not data or 'question' not in data:
        return jsonify({"error": "Invalid request. 'question' is required."}), 400

    question = data['question'].strip()

    if not question:
        return jsonify({"error": "Question cannot be empty."}), 400

    # Use OpenAI to get a response
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"You are a language learning tutor specializing in helping users learn new languages. "
                   f"Answer the user's question in a way that teaches them something new about the language they are learning. "
                   f"Provide examples, translations, grammar tips, or help with vocabulary. The user's question: {question}",
            max_tokens=150,
            temperature=0.7,
            n=1
        )

        answer = response.choices[0].text.strip()

        # Log the conversation in MongoDB
        log_entry = {
            "user_id": user_identity,
            "question": question,
            "response": answer,
            "timestamp": datetime.now()
        }
        chat_collection.insert_one(log_entry)

        return jsonify({"answer": answer}), 200

    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API error: {str(e)}")
        return jsonify({"error": "Error communicating with the AI service. Please try again later."}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500
