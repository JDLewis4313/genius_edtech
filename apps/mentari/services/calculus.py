from sympy import symbols, diff, integrate, limit, oo, simplify, latex
from sympy.parsing.sympy_parser import parse_expr
import re

class CalculusSolver:
    """Enhanced calculus service for derivatives, integrals, and limits"""
    
    def __init__(self):
        self.x = symbols('x')
    
    def differentiate(self, expr_str, order=1):
        """Calculate derivatives"""
        try:
            expr = parse_expr(expr_str.replace('^', '**'))
            derivative = diff(expr, self.x, order)
            
            if order == 1:
                return f"d/dx({expr_str}) = {derivative}"
            else:
                return f"d^{order}/dx^{order}({expr_str}) = {derivative}"
        except Exception as e:
            return f"Error calculating derivative: {str(e)}"
    
    def integrate_expr(self, expr_str, definite=None):
        """Calculate integrals"""
        try:
            expr = parse_expr(expr_str.replace('^', '**'))
            
            if definite:
                # Definite integral with bounds
                a, b = definite
                result = integrate(expr, (self.x, a, b))
                return f"∫[{a} to {b}] ({expr_str}) dx = {result}"
            else:
                # Indefinite integral
                result = integrate(expr, self.x)
                return f"∫({expr_str}) dx = {result} + C"
        except Exception as e:
            return f"Error calculating integral: {str(e)}"
    
    def calculate_limit(self, expr_str, point, direction=None):
        """Calculate limits"""
        try:
            expr = parse_expr(expr_str.replace('^', '**'))
            
            if point == 'infinity':
                point = oo
            elif point == '-infinity':
                point = -oo
            else:
                point = float(point)
            
            if direction:
                result = limit(expr, self.x, point, direction)
                return f"lim(x→{point}{direction}) {expr_str} = {result}"
            else:
                result = limit(expr, self.x, point)
                return f"lim(x→{point}) {expr_str} = {result}"
        except Exception as e:
            return f"Error calculating limit: {str(e)}"
    
    def analyze_expression(self, expr):
        """Basic analysis for compatibility"""
        try:
            x = symbols('x')
            simplified = simplify(expr)
            derivative = diff(simplified, x)
            integral = integrate(simplified, x)
            return f"Expression: {simplified}\nDerivative: {derivative}\nIntegral: {integral} + C"
        except Exception as e:
            return f"Error analyzing expression: {str(e)}"
