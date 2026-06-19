# =====================================================================
#             CALCULATOR FRONTEND: GUI WINDOW CLIENT (client.py)
# =====================================================================
# This file acts as the GUI client ("the waiter"). It does two things:
# 1. Shows a graphical calculator and a history sidebar to the user.
# 2. Sends HTTP API requests to the API Server (server.py) to calculate
#    math and to retrieve history logs.
#
# No external packages (like requests) are needed. This uses only
# Python's built-in libraries (tkinter and urllib).

import os  # Import the OS library to modify system/network settings
# Force Python to completely ignore proxy configuration for localhost/127.0.0.1
# (Vital for Zscaler/corporate networks to prevent network interception of local requests)
os.environ['no_proxy'] = 'localhost,127.0.0.1,127.0.0.1:5000,localhost:5000'  # Disable lowercase proxy env
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,127.0.0.1:5000,localhost:5000'  # Disable uppercase proxy env

import tkinter as tk  # Import Python's built-in GUI library and name it 'tk'
from tkinter import messagebox  # Import pop-up box component from tkinter
import urllib.request   # Built-in library to send web/HTTP requests
import urllib.error     # Built-in library to handle network/connection errors
import json             # Built-in library to parse and encode JSON data

# Disable system proxy settings for localhost (vital for Zscaler/corporate networks)
# We hand Python a blank dictionary '{}' to force it to connect directly.
proxy_handler = urllib.request.ProxyHandler({})  # Set proxy handler with empty dictionary
opener = urllib.request.build_opener(proxy_handler)  # Build request opener using empty proxy settings
urllib.request.install_opener(opener)  # Install this opener as the default for urllib

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------
API_URL = "http://127.0.0.1:5000"   # The URL of our API server (using IP directly to bypass DNS issues)

# Design Palette (Sky Blue Casio Theme)
WINDOW_BG = "#0a1d37"          # Dark steel blue casing background color
PANEL_BG = "#11223b"           # Bezel slate blue card background color
TEXT_COLOR = "#ffffff"         # Main white text color
TEXT_MUTED = "#93c5fd"         # Muted sky-blue text color

NUM_BG = "#e0f2fe"             # Light sky-blue for numeric keypad (0-9, decimal)
OP_BG = "#38bdf8"              # Sky-blue for operator keys (+, -, *, /, =)
SPECIAL_BG = "#ef4444"         # Vibrant red for C and backspace (like Casio DEL/AC)
SCI_BG = "#1b3b5f"             # Medium navy for scientific keys (sin, cos, log, etc.)
FONT_NAME = "Segoe UI"         # Sleek, modern font family name

expression = ""                # Global string that holds the math typing (e.g. "5+3")
angle_mode = "DEG"             # Stores the current angle mode ("DEG" or "RAD")

# ---------------------------------------------------------------------
# PART 1: HTTP API COMMUNICATIONS (Connecting to the Server)
# ---------------------------------------------------------------------

def send_calculation_request(math_expr):
    """
    Sends the math equation to the API server via an HTTP POST request.
    Returns the calculated result string.
    """
    global angle_mode  # Tell Python to use the global angle_mode variable
    url = f"{API_URL}/calculate"  # Create the final destination endpoint URL
    
    # 1. Package the equation and angle mode into a dictionary, then translate it to JSON bytes
    payload = {"expression": math_expr, "angle_mode": angle_mode}  # Create payload dictionary
    json_data = json.dumps(payload).encode('utf-8')  # Dump dict to string and encode to binary bytes
    
    # 2. Setup the request details (Destination URL, Body data, and JSON Header)
    request = urllib.request.Request(
        url,                          # Destination server URL address
        data=json_data,               # Payload data containing calculation info
        headers={'Content-Type': 'application/json'},  # HTTP headers telling server it's JSON data
        method='POST'                 # Request type is POST
    )
    
    try:
        # 3. Open connection with a 2-second timeout (prevents GUI from freezing if server is offline)
        with urllib.request.urlopen(request, timeout=2) as response:
            # Decode the reply bytes to text, and parse it back into a Python dictionary
            response_json = json.loads(response.read().decode('utf-8'))  # Read and parse JSON bytes
            return response_json.get("result", "Error")  # Return result value, default to "Error"
            
    except Exception as e:
        # If the server is offline or fails, print debug log and return standard status
        print(f"DEBUG - Calculation request failed: {e}")  # Print failure message
        import traceback
        traceback.print_exc()  # Print details of trace stack
        return "Server Offline"  # Return offline status string


