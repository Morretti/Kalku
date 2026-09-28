"""Advance Calculactor + Unit Converter + Loan Calculactor Built with python & Tkinter"""

import ast
import math
import operator
import tkinter as tk
from tkinter import ttk

# =============
# Calcu Engine
# =============

BINARY_OPS = {
    ast.add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.div: operator.truediv,
    ast.pow: operator.pow, ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
CONSTANTS = {"pi": math.pi, "e":math.e}

def factorial(n):
    if n < 0 or int(n) != n:
        raise ValueError("Factorial is only defined for integers >= 0")
    return math.factorial(int(n))

def build_functions(degress):
    to_rad = math.radians if degress else (lambda x: x)
    from_rad = math.degrees if degress else (lambda x: x)
    return {
        "sin": lambda x: math.sin(to_rad(x)),
        "cos": lambda x: math.cos(to_rad(x)),
        "tan": lambda x: math.tan(to_rad(x)),
        "asin": lambda x: from_rad(math.asin(x)),
        "acos": lambda x: from_rad(math.acos(x)),
        "atan": lambda x: from_rad(math.atan(x)),
        "ln": math.log, "log":math.log10, "sqrt": math.sqrt,
        "abs": abs, "fact": factorial, "exp": math.exp,
    }

def calculate(text, degrees=True):
    text = (text.replace("x", "*").replace("÷", "/").replace("−", "-")
            .replace("^", "**").replace("π","phi").replace("√", "sqrt")
            .replace("%", "/100").replace(" ", "")
            )
    functions = build_functions(degrees)

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.Name) and node.id in CONSTANTS:
            return CONSTANTS[node.id]
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](ev(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPS:
            left, right = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10000:
                raise ValueError("Exponent too large")
            return BINARY_OPS[type(node.op)](left, right)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in functions and len(node.args) == 1
                and not node.keywords):
            return functions[node.func.id](ev(node.args[0]))
        raise ValueError("Invalid Expression")

    result = ev(ast.parse(text, mode="eval"))
    if isinstance(result, complex):
        raise ValueError("Result is a complex number")
    if isinstance(result, float) and not math.isfinite(result):
        raise ValueError("Result is infinite")
    return result

def format_number(x, snap_to_zero=True):
    if isinstance(x, int):
        return str(x)
    if snap_to_zero and abs(x) < 1e-12: #Harusnya si ngehapus floating point noise
        return "0"
    if x == int(x) and abs(x) < 1e15:
        return str(int(x))
    return f"{x:.12g}"



# ==============
# 2. Conversion
# ==============

UNITS = {
    "Length": { #satuannya pake meter aja udah
        "Meter (m)": 1, "Kilometer (km)":1000, "Centimeter (cm)":0.01, "Milimeter (mm)": 0.001, "Mile (mi)": 1609.344, "Yard (yd)": 0.9144, "Foot (ft)": 0.3048, "Inch (in)": 0.0254,
    },

    "Mass" : { #ngitung beradd
        "Kilogram (kg)": 1,"Gram (g)": 0.001, "Miligram (mg)": 1e-6, "Metric ton (t)": 1000, "Pound (lb)": 0.45359273, "Ounce (oz)": 0.028349523125, 
    },

    "Volume": { #nyari volume (isi)
        "Liter (L)": 1, "Mililiter (ml)": 0.001, "Cubic meter (m³)": 1000, "Gallon (US)": 3.785411784, "Cup (US)": 0.2365882365,
    },

    "Area": { #nyari luas
        "Square meter (m²)": 1, "Square kilometer (km²)": 1e6, "Hectare (ha)": 1e4, "Square centimeter (cm²)": 1e-4, "Acre": 4046.8564224, "Square foot (ft²)": 0.09290304,
    },

    "Temperature" : { #Suhu
        "Celcius (°C)": None, "Fahrenheit (°F)": None, "Kelvin (K)": None, "Reaumur (°Re)": None
    },

    "Speed": {#Kecepetean 
        "m/s": 1, "km/h": 1 / 3.6, "mph": 0.44704, "Knot": 0.514444444,
    },

    "Time": { #waktu
        "Second" : 1, "Minute": 60, "Hour": 3600, "Day": 86400, "Week": 604800,
        "Year (365 Days)": 31536000, 
    },

    "Data": { #byte 
        "Bit": 0.125, "Byte": 1, "Kilobyte (KB)": 1024, "Megabyte (MB)": 1024 ** 2, "Gigabyte (GB)": 1024 ** 3, "Terabyte (TB)": 1024 ** 4,    
    },

    "Energy": { #joule
        "Joule (J)": 1, "Kilojoule (KJ)": 1000, "Calorie (cal)": 4.184, "Kilocalorie (kcal)": 4184, "Kilowatt-hour (kWh)": 3.6e6,
    },

    "Pressure": { #pascal 
        "Pascal (Pa)": 1, "Kilopascal (kPa)": 1000, "Bar": 1e5, "Atmosphere (atm)": 101325, "PSI": 6894.757293168,
    },

    "Angle": { #sudut
        "Degree (°)": 1, "Radian (rad)": 180 / math.pi, "Gradian (grad)": 0.9,
    },

    #Money (In Indonesia Rupiah)
    "Currency": {
        "Indonesia Rupiah (IDR)": 1, "US Dollar (USD)": 17914, "Euro (EUR)": 20480,
        "British Pound (GBP)": 23725, "Japanese Yen (JPY)": 113, "Singapore Dollar (SGD)": 14025, "Malaysian Ringgit (MYR)": 4400, "Chinese Yuan (CNY)": 2670,
        "Saudi Riyal (SAR)": 4800,
    },
}

def convert(category, value, from_unit, to_unit):
    if category == "Temperature":
        celcius = {"Celcius (°C)": value,
                   "Fahrenheit (°F)": (value - 32) * 5 /9,
                   "Kelvin (K)": value - 273.15,
                   "Reaumur (°Re)": value * 5 / 4}[from_unit]
        return {"Celcius (°C)": celcius,
                "Fahrenheit (°F)": celcius * 9 / 5 + 32,
                "Kelvin (K)": celcius + 273.15,
                "Reaumur (°Re)": celcius * 4 / 5}[to_unit]
    table = UNITS[category]
    return value * table[from_unit] / table[to_unit]

def format_currency(x):
    return f"{x:,.0f}"

# ===============
# User Interface
# ===============

COLORS = {"bg": "#1c1c1e", "display": "#000000", "number": "#333336",       "operator": "#ff9f0a", "function": "#4a4a4f", "text": "#ffffff", "gary": "9a9a9f", "red": "#ff453a"}
FUNCTION_NAMES = {"sin", "cos", "tan", "asin", "acos", "atan", "in", "log", "√", "abs"}

class App(tk.Tk):
    def __init__(self):
        self.tittle("Advanced Calculactor")
        self.geometry("400x740")
        self.minsize(360, 660)
        self.degress = True
        self.memory = 0
        self.last_answer = "0"
        self.scientific_visible = False

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)
        tab_calc = tk.Frame(notebook, bg=COLORS["bg"])
        tab_convert, tab_loan = ttk.Frame(notebook), ttk.Frame(notebook)
        notebook.add(tab_calc, text="Calculactor")
        notebook.add(tab_convert, text="Converter")
        notebook.add(tab_loan, text="Loan")
        self.build_calculactor(tab_calc)
        self.build_converter(tab_convert)
        self.build_loan(tab_loan)


    def build_calculactor(self, frame):
        self.expression = tk.StringVar()
        self.expression.trace_add("write", self.preview)
        self.entry = tk.Entry(frame, textvariable=self.expression,
                              font=("Segoe UI", 26), justify="right", bg=COLORS["display"], fg=COLORS["text"], insertbackground=COLORS["text"], relief="flat")
        self.entry.pack(fill="x", padx=10, pady=(12, 0), ipady=8)
        self.entry.bind("<Return>", lambda e: self.equals())
        self.entry.bind("<KP_Enter>", lambda e: self.equals())
        self.entry.bind("<Escape>", lambda e: self.clear_all())
        self.entry.focus.set()
        self.result_label = tk.Label(frame, text="", font=("Segoe UI", 16), anchor="e", bg=COLORS["bg"], fg=COLORS["gray"])
        self.result_label.pack(fill="x", padx=12)

        bar = tk.Frame(frame, bg=COLORS["bg"])
        bar.pack(fill="x", padx=10, pady=4)
        self.mode_button = tk.Button(bar, text="DEG", width=6,
                                     bg=COLORS["function"], fg=COLORS["text"],
                                     relief="flat", takefocus=False,
                                     command=self.toggle_angle_mode)
        self.mode_button.pack(side="left")
        tk.Button(bar, text="Scientific", width=11, bg=COLORS["function"], fg=COLORS["text"], relief="flat", takefocus=False, command=self.toggle_scientific).pack(side="left", padx=6)

        self.history_list = tk.Listbox(frame, height=4, bg=COLORS["display"], fg=COLORS["gray"], bd=0, highlightthickness=0, font=("Consolas", 10))

        self.history_list.pack(fill="x", padx="10", pady="4")
        self.history_list.bind("<Double-Button-1>", self.use_history)

        area = tk.Frame(frame, bg=COLORS["bg"])
        area.pack(fill="both", expand=True, padx=8, pady=6)
        area.columnconfigure(0, weight=1)
        area.rowconfigure(1, weight=2)

        actions = {
            
        }


