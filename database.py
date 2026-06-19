import sqlite3
import datetime

DB_FILE = "calculator.db"

def init_database():
    """
    Creates the SQLite database file and a 'history' table if they don't exist.
    """
    connection = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equation TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    connection.close()
    print("Database initialized successfully (calculator.db).")

def save_calculation(expression, answer):
    """
    Saves an equation and its result to the database with local time.
    """
    local_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    connection = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO history (equation, answer, timestamp) VALUES (?, ?, ?)",
        (expression, answer, local_time)
    )
    connection.commit()
    connection.close()

def get_recent_history(limit=10):
    """
    Fetches the most recent calculations from the database.
    """
    connection = sqlite3.connect(DB_FILE, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT equation, answer FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    connection.close()
    
    history_list = []
    for equation, answer in rows:
        history_list.append(f"{equation} = {answer}")
    return history_list