def fetch_history_request():
    """
    Fetches the last 10 calculations from the API server via an HTTP GET request.
    Returns a list of calculation strings.
    """
    url = f"{API_URL}/history"  # Create target URL path for fetching logs
    
    try:
        # Open connection and fetch calculation history logs
        with urllib.request.urlopen(url, timeout=2) as response:
            response_json = json.loads(response.read().decode('utf-8'))  # Parse JSON bytes
            return response_json.get("history", [])  # Grab history list, default to empty list
            
    except Exception as e:
        # If server is offline, print traceback and return error placeholder
        print(f"DEBUG - History request failed: {e}")  # Print error log
        import traceback
        traceback.print_exc()  # Print call stack
        return ["Server Offline"]  # Return error status array


# ---------------------------------------------------------------------
# PART 2: GUI INTERACTION LOGIC
# ---------------------------------------------------------------------

def press(character):
    """Appends characters or expressions to the equation screen."""
    global expression  # Use the global expression variable
    
    # 1. Map special GUI labels to computer math notation
    if character == "x²":
        expression = expression + "^2"  # Append power of two symbol
    elif character == "1/x":
        if expression == "" or expression == "0":
            expression = "1/("  # Start division syntax
        else:
            expression = f"1/({expression})"  # Enclose current expression in division bracket
    elif character == "10ˣ":
        expression = expression + "10^("  # Append base-10 power syntax
    elif character in ["sin", "cos", "tan", "ln", "log", "fact", "abs"]:
        # Standard scientific functions append with an opening bracket (e.g. "sin(")
        if expression == "0":
            expression = f"{character}("  # Replace starting zero with function name
        else:
            expression = expression + f"{character}("  # Append function name to expression
    else:
        # If starting fresh and typing an operator, prefix with "0" (e.g. "+ 5" becomes "0+5")
        if expression == "" and character in ["+", "*", "/"]:
            expression = "0" + str(character)  # Prefix operator with zero
        else:
            expression = expression + str(character)  # Append character directly
            
    # Update the visual screen variable
    equation_text.set(expression)  # Update screen text string


def calculate():
    """Sends the expression to the API server and displays the answer."""
    global expression  # Use the global expression variable
    
    # If the screen is empty, do nothing
    if expression == "":
        return  # Exit function
        
    # Send the math expression to our server to compute and save it
    result = send_calculation_request(expression)  # Query server calculation API
    
    # Update the calculator screen with the returned result
    equation_text.set(result)  # Set visual screen text
    
    # If calculation was successful, store the result so the user can calculate further
    if "Error" not in result and result != "Server Offline":
        expression = result  # Set expression to calculation result
    else:
        # Reset if an error occurred
        expression = ""  # Clear expression memory
        
    # Refresh the history sidebar on the right to show this new calculation
    update_history_sidebar()  # Call history refresh function


def clear():
    """Resets the calculator input to empty."""
    global expression  # Use the global expression variable
    expression = ""  # Empty string in memory
    equation_text.set("0")  # Set screen to show "0"


def backspace():
    """Removes the last character on the screen (DEL key functionality)."""
    global expression  # Use the global expression variable
    # Slice the string to remove the last character
    expression = expression[:-1]  # Take all characters except the last one
    if expression == "":
        equation_text.set("0")  # If screen becomes empty, show "0"
    else:
        equation_text.set(expression)  # Update screen with remainder string


def update_history_sidebar():
    """Fetches the history log from the server and updates the sidebar listbox."""
    # 1. Get the list of equations from the server
    history_items = fetch_history_request()  # Query server history API
    
    # 2. Clear the existing items in the visual sidebar listbox
    history_listbox.delete(0, tk.END)  # Clear all values from index 0 to end
    
    # 3. Add each item from the history list to the listbox
    for item in history_items:
        history_listbox.insert(tk.END, item)  # Insert at the end of the listbox


