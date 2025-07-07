from sympy import sin, cos, tan, cot, sec, csc, pi, simplify, solve, symbols
from sympy.parsing.sympy_parser import parse_expr

class TrigSolver:
    """Enhanced trigonometry service for trig functions and identities"""
    
    def __init__(self):
        self.x = symbols('x')
    
    def solve_trig_equation(self, equation_str):
        """Solve trigonometric equations"""
        try:
            equation_str = equation_str.replace('^', '**')
            if '=' not in equation_str:
                return "Please provide an equation with = sign"
            
            lhs, rhs = equation_str.split('=', 1)
            lhs_expr = parse_expr(lhs)
            rhs_expr = parse_expr(rhs)
            
            solutions = solve(lhs_expr - rhs_expr, self.x)
            
            if not solutions:
                return "No solutions found in the given domain"
            else:
                return f"Solutions: {', '.join(map(str, solutions))}"
        except Exception as e:
            return f"Error solving trig equation: {str(e)}"
    
    def solve_trig_expression(self, expr_str):
        """Simplify trigonometric expressions"""
        try:
            expr = parse_expr(expr_str.replace('^', '**'))
            simplified = simplify(expr)
            return f"Simplified: {simplified}"
        except Exception as e:
            return f"Error simplifying: {str(e)}"
    
    def convert_degrees_to_radians(self, degrees):
        """Convert degrees to radians"""
        try:
            deg = float(degrees)
            rad = deg * pi / 180
            return f"{degrees}° = {rad} radians ≈ {float(rad):.4f} radians"
        except Exception as e:
            return f"Error converting: {str(e)}"
    
    def evaluate_trig_function(self, func, value, unit='radians'):
        """Evaluate trigonometric functions"""
        try:
            val = float(value)
            if unit == 'degrees':
                val = val * pi / 180
            
            trig_funcs = {
                'sin': sin, 'cos': cos, 'tan': tan,
                'cot': cot, 'sec': sec, 'csc': csc
            }
            
            if func.lower() in trig_funcs:
                result = trig_funcs[func.lower()](val)
                return f"{func}({value}{' degrees' if unit == 'degrees' else ' radians'}) = {result} ≈ {float(result):.4f}"
            else:
                return f"Unknown function: {func}"
        except Exception as e:
            return f"Error evaluating: {str(e)}"
    
    def solve_calculus_expression(self, expr):
        """Basic calculus for compatibility"""
        try:
            from sympy import diff, integrate
            x = symbols('x')
            derivative = diff(expr, x)
            integral = integrate(expr, x)
            return f"Derivative: {derivative}, Integral: {integral} + C"
        except Exception as e:
            return f"Error: {str(e)}"
