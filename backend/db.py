import os
import psycopg2
from psycopg2 import pool
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL connection pool
pg_pool = None

# MongoDB client setup
client = None
mongo_db = None

def setup_db():
    """
    Initialize both PostgreSQL and MongoDB connections.
    """
    global pg_pool, client, mongo_db

    # Setup PostgreSQL connection pool
    pg_database_url = os.getenv('DATABASE_URL')  # PostgreSQL connection URL
    if not pg_database_url:
        raise Exception("DATABASE_URL is not set in environment variables.")
    
    try:
        pg_pool = psycopg2.pool.SimpleConnectionPool(1, 20, pg_database_url)
        print("PostgreSQL connection pool created successfully")
    except Exception as e:
        raise Exception(f"Error while creating PostgreSQL connection pool: {e}")

    # Setup MongoDB connection
    mongo_uri = os.getenv('MONGO_URI')  # MongoDB connection string
    if not mongo_uri:
        raise Exception("MONGO_URI is not set in environment variables.")

    try:
        client = MongoClient(mongo_uri)
        mongo_db = client['chatbot_db']
        print("MongoDB connection established successfully")
    except Exception as e:
        raise Exception(f"Error while connecting to MongoDB: {e}")

def get_postgres_connection():
    if not pg_pool:
        raise Exception("PostgreSQL pool has not been initialized. Call setup_db first.")
    return pg_pool.getconn()

def return_postgres_connection(conn):
    if pg_pool and conn:
        pg_pool.putconn(conn)

def get_mongo_db():
    if mongo_db is None:
        raise Exception("MongoDB has not been initialized. Call setup_db first.")
    return mongo_db


def initialize_mongo_collections():
    if not mongo_db:
        raise Exception("MongoDB has not been initialized. Call setup_db first.")
    
    chat_collection = mongo_db['chat_logs']
    users_collection = mongo_db['users']

    chat_collection.create_index("question")
    users_collection.create_index("email", unique=True)

    print("MongoDB collections initialized successfully")

def initialize_postgres_tables():
    conn = get_postgres_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        cursor.close()
        print("PostgreSQL tables initialized successfully")
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error while initializing PostgreSQL tables: {e}")
    finally:
        return_postgres_connection(conn)