# ---------------------------------------------------------------------
# PART 3: MAIN GUI LAYOUT (Tkinter)
# ---------------------------------------------------------------------

# Create the main window window
root = tk.Tk()  # Instantiate Tkinter root window
root.title("Scientific Calculator Client")  # Set window title
root.geometry("770x520")             # Wider window to fit scientific layout + sidebar
root.configure(bg=WINDOW_BG)         # Apply deep blue casing background color
root.resizable(False, False)         # Lock resizing to keep layout perfect

# Divide the window into LEFT (Calculator) and RIGHT (History Sidebar)
calculator_frame = tk.Frame(root, bg=WINDOW_BG, width=540)  # Left frame container
calculator_frame.pack(side="left", fill="both", expand=True, padx=(15, 5), pady=15)  # Pack left frame

history_frame = tk.Frame(root, bg=PANEL_BG, width=210)  # Right frame container
history_frame.pack(side="right", fill="both", padx=(5, 15), pady=15)  # Pack right frame

# --- A. CALCULATOR LEFT PANEL ---

# StringVar to update the calculator screen dynamically
equation_text = tk.StringVar()  # Link variable
equation_text.set("0")  # Start screen display at "0"

# Screen Bezel (Recessed bezel like a physical calculator)
screen_bezel = tk.Frame(calculator_frame, bg="#112233", bd=3, relief="sunken")  # Create screen frame border
screen_bezel.pack(fill="x", pady=(0, 10))  # Pack screen frame

# LCD Screen inside the bezel (soft blue-green backlight color)
lcd_screen = tk.Frame(screen_bezel, bg="#c2e9fb", padx=12, pady=10)  # Create screen inner background
lcd_screen.pack(fill="x")  # Pack screen inner frame

# Top LCD Row (shows RAD/DEG mode indicators)
lcd_top_row = tk.Frame(lcd_screen, bg="#c2e9fb")  # Create top row container
lcd_top_row.pack(fill="x")  # Pack top row frame

# DEG/RAD status text indicator label
lcd_indicator = tk.Label(
    lcd_top_row,
    text="DEG",                       # Initial display string
    bg="#c2e9fb",                     # Matching background
    fg="#0a1d37",                     # Dark blue text
    font=("Consolas", 10, "bold")     # Digital font style
)
lcd_indicator.pack(side="right")  # Pack label on the right

# Bottom LCD Row (main digit screen)
lcd_main = tk.Label(
    lcd_screen,
    textvariable=equation_text,       # Link to equation text variable
    anchor="e",                       # Right align digits
    bg="#c2e9fb",                     # Matching background
    fg="#0a1d37",                     # Dark blue text
    font=("Courier New", 26, "bold"), # Digital Courier font
    height=2                          # Display height
)
lcd_main.pack(fill="x")  # Pack main label

# Mode Status Frame (casing design for the toggle button)
mode_frame = tk.Frame(calculator_frame, bg=WINDOW_BG)  # Create casing frame container
mode_frame.pack(fill="x", pady=(0, 8))  # Pack casing frame

# Angle mode description text label
mode_label = tk.Label(
    mode_frame,
    text="ANGLE MODE CONTROL:",        # Description label string
    bg=WINDOW_BG,                     # Casing background
    fg=TEXT_MUTED,                    # Muted light blue text
    font=(FONT_NAME, 9, "bold")       # Font properties
)
mode_label.pack(side="left", padx=5)  # Pack description on the left

def toggle_mode():
    """Switches the angle calculation mode between DEG and RAD."""
    global angle_mode  # Use global variable
    if angle_mode == "DEG":
        angle_mode = "RAD"  # Toggle to RAD
    else:
        angle_mode = "DEG"  # Toggle to DEG
    # Update LCD screen indicator and button text labels
    lcd_indicator.config(text=angle_mode)  # Update indicator label
    toggle_btn.config(text="Switch to DEG" if angle_mode == "RAD" else "Switch to RAD")  # Update toggle button label

