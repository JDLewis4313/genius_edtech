from sympy import symbols, Eq, solve, simplify
import re

class AlgebraSolver:
    def solve_equation(self, equation_str):
        try:
            x = symbols('x')
            # Sanitize input
            equation_str = re.sub(r'[^0-9xX+\-*/=(). ]', '', equation_str)
            lhs, rhs = equation_str.split('=')
            eq = Eq(simplify(lhs), simplify(rhs))
            solutions = solve(eq, x)
            return f"Solution(s): {solutions}"
        except Exception as e:
            return f"Sorry, I couldn't solve that. Error: {str(e)}"
