# =====================================================================
#             CALCULATOR BACKEND: HTTP API SERVER & SQL DATABASE
# =====================================================================
# This file acts as the server ("the chef"). It does routing and handles
# HTTP requests by delegating database tasks and math operations to
# separate modules.

import http.server
import json
import os
import database
import math_engine

PORT = int(os.getenv("PORT", 5000))

class CalculatorAPIHandler(http.server.BaseHTTPRequestHandler):
    """
    Handles incoming HTTP requests from the GUI client.
    Delegates database operations to database.py and calculations to math_engine.py.
    """
    
    def do_POST(self):
        """
        Handles POST requests (calculating expressions).
        Route: http://localhost:5000/calculate
        """
        if self.path == "/calculate":
            content_length = int(self.headers['Content-Length'])
            raw_post_data = self.rfile.read(content_length)
            
            expression = ""
            try:
                data = json.loads(raw_post_data.decode('utf-8'))
                expression = data.get("expression", "")
                angle_mode = data.get("angle_mode", "DEG")
                
                # Perform calculation using the math engine
                result_str = math_engine.evaluate_math(expression, angle_mode)
                
                # Save result in database
                database.save_calculation(expression, result_str)
                
                response = {"status": "success", "result": result_str}
                self.send_json_response(200, response)
                
            except Exception as e:
                # Convert exception to friendly name and save log to DB
                error_name = math_engine.get_error_name(e)
                database.save_calculation(expression, error_name)
                
                self.send_json_response(200, {"status": "error", "result": error_name})
        else:
            self.send_json_response(404, {"error": "Not Found"})

    def do_GET(self):
        """
        Handles GET requests (fetching calculation history).
        Route: http://localhost:5000/history
        """
        if self.path == "/history":
            try:
                history_list = database.get_recent_history(10)
                self.send_json_response(200, {"status": "success", "history": history_list})
            except Exception as e:
                self.send_json_response(500, {"status": "error", "message": str(e)})
        else:
            self.send_json_response(404, {"error": "Not Found"})

    def send_json_response(self, status_code, data_dict):
        """Helper function to send JSON responses."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data_dict).encode('utf-8'))

    def log_message(self, format, *args):
        """Overrides default log_message to keep terminal output clean."""
        pass

if __name__ == "__main__":
    # Initialize SQLite database through the database module
    database.init_database()
    
    server_address = ('', PORT)
    api_server = http.server.ThreadingHTTPServer(server_address, CalculatorAPIHandler)
    
    print(f"\nAPI Server is successfully running at http://localhost:{PORT}")
    print("Press Ctrl+C in this terminal window to stop the server.")
    
    try:
        api_server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping API Server. Goodbye!")
        api_server.server_close()
