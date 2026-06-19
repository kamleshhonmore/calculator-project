# =====================================================================
#             CALCULATOR BACKEND: HTTP API SERVER & SQL DATABASE
# =====================================================================
# This file acts as the server ("the chef"). It does two things:
# 1. Manages a SQLite database to remember previous calculations.
# 2. Listens for HTTP web requests from our GUI client, calculates
#    the math, saves it to the database, and returns the result.
#
# No packages (like Flask or Django) are needed. This uses only
# Python's built-in libraries.

import http.server  # Built-in library to create a basic web server
import json         # Built-in library to format data as JSON
import sqlite3      # Built-in library to interact with SQLite databases
import datetime     # Built-in library to handle dates and times
import re           # Built-in library for regular expressions
import math         # Built-in library for scientific math calculations

PORT = 5000         # The port number our server will run on (http://localhost:5000)


def get_error_name(exception):
    """
    Returns a friendly string name for the exception (e.g. "Zero Division Error").
    This helps translate cryptic system tracebacks into user-friendly messages.
    """
    # Check if the error is a division-by-zero (e.g. 5/0)
    if isinstance(exception, ZeroDivisionError):
        return "Zero Division Error"  # Return division by zero error string
    # Check if the error is syntax-related (e.g. missing brackets or bad characters)
    elif isinstance(exception, SyntaxError):
        return "Syntax Error"  # Return syntax error string
    # Check if the error is due to an unknown variable/name
    elif isinstance(exception, NameError):
        return "Name Error"  # Return name error string
    # Check if the error is due to mismatched data types (e.g. adding letters to numbers)
    elif isinstance(exception, TypeError):
        return "Type Error"  # Return type error string
    # Check if the error is due to an invalid mathematical value (e.g. square root of a negative number)
    elif isinstance(exception, ValueError):
        return "Value Error"  # Return value error string
    else:
        # Get the actual class name of the exception object (e.g., "AttributeError")
        name = type(exception).__name__
        # Use regex to insert spaces before capital letters (e.g., "AttributeError" -> "Attribute Error")
        friendly_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
        # Return the friendly name if it ends with "Error", else append " Error"
        return friendly_name if friendly_name.endswith("Error") else f"{friendly_name} Error"


def sanitize_expression(expr):
    """
    Sanitizes the mathematical expression:
    1. Rejects empty parentheses '()' as a Syntax Error.
    2. Maps visual symbols to Python equivalents (π -> pi, √ -> sqrt, ^ -> **, x% -> x/100).
    3. Rewrites integers with leading zeros (e.g., '0999' -> '999') so Python can evaluate them.
    """
    # Check for empty brackets '()' which cause errors in math evaluation
    if re.search(r'\(\s*\)', expr):
        raise SyntaxError("Empty parentheses are not mathematically valid.")  # Raise a syntax error
    
    # Map display characters clicked on the GUI screen to Python's math keywords
    expr = expr.replace('π', 'pi')       # Map pi character to variable 'pi'
    expr = expr.replace('√', 'sqrt')     # Map square root to function 'sqrt'
    expr = expr.replace('^', '**')       # Map power symbol to Python power operator '**'
    
    # Replace percentage symbol following a number with /100 (e.g., 50% -> 50/100)
    # The regex looks for digits, remembers them, and appends /100.
    expr = re.sub(r'(\d+(?:\.\d+)?)%', r'\1/100', expr)
    
    # Replace leading zeros on digits (excluding decimals).
    # In Python, numbers like '09' throw a SyntaxError. We clean them to '9'.
    expr = re.sub(r'\b0+(\d+)(?!\.)', r'\1', expr)
    
    return expr  # Return the fully cleaned mathematical expression string


# ---------------------------------------------------------------------
# PART 1: DATABASE INITIALIZATION
# ---------------------------------------------------------------------
def init_database():
    """
    Creates the SQLite database file and a 'history' table if they don't exist.
    """
    # Connect to (or create) a local file called 'calculator.db'
    connection = sqlite3.connect("calculator.db", check_same_thread=False)
    
    # Create a cursor object, which is used to run SQL commands
    cursor = connection.cursor()
    
    # Run the SQL command to create our 'history' table if it does not exist yet.
    # The table has columns: id (unique key), equation, answer, and a timestamp.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equation TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Commit (save) the changes to the database file
    connection.commit()
    # Close the database connection to release the file lock
    connection.close()
    # Print status message
    print("Database initialized successfully (calculator.db).")


