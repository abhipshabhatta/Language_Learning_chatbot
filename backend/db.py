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

# Setup PostgreSQL and MongoDB connections
def setup_db():
    global pg_pool, client, mongo_db

    # Setup PostgreSQL connection pool
    pg_database_url = os.getenv('DATABASE_URL')  # PostgreSQL connection URL
    if not pg_database_url:
        raise Exception("DATABASE_URL is not set in environment variables.")
    
    try:
        pg_pool = psycopg2.pool.SimpleConnectionPool(1, 20, pg_database_url)
        if pg_pool:
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

# getters for PostgreSQL
def get_postgres_connection():
    if not pg_pool:
        raise Exception("PostgreSQL pool has not been initialized. Call setup_db first.")
    try:
        return pg_pool.getconn()
    except Exception as e:
        raise Exception(f"Error getting connection from PostgreSQL pool: {e}")

# Put PostgreSQL connection back to the pool
def return_postgres_connection(conn):
    if pg_pool and conn:
        try:
            pg_pool.putconn(conn)
        except Exception as e:
            raise Exception(f"Error returning connection to PostgreSQL pool: {e}")

# getters for Mongo db
def get_mongo_db():
    if not mongo_db:
        raise Exception("MongoDB has not been initialized. Call setup_db first.")
    return mongo_db

def get_chat_collection():
    return mongo_db['chat_logs']

def get_users_collection():
    return mongo_db['users']
# initialize mongo db
def initialize_mongo_collections():
    if not mongo_db:
        raise Exception("MongoDB has not been initialized. Call setup_db first.")
    
    chat_collection = mongo_db['chat_logs']
    users_collection = mongo_db['users']

    # Create indexes
    chat_collection.create_index("question")
    users_collection.create_index("email", unique=True)

    print("MongoDB collections initialized successfully")

# initialize PostgreSQL tables
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
