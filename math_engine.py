import re
import math

def get_error_name(exception):
    """
    Returns a friendly string name for the exception (e.g. "Zero Division Error").
    """
    if isinstance(exception, ZeroDivisionError):
        return "Zero Division Error"
    elif isinstance(exception, SyntaxError):
        return "Syntax Error"
    elif isinstance(exception, NameError):
        return "Name Error"
    elif isinstance(exception, TypeError):
        return "Type Error"
    elif isinstance(exception, ValueError):
        return "Value Error"
    else:
        name = type(exception).__name__
        friendly_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
        return friendly_name if friendly_name.endswith("Error") else f"{friendly_name} Error"

def sanitize_expression(expr):
    """
    Sanitizes the mathematical expression.
    """
    if re.search(r'\(\s*\)', expr):
        raise SyntaxError("Empty parentheses are not mathematically valid.")
    
    expr = expr.replace('π', 'pi')
    expr = expr.replace('√', 'sqrt')
    expr = expr.replace('^', '**')
    expr = re.sub(r'(\d+(?:\.\d+)?)%', r'\1/100', expr)
    expr = re.sub(r'\b0+(\d+)(?!\.)', r'\1', expr)
    return expr

def evaluate_math(expression, angle_mode="DEG"):
    """
    Safely sanitizes and evaluates the expression under restricted environments.
    """
    sanitized_expr = sanitize_expression(expression)
    is_deg = (angle_mode == "DEG")
    
    eval_globals = {
        'sin': lambda x: math.sin(math.radians(x)) if is_deg else math.sin(x),
        'cos': lambda x: math.cos(math.radians(x)) if is_deg else math.cos(x),
        'tan': lambda x: math.tan(math.radians(x)) if is_deg else math.tan(x),
        'sqrt': math.sqrt,
        'ln': math.log,
        'log': math.log10,
        'pi': math.pi,
        'e': math.e,
        'fact': math.factorial,
        'abs': abs,
    }
    
    calculation_result = eval(sanitized_expr, {"__builtins__": None}, eval_globals)
    
    if isinstance(calculation_result, (int, float)):
        calculation_result = round(calculation_result, 12)
        if isinstance(calculation_result, float) and calculation_result.is_integer():
            calculation_result = int(calculation_result)
            
    return str(calculation_result)
