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
        "Meter (m)": 1, "Kilometer (km)":1000, "Centimeter (cm)":0.01, "Milimeter (mm)": 0.001, "Mile (mi)": 1609.344, "Yard (yd)": 0.9144, "Foot (ft)": 0.3048,
    }
}