# Toggle Button
toggle_btn = tk.Button(
    mode_frame,
    text="Switch to RAD",              # Initial text
    bg=SCI_BG,                        # Scientific dark blue background
    fg=TEXT_COLOR,                    # White text
    font=(FONT_NAME, 8, "bold"),      # Font properties
    bd=0,                             # Flat borderless style
    relief="flat",                    # Flat relief
    padx=10,                          # Inner X margins
    pady=3,                           # Inner Y margins
    command=toggle_mode               # Callback function when clicked
)
toggle_btn.pack(side="right", padx=5)  # Pack button on the right

# Keyboard Keypad Container
keys_frame = tk.Frame(calculator_frame, bg=WINDOW_BG)  # Keyboard container frame
keys_frame.pack(fill="both", expand=True)  # Pack container frame

# Grid row/col weights (7 columns x 5 rows)
for r in range(5):
    keys_frame.rowconfigure(r, weight=1)  # Allow row r to expand vertically
for c in range(7):
    keys_frame.columnconfigure(c, weight=1)  # Allow column c to expand horizontally

# Helper function for mouse hover light-up animations
def bind_hover(btn, hover_bg, normal_bg):
    # Bind mouse hover enter event (starts hover highlights)
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    # Bind mouse hover leave event (restores normal background)
    btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))

# Helper function to generate styled grid buttons
def create_button(text, row, col, bg_color, command_func):
    # Determine custom text color and hover highlights depending on category
    if bg_color == SCI_BG:
        hover_color = "#2a527c"        # Muted sky blue hover highlight
        text_fg = "#ffffff"            # White text
    elif bg_color == NUM_BG:
        hover_color = "#bae6fd"        # Light sky blue hover highlight
        text_fg = "#0a1d37"            # Dark blue text
    elif bg_color == OP_BG:
        hover_color = "#7dd3fc"        # Vivid sky blue hover highlight
        text_fg = "#0a1d37"            # Dark blue text
    elif bg_color == SPECIAL_BG:
        hover_color = "#f87171"        # Soft red hover highlight
        text_fg = "#ffffff"            # White text
    else:
        hover_color = bg_color
        text_fg = "#ffffff"

    # Instantiate the Tkinter Button widget
    btn = tk.Button(
        keys_frame,
        text=text,                     # Text content
        bg=bg_color,                   # Background color
        fg=text_fg,                    # Text color
        font=(FONT_NAME, 12, "bold"),  # Font properties
        bd=0,                          # Flat borderless style
        relief="flat",                 # Flat relief
        command=command_func,          # Function callback
        activebackground=hover_color,  # Active background color
        activeforeground=text_fg       # Active text color
    )
    # Put button in its grid coordinates
    btn.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
    # Bind the hover effect
    bind_hover(btn, hover_color, bg_color)

# --- KEYPAD BUTTONS (7 Columns x 5 Rows) ---

# --- Row 0 ---
create_button("sin",  0, 0, SCI_BG,     lambda: press("sin"))
create_button("cos",  0, 1, SCI_BG,     lambda: press("cos"))
create_button("tan",  0, 2, SCI_BG,     lambda: press("tan"))
create_button("C",    0, 3, SPECIAL_BG, clear)
create_button("(",    0, 4, SPECIAL_BG, lambda: press("("))
create_button(")",    0, 5, SPECIAL_BG, lambda: press(")"))
create_button("/",    0, 6, OP_BG,      lambda: press("/"))

# --- Row 1 ---
create_button("√",    1, 0, SCI_BG,     lambda: press("√"))
create_button("^",    1, 1, SCI_BG,     lambda: press("^"))
create_button("x²",   1, 2, SCI_BG,     lambda: press("x²"))
create_button("7",    1, 3, NUM_BG,     lambda: press("7"))
create_button("8",    1, 4, NUM_BG,     lambda: press("8"))
create_button("9",    1, 5, NUM_BG,     lambda: press("9"))
create_button("*",    1, 6, OP_BG,      lambda: press("*"))

