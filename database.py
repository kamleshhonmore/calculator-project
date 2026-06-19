import os
import psycopg2
from dotenv import load_dotenv

# Load the environment variables from the local .env file
load_dotenv()

# Get the database connection URL
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """
    Creates and returns a connection to the PostgreSQL database.
    """
    return psycopg2.connect(DATABASE_URL)

def init_database():
    """
    Creates the PostgreSQL 'history' table if it does not exist yet.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    # In PostgreSQL, we use SERIAL PRIMARY KEY instead of AUTOINCREMENT
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id SERIAL PRIMARY KEY,
            equation TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()
    print("Cloud PostgreSQL Database initialized successfully.")

def save_calculation(expression, answer):
    """
    Saves an equation and its result to the cloud PostgreSQL database.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    # In PostgreSQL, psycopg2 uses '%s' as the query parameter placeholder instead of '?'
    cursor.execute(
        "INSERT INTO history (equation, answer) VALUES (%s, %s)",
        (expression, answer)
    )
    connection.commit()
    cursor.close()
    connection.close()

def get_recent_history(limit=10):
    """
    Fetches the most recent calculations from the cloud PostgreSQL database.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    # Query history sorted from newest to oldest, limit to the requested amount
    cursor.execute("SELECT equation, answer FROM history ORDER BY id DESC LIMIT %s", (limit,))
    rows = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    history_list = []
    for equation, answer in rows:
        history_list.append(f"{equation} = {answer}")
    return history_list
