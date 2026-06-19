# =====================================================================
#             CALCULATOR FRONTEND: GUI WINDOW CLIENT (client.py)
# =====================================================================
# This file acts as the GUI client ("the waiter"). It shows the graphical
# calculator interface and delegates all API communication to api_client.py.

import tkinter as tk
from tkinter import messagebox
import api_client

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
# GUI INTERACTION LOGIC
# ---------------------------------------------------------------------

def press(character):
    """Appends characters or expressions to the equation screen."""
    global expression
    
    if character == "x²":
        expression = expression + "^2"
    elif character == "1/x":
        if expression == "" or expression == "0":
            expression = "1/("
        else:
            expression = f"1/({expression})"
    elif character == "10ˣ":
        expression = expression + "10^("
    elif character in ["sin", "cos", "tan", "ln", "log", "fact", "abs"]:
        if expression == "0":
            expression = f"{character}("
        else:
            expression = expression + f"{character}("
    else:
        if expression == "" and character in ["+", "*", "/"]:
            expression = "0" + str(character)
        else:
            expression = expression + str(character)
            
    equation_text.set(expression)

def calculate():
    """Sends the expression to the API server and displays the answer."""
    global expression
    
    if expression == "":
        return
        
    # Delegate API network call to api_client module
    result = api_client.send_calculation_request(expression, angle_mode)
    equation_text.set(result)
    
    if "Error" not in result and result != "Server Offline":
        expression = result
    else:
        expression = ""
        
    update_history_sidebar()

def clear():
    """Resets the calculator input to empty."""
    global expression
    expression = ""
    equation_text.set("0")

def backspace():
    """Removes the last character on the screen (DEL key functionality)."""
    global expression
    expression = expression[:-1]
    if expression == "":
        equation_text.set("0")
    else:
        equation_text.set(expression)

def update_history_sidebar():
    """Fetches history logs from api_client and updates the listbox."""
    history_items = api_client.fetch_history_request()
    history_listbox.delete(0, tk.END)
    for item in history_items:
        history_listbox.insert(tk.END, item)

# ---------------------------------------------------------------------
# MAIN GUI LAYOUT (Tkinter)
# ---------------------------------------------------------------------

root = tk.Tk()
root.title("Scientific Calculator Client")
root.geometry("770x520")
root.configure(bg=WINDOW_BG)
root.resizable(False, False)

# Divide the window into LEFT (Calculator) and RIGHT (History Sidebar)
calculator_frame = tk.Frame(root, bg=WINDOW_BG, width=540)
calculator_frame.pack(side="left", fill="both", expand=True, padx=(15, 5), pady=15)

history_frame = tk.Frame(root, bg=PANEL_BG, width=210)
history_frame.pack(side="right", fill="both", padx=(5, 15), pady=15)

# --- A. CALCULATOR LEFT PANEL ---

equation_text = tk.StringVar()
equation_text.set("0")

screen_bezel = tk.Frame(calculator_frame, bg="#112233", bd=3, relief="sunken")
screen_bezel.pack(fill="x", pady=(0, 10))

lcd_screen = tk.Frame(screen_bezel, bg="#c2e9fb", padx=12, pady=10)
lcd_screen.pack(fill="x")

lcd_top_row = tk.Frame(lcd_screen, bg="#c2e9fb")
lcd_top_row.pack(fill="x")

lcd_indicator = tk.Label(
    lcd_top_row,
    text="DEG",
    bg="#c2e9fb",
    fg="#0a1d37",
    font=("Consolas", 10, "bold")
)
lcd_indicator.pack(side="right")

lcd_main = tk.Label(
    lcd_screen,
    textvariable=equation_text,
    anchor="e",
    bg="#c2e9fb",
    fg="#0a1d37",
    font=("Courier New", 26, "bold"),
    height=2
)
lcd_main.pack(fill="x")

mode_frame = tk.Frame(calculator_frame, bg=WINDOW_BG)
mode_frame.pack(fill="x", pady=(0, 8))

mode_label = tk.Label(
    mode_frame,
    text="ANGLE MODE CONTROL:",
    bg=WINDOW_BG,
    fg=TEXT_MUTED,
    font=(FONT_NAME, 9, "bold")
)
mode_label.pack(side="left", padx=5)

def toggle_mode():
    """Switches the angle calculation mode between DEG and RAD."""
    global angle_mode
    if angle_mode == "DEG":
        angle_mode = "RAD"
    else:
        angle_mode = "DEG"
    lcd_indicator.config(text=angle_mode)
    toggle_btn.config(text="Switch to DEG" if angle_mode == "RAD" else "Switch to RAD")

toggle_btn = tk.Button(
    mode_frame,
    text="Switch to RAD",
    bg=SCI_BG,
    fg=TEXT_COLOR,
    font=(FONT_NAME, 8, "bold"),
    bd=0,
    relief="flat",
    padx=10,
    pady=3,
    command=toggle_mode
)
toggle_btn.pack(side="right", padx=5)

keys_frame = tk.Frame(calculator_frame, bg=WINDOW_BG)
keys_frame.pack(fill="both", expand=True)

for r in range(5):
    keys_frame.rowconfigure(r, weight=1)
for c in range(7):
    keys_frame.columnconfigure(c, weight=1)