# ---------------------------------------------------------------------
# PART 2: HANDLING API REQUESTS (GET and POST)
# ---------------------------------------------------------------------
class CalculatorAPIHandler(http.server.BaseHTTPRequestHandler):
    """
    This class handles the incoming HTTP requests from the GUI client.
    It automatically routes GET and POST requests based on request paths.
    """
    
    def do_POST(self):
        """
        Handles POST requests (used for sending new data, e.g. calculating a math expression).
        Route: http://localhost:5000/calculate
        """
        # Route check: make sure the client is calling '/calculate'
        if self.path == "/calculate":
            # Read the Content-Length header to find the size of the incoming data in bytes
            content_length = int(self.headers['Content-Length'])
            
            # Read the raw byte data sent by the GUI client
            raw_post_data = self.rfile.read(content_length)
            
            expression = ""
            try:
                # Decode the binary bytes to string and parse as a JSON dictionary
                data = json.loads(raw_post_data.decode('utf-8'))
                # Extract the math expression string from the dictionary
                expression = data.get("expression", "")
                # Extract the angle mode setting (DEG or RAD)
                angle_mode = data.get("angle_mode", "DEG")
                
                # Sanitize the expression (converts visual symbols, leading zeros, etc.)
                sanitized_expr = sanitize_expression(expression)
                
                # Define mathematical constants and functions based on angle mode
                # This also acts as a security lock, allowing ONLY these functions to be evaluated.
                is_deg = (angle_mode == "DEG")  # Check if angle mode is Degrees
                eval_globals = {
                    # If in DEG mode, convert input to radians first, else calculate directly
                    'sin': lambda x: math.sin(math.radians(x)) if is_deg else math.sin(x),
                    'cos': lambda x: math.cos(math.radians(x)) if is_deg else math.cos(x),
                    'tan': lambda x: math.tan(math.radians(x)) if is_deg else math.tan(x),
                    'sqrt': math.sqrt,        # Square root function mapping
                    'ln': math.log,          # Natural logarithm function mapping
                    'log': math.log10,       # Base-10 logarithm function mapping
                    'pi': math.pi,           # Math constant Pi (3.14159...)
                    'e': math.e,             # Math constant Euler's number (2.71828...)
                    'fact': math.factorial,  # Factorial function mapping
                    'abs': abs,              # Absolute value function mapping
                }
                
                # Perform the mathematical calculation in a restricted environment.
                # passing {"__builtins__": None} blocks access to dangerous system functions.
                calculation_result = eval(sanitized_expr, {"__builtins__": None}, eval_globals)
                
                # Round to 12 decimal places to resolve float representation issues
                if isinstance(calculation_result, (int, float)):
                    calculation_result = round(calculation_result, 12)  # Round calculation result
                    # Convert floats to integers if possible (e.g. 5.0 becomes 5)
                    if isinstance(calculation_result, float) and calculation_result.is_integer():
                        calculation_result = int(calculation_result)  # Cast float to integer
                
                # Convert the final result to a string representation
                result_str = str(calculation_result)
                
                # Save the expression and result into the SQLite database with local time
                local_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get local time
                connection = sqlite3.connect("calculator.db", check_same_thread=False)  # Connect to database
                cursor = connection.cursor()  # Create cursor
                cursor.execute(
                    "INSERT INTO history (equation, answer, timestamp) VALUES (?, ?, ?)",
                    (expression, result_str, local_time)
                )  # Run SQL insert statement
                connection.commit()  # Save changes
                connection.close()  # Close connection
                
                # Prepare success response message dictionary
                response = {"status": "success", "result": result_str}
                # Send the response back with an HTTP 200 (OK) status code
                self.send_json_response(200, response)
                
            except ZeroDivisionError:
                # If they divide by zero (e.g., "5/0"), save the error log to the database and return it
                error_name = "Zero Division Error"  # Set error name string
                local_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get local time
                
                connection = sqlite3.connect("calculator.db", check_same_thread=False)  # Connect to database
                cursor = connection.cursor()  # Create cursor
                cursor.execute(
                    "INSERT INTO history (equation, answer, timestamp) VALUES (?, ?, ?)",
                    (expression, error_name, local_time)
                )  # Run SQL insert statement
                connection.commit()  # Save changes
                connection.close()  # Close connection
                
                # Send back the error result to the GUI client
                self.send_json_response(200, {"status": "error", "result": error_name})
                
            except Exception as e:
                # If they enter invalid math, convert the exception to a friendly name, log it, and return
                error_name = get_error_name(e)  # Get friendly error name string
                local_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get local time
                
                connection = sqlite3.connect("calculator.db", check_same_thread=False)  # Connect to database
                cursor = connection.cursor()  # Create cursor
                cursor.execute(
                    "INSERT INTO history (equation, answer, timestamp) VALUES (?, ?, ?)",
                    (expression, error_name, local_time)
                )  # Run SQL insert statement
                connection.commit()  # Save changes
                connection.close()  # Close connection
                
                # Send back the error result to the GUI client
                self.send_json_response(200, {"status": "error", "result": error_name})
        else:
            # If the GUI client requests a path that doesn't exist, send a 404 (Not Found)
            self.send_json_response(404, {"error": "Not Found"})

    def do_GET(self):
        """
        Handles GET requests (used for fetching data, e.g. getting calculation history).
        Route: http://localhost:5000/history
        """
        # Route check: make sure the client is calling '/history'
        if self.path == "/history":
            try:
                # Fetch the last 10 calculations from the SQLite database
                connection = sqlite3.connect("calculator.db", check_same_thread=False)  # Connect to database
                cursor = connection.cursor()  # Create database cursor
                # Query history sorted from newest to oldest, limit to 10
                cursor.execute("SELECT equation, answer FROM history ORDER BY id DESC LIMIT 10")  # Run SQL select
                rows = cursor.fetchall()  # Fetch all matching rows
                connection.close()  # Close connection
                
                # Format the rows into a clean list of strings (e.g., ["5+3 = 8", "10/2 = 5"])
                history_list = []  # Initialize empty list
                for equation, answer in rows:
                    history_list.append(f"{equation} = {answer}")  # Format and append
                
                # Send the history list back to the GUI client with an HTTP 200 (OK)
                self.send_json_response(200, {"status": "success", "history": history_list})
                
            except Exception as e:
                # Send a 500 server error response back if the database read fails
                self.send_json_response(500, {"status": "error", "message": str(e)})
        else:
            # Send a 404 Not Found response if path is incorrect
            self.send_json_response(404, {"error": "Not Found"})

    def send_json_response(self, status_code, data_dict):
        """Helper function to send JSON data back to the GUI."""
        self.send_response(status_code)  # Send HTTP status code header
        # Inform the client we are returning JSON data
        self.send_header("Content-Type", "application/json")  # Set headers content type
        self.end_headers()  # Complete headers section
        # Convert dictionary to JSON string and send it down the output stream
        self.wfile.write(json.dumps(data_dict).encode('utf-8'))  # Send response bytes

    def log_message(self, format, *args):
        """Overrides default log_message to keep terminal output clean."""
        # This prevents the terminal from getting cluttered with default server logs.
        pass


# ---------------------------------------------------------------------
# PART 3: RUNNING THE SERVER
# ---------------------------------------------------------------------
# This block runs ONLY when server.py is executed directly, not when imported.
if __name__ == "__main__":
    # Initialize the database file and table
    init_database()  # Call database init function
    
    # Configure the server address and port (empty string '' binds to all local network adapters)
    server_address = ('', PORT)  # Define address tuple
    # Start the server as a ThreadingHTTPServer for multi-threaded handling
    api_server = http.server.ThreadingHTTPServer(server_address, CalculatorAPIHandler)  # Create server instance
    
    # Print status logs
    print(f"\nAPI Server is successfully running at http://localhost:{PORT}")
    print("Press Ctrl+C in this terminal window to stop the server.")
    
    # Start the server loop to keep listening for requests
    try:
        api_server.serve_forever()  # Run server loop forever
    except KeyboardInterrupt:
        print("\nStopping API Server. Goodbye!")
        api_server.server_close()  # Stop and close server socket