# --- Row 2 ---
create_button("ln",   2, 0, SCI_BG,     lambda: press("ln"))
create_button("log",  2, 1, SCI_BG,     lambda: press("log"))
create_button("1/x",  2, 2, SCI_BG,     lambda: press("1/x"))
create_button("4",    2, 3, NUM_BG,     lambda: press("4"))
create_button("5",    2, 4, NUM_BG,     lambda: press("5"))
create_button("6",    2, 5, NUM_BG,     lambda: press("6"))
create_button("-",    2, 6, OP_BG,      lambda: press("-"))

# --- Row 3 ---
create_button("π",    3, 0, SCI_BG,     lambda: press("π"))
create_button("e",    3, 1, SCI_BG,     lambda: press("e"))
create_button("fact", 3, 2, SCI_BG,     lambda: press("fact"))
create_button("1",    3, 3, NUM_BG,     lambda: press("1"))
create_button("2",    3, 4, NUM_BG,     lambda: press("2"))
create_button("3",    3, 5, NUM_BG,     lambda: press("3"))
create_button("+",    3, 6, OP_BG,      lambda: press("+"))

# --- Row 4 ---
create_button("abs",  4, 0, SCI_BG,     lambda: press("abs"))
create_button("10\u1d6a", 4, 1, SCI_BG, lambda: press("10\u1d6a"))
create_button("%",    4, 2, SCI_BG,     lambda: press("%"))
create_button("\u232b", 4, 3, SPECIAL_BG, backspace)
create_button("0",    4, 4, NUM_BG,     lambda: press("0"))
create_button(".",    4, 5, NUM_BG,     lambda: press("."))
create_button("=",    4, 6, OP_BG,      calculate)


# --- B. HISTORY RIGHT PANEL ---

# Sidebar Title Label
history_title = tk.Label(
    history_frame,
    text="Calculation History",         # Header text
    bg=PANEL_BG,                       # Dark navy background
    fg=TEXT_MUTED,                     # Light blue muted text
    font=(FONT_NAME, 11, "bold"),      # Font properties
    pady=10                            # Top/bottom spacing
)
history_title.pack(fill="x")  # Pack header to stretch horizontally

# Listbox to show the list of previous calculations
history_listbox = tk.Listbox(
    history_frame,
    bg=PANEL_BG,                       # Slate blue background
    fg=TEXT_COLOR,                     # White text
    font=(FONT_NAME, 10, "bold"),      # Font properties
    bd=0,                              # Borderless
    highlightthickness=0,              # Remove default white outline border
    selectbackground=PANEL_BG,         # Select background
    selectforeground=TEXT_COLOR        # Select text color
)
history_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))  # Pack listbox to fill frame

# Button to refresh history manually
refresh_btn = tk.Button(
    history_frame,
    text="Refresh History",             # Button text label
    bg=SCI_BG,                          # Scientific dark blue background
    fg=TEXT_COLOR,                      # White text
    font=(FONT_NAME, 10, "bold"),       # Font properties
    bd=0,                               # Borderless
    relief="flat",                      # Flat relief
    command=update_history_sidebar      # Callback function when clicked
)
refresh_btn.pack(fill="x", padx=10, pady=10)  # Pack button to stretch horizontally

# Bind hover highlights to refresh button
bind_hover(refresh_btn, "#2a527c", SCI_BG)  # Bind hover highlight to refresh button


# ---------------------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------------------
# Print startup status logs in the command prompt console in background
print("\n--- Starting Calculator GUI Client ---")
print(f"Connecting to API Server at {API_URL}...")

# Fetch and display the history log when the application starts
update_history_sidebar()  # Populate listbox history on startup

# Check connection status to print a friendly status message in console
test_history = fetch_history_request()  # Grab history request
if test_history and test_history[0] == "Server Offline":
    print("\n[!] WARNING: Could not connect to API Server.")
    print("    Please verify that server.py is running on port 5000.")
else:
    print("\n[+] SUCCESS: Connected to API Server! History loaded successfully.")

# Start the application loop (blocks here and keeps GUI window active)
root.mainloop()  # Run Tkinter main window loop
