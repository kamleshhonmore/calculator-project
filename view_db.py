# =====================================================================
#             DATABASE HISTORY VIEWER UTILITY (view_db.py)
# =====================================================================
# This utility script connects to our SQLite database ("calculator.db")
# and prints out every saved calculation in a neat, human-readable table.
# It is used for verifying and debugging what the server has saved.

import sqlite3  # Import Python's built-in SQLite database library

try:
    # 1. Connect to the SQLite database file named "calculator.db"
    # If the file does not exist, this will throw an error.
    connection = sqlite3.connect("calculator.db")
    
    # 2. Create a "cursor" object. The cursor is like a pointer/pointer-hand
    # that allows us to run SQL queries and fetch the results.
    cursor = connection.cursor()
    
    # 3. Execute an SQL query to select all columns (id, equation, answer, timestamp)
    # from the "history" table, sorted from oldest to newest (id ASC).
    cursor.execute("SELECT id, equation, answer, timestamp FROM history ORDER BY id ASC")
    
    # 4. Fetch all the matching rows from the query and store them in a Python list.
    rows = cursor.fetchall()
    
    # 5. Print the top header lines to make the console output look clean.
    print("\n" + "=" * 70)
    print("                      ALL CALCULATOR HISTORY")
    print("=" * 70)
    print(f"Total calculations stored: {len(rows)}\n")
    
    # 6. Print the column headers, aligned nicely.
    # '<5' means left-aligned in a column 5 characters wide.
    # '<20' means left-aligned in a column 20 characters wide, etc.
    print(f"{'ID':<5} | {'Equation':<20} | {'Answer':<15} | {'Saved At (Local)'}")
    print("-" * 70)
    
    # 7. Loop through each row of database results and print them.
    for row in rows:
        db_id = row[0]       # Column 0: The auto-incremented database ID
        equation = row[1]    # Column 1: The mathematical formula (e.g. "5+5")
        answer = row[2]      # Column 2: The calculated result (e.g. "10")
        timestamp = row[3]   # Column 3: The system local time when saved
        
        # Print this row aligned to the exact same column widths as the header
        print(f"{db_id:<5} | {equation:<20} | {answer:<15} | {timestamp}")
        
    print("=" * 70 + "\n")
    
    # 8. Close the connection to release the file lock on "calculator.db"
    connection.close()

except sqlite3.OperationalError:
    # This block triggers if "calculator.db" doesn't exist yet
    # (i.e., if the server has never been run).
    print("\n[!] Database file 'calculator.db' not found. Please run the server first!")