def bind_hover(btn, hover_bg, normal_bg):
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))

def create_button(text, row, col, bg_color, command_func):
    if bg_color == SCI_BG:
        hover_color = "#2a527c"
        text_fg = "#ffffff"
    elif bg_color == NUM_BG:
        hover_color = "#bae6fd"
        text_fg = "#0a1d37"
    elif bg_color == OP_BG:
        hover_color = "#7dd3fc"
        text_fg = "#0a1d37"
    elif bg_color == SPECIAL_BG:
        hover_color = "#f87171"
        text_fg = "#ffffff"
    else:
        hover_color = bg_color
        text_fg = "#ffffff"

    btn = tk.Button(
        keys_frame,
        text=text,
        bg=bg_color,
        fg=text_fg,
        font=(FONT_NAME, 12, "bold"),
        bd=0,
        relief="flat",
        command=command_func,
        activebackground=hover_color,
        activeforeground=text_fg
    )
    btn.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
    bind_hover(btn, hover_color, bg_color)

# --- KEYPAD BUTTONS ---
create_button("sin",  0, 0, SCI_BG,     lambda: press("sin"))
create_button("cos",  0, 1, SCI_BG,     lambda: press("cos"))
create_button("tan",  0, 2, SCI_BG,     lambda: press("tan"))
create_button("C",    0, 3, SPECIAL_BG, clear)
create_button("(",    0, 4, SPECIAL_BG, lambda: press("("))
create_button(")",    0, 5, SPECIAL_BG, lambda: press(")"))
create_button("/",    0, 6, OP_BG,      lambda: press("/"))

create_button("√",    1, 0, SCI_BG,     lambda: press("√"))
create_button("^",    1, 1, SCI_BG,     lambda: press("^"))
create_button("x²",   1, 2, SCI_BG,     lambda: press("x²"))
create_button("7",    1, 3, NUM_BG,     lambda: press("7"))
create_button("8",    1, 4, NUM_BG,     lambda: press("8"))
create_button("9",    1, 5, NUM_BG,     lambda: press("9"))
create_button("*",    1, 6, OP_BG,      lambda: press("*"))

create_button("ln",   2, 0, SCI_BG,     lambda: press("ln"))
create_button("log",  2, 1, SCI_BG,     lambda: press("log"))
create_button("1/x",  2, 2, SCI_BG,     lambda: press("1/x"))
create_button("4",    2, 3, NUM_BG,     lambda: press("4"))
create_button("5",    2, 4, NUM_BG,     lambda: press("5"))
create_button("6",    2, 5, NUM_BG,     lambda: press("6"))
create_button("-",    2, 6, OP_BG,      lambda: press("-"))

create_button("π",    3, 0, SCI_BG,     lambda: press("π"))
create_button("e",    3, 1, SCI_BG,     lambda: press("e"))
create_button("fact", 3, 2, SCI_BG,     lambda: press("fact"))
create_button("1",    3, 3, NUM_BG,     lambda: press("1"))
create_button("2",    3, 4, NUM_BG,     lambda: press("2"))
create_button("3",    3, 5, NUM_BG,     lambda: press("3"))
create_button("+",    3, 6, OP_BG,      lambda: press("+"))

create_button("abs",  4, 0, SCI_BG,     lambda: press("abs"))
create_button("10\u1d6a", 4, 1, SCI_BG, lambda: press("10\u1d6a"))
create_button("%",    4, 2, SCI_BG,     lambda: press("%"))
create_button("\u232b", 4, 3, SPECIAL_BG, backspace)
create_button("0",    4, 4, NUM_BG,     lambda: press("0"))
create_button(".",    4, 5, NUM_BG,     lambda: press("."))
create_button("=",    4, 6, OP_BG,      calculate)

# --- B. HISTORY RIGHT PANEL ---

history_title = tk.Label(
    history_frame,
    text="Calculation History",
    bg=PANEL_BG,
    fg=TEXT_MUTED,
    font=(FONT_NAME, 11, "bold"),
    pady=10
)
history_title.pack(fill="x")

history_listbox = tk.Listbox(
    history_frame,
    bg=PANEL_BG,
    fg=TEXT_COLOR,
    font=(FONT_NAME, 10, "bold"),
    bd=0,
    highlightthickness=0,
    selectbackground=PANEL_BG,
    selectforeground=TEXT_COLOR
)
history_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

refresh_btn = tk.Button(
    history_frame,
    text="Refresh History",
    bg=SCI_BG,
    fg=TEXT_COLOR,
    font=(FONT_NAME, 10, "bold"),
    bd=0,
    relief="flat",
    command=update_history_sidebar
)
refresh_btn.pack(fill="x", padx=10, pady=10)
bind_hover(refresh_btn, "#2a527c", SCI_BG)

# ---------------------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------------------

print("\n--- Starting Calculator GUI Client ---")
print(f"Connecting to API Server at {api_client.API_URL}...")

update_history_sidebar()

test_history = api_client.fetch_history_request()
if test_history and test_history[0] == "Server Offline":
    print("\n[!] WARNING: Could not connect to API Server.")
    print("    Please verify that server.py is running on port 5000.")
else:
    print("\n[+] SUCCESS: Connected to API Server! History loaded successfully.")

root.mainloop()
