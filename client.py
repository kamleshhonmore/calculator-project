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
    """Inserts characters or expressions at the current text cursor position."""
    global expression
    
    expr = equation_text.get()
    if expr == "0":
        expr = ""
        current_pos = 0
    else:
        try:
            current_pos = lcd_main.index(tk.INSERT)
        except:
            current_pos = len(expr)
            
    prefix = expr[:current_pos]
    suffix = expr[current_pos:]
    
    if character == "1/x":
        if expr == "" or expr == "0":
            new_expr = "1/("
            cursor_offset = 3
        else:
            new_expr = f"1/({expr})"
            cursor_offset = len(new_expr)
        equation_text.set(new_expr)
        lcd_main.icursor(cursor_offset)
        lcd_main.focus_set()
        expression = new_expr
        return

    inserted = ""
    if character == "x²":
        inserted = "^2"
    elif character == "10\u1d6a":
        inserted = "10^("
    elif character in ["sin", "cos", "tan", "ln", "log", "fact", "abs"]:
        inserted = f"{character}("
    else:
        inserted = str(character)
        
    new_expr = prefix + inserted + suffix
    equation_text.set(new_expr)
    
    # Put cursor right after the inserted text
    lcd_main.icursor(current_pos + len(inserted))
    lcd_main.focus_set()
    expression = new_expr

def calculate():
    """Sends the expression to the API server and displays the answer."""
    global expression
    expression = equation_text.get()
    
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
    lcd_main.icursor(tk.END)
    lcd_main.focus_set()

def clear():
    """Resets the calculator input to empty."""
    global expression
    expression = ""
    equation_text.set("0")
    lcd_main.icursor(1)
    lcd_main.focus_set()

def backspace():
    """Removes the character right before the cursor (standard backspace action)."""
    global expression
    expr = equation_text.get()
    if expr == "0" or expr == "":
        return
        
    try:
        current_pos = lcd_main.index(tk.INSERT)
    except:
        current_pos = len(expr)
        
    if current_pos > 0:
        prefix = expr[:current_pos - 1]
        suffix = expr[current_pos:]
        new_expr = prefix + suffix
        if new_expr == "":
            new_expr = "0"
            cursor_pos = 1
        else:
            cursor_pos = current_pos - 1
        equation_text.set(new_expr)
        lcd_main.icursor(cursor_pos)
        
    expression = equation_text.get()
    if expression == "0":
        expression = ""
    lcd_main.focus_set()

def update_history_sidebar():
    """Fetches history logs from api_client and updates the listbox."""
    history_items = api_client.fetch_history_request()
    history_listbox.delete(0, tk.END)
    for item in history_items:
        history_listbox.insert(tk.END, item)

def on_history_select(event):
    """Loads clicked calculation history back into the calculator display."""
    try:
        selected_index = history_listbox.curselection()
        if selected_index:
            selected_item = history_listbox.get(selected_index)
            if " = " in selected_item:
                eq = selected_item.split(" = ")[0]
                equation_text.set(eq)
                lcd_main.icursor(tk.END)
                lcd_main.focus_set()
    except Exception as e:
        print(f"DEBUG - History select error: {e}")

# ---------------------------------------------------------------------
# MAIN GUI LAYOUT (Tkinter)
# ---------------------------------------------------------------------

root = tk.Tk()
root.title("Scientific Calculator Client")
root.geometry("770x520")
root.configure(bg=WINDOW_BG)
root.resizable(False, False)

def bind_hover(btn, hover_bg, normal_bg):
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))

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

# Validation logic to prevent typing random non-math characters
def validate_input(new_value):
    import re
    return bool(re.match(r"^[0-9+\-*/.()^%\s\u03c0\u221a\u1d6a\u00b2a-zA-Z]*$", new_value))

vcmd = (root.register(validate_input), "%P")

# If display is exactly "0" and user types a digit or math start, clear the "0"
def check_zero(event):
    if equation_text.get() == "0" and event.char in "0123456789(sclat":
        equation_text.set("")

lcd_main = tk.Entry(
    lcd_screen,
    textvariable=equation_text,
    justify="right",
    bg="#c2e9fb",
    fg="#0a1d37",
    font=("Courier New", 26, "bold"),
    bd=0,
    highlightthickness=0,
    insertbackground="#0a1d37",
    validate="key",
    validatecommand=vcmd
)
lcd_main.pack(fill="x", pady=10)
lcd_main.bind("<Key>", check_zero)

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

def move_cursor_left():
    try:
        current_pos = lcd_main.index(tk.INSERT)
        if current_pos > 0:
            lcd_main.icursor(current_pos - 1)
    except:
        pass
    lcd_main.focus_set()

def move_cursor_right():
    try:
        current_pos = lcd_main.index(tk.INSERT)
        lcd_main.icursor(current_pos + 1)
    except:
        pass
    lcd_main.focus_set()

right_arrow_btn = tk.Button(
    mode_frame,
    text="▶",
    bg=SCI_BG,
    fg=TEXT_COLOR,
    font=(FONT_NAME, 8, "bold"),
    bd=0,
    relief="flat",
    padx=8,
    pady=3,
    command=move_cursor_right
)
right_arrow_btn.pack(side="right", padx=2)
bind_hover(right_arrow_btn, "#2a527c", SCI_BG)

left_arrow_btn = tk.Button(
    mode_frame,
    text="◀",
    bg=SCI_BG,
    fg=TEXT_COLOR,
    font=(FONT_NAME, 8, "bold"),
    bd=0,
    relief="flat",
    padx=8,
    pady=3,
    command=move_cursor_left
)
left_arrow_btn.pack(side="right", padx=2)
bind_hover(left_arrow_btn, "#2a527c", SCI_BG)

keys_frame = tk.Frame(calculator_frame, bg=WINDOW_BG)
keys_frame.pack(fill="both", expand=True)

for r in range(5):
    keys_frame.rowconfigure(r, weight=1)
for c in range(7):
    keys_frame.columnconfigure(c, weight=1)

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

history_listbox.bind("<<ListboxSelect>>", on_history_select)

# Bind Enter/Return to calculate, Escape to clear screen
root.bind("<Return>", lambda e: calculate())
root.bind("<Escape>", lambda e: clear())

# Set initial focus and position cursor at the end
lcd_main.focus_set()
lcd_main.icursor(tk.END)

root.mainloop()
