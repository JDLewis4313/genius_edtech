from sympy import symbols, Eq, solve, simplify, expand, factor, cancel
from sympy.parsing.sympy_parser import parse_expr
import re

class AlgebraSolver:
    """Enhanced algebra service for equations, polynomials, and algebraic expressions"""
    
    def __init__(self):
        self.x = symbols('x')
    
    def solve_equation(self, equation_str):
        """Solve algebraic equations"""
        try:
            equation_str = re.sub(r'[^0-9xX+\-*/=(). ]', '', equation_str)
            if '=' not in equation_str:
                return "Please provide an equation with = sign"
            
            lhs, rhs = equation_str.split('=', 1)
            eq = Eq(parse_expr(lhs), parse_expr(rhs))
            solutions = solve(eq, self.x)
            
            if not solutions:
                return "No real solutions found"
            elif len(solutions) == 1:
                return f"Solution: x = {solutions[0]}"
            else:
                return f"Solutions: x = {', '.join(map(str, solutions))}"
        except Exception as e:
            return f"Error solving equation: {str(e)}"
    
    def factor_expression(self, expr_str):
        """Factor algebraic expressions"""
        try:
            expr = parse_expr(expr_str.replace('^', '**'))
            factored = factor(expr)
            return f"Factored form: {factored}"
        except Exception as e:
            return f"Error factoring: {str(e)}"
    
    def expand_expression(self, expr_str):
        """Expand algebraic expressions"""
        try:
            expr = parse_expr(expr_str.replace('^', '**'))
            expanded = expand(expr)
            return f"Expanded form: {expanded}"
        except Exception as e:
            return f"Error expanding: {str(e)}"
    
    def simplify_expression(self, expr_str):
        """Simplify algebraic expressions"""
        try:
            expr = parse_expr(expr_str.replace('^', '**'))
            simplified = simplify(expr)
            return f"Simplified: {simplified}"
        except Exception as e:
            return f"Error simplifying: {str(e)}"
