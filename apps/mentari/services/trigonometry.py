from sympy import sin, cos, tan, symbols, simplify, pi

class TrigSolver:
    def solve_trig_expression(self, expr):
        try:
            x = symbols('x')
            simplified = simplify(expr)
            return f"Simplified: {simplified}"
        except Exception as e:
            return f"Error: {str(e)}"

    def solve_calculus_expression(self, expr):
        try:
            from sympy import diff, integrate
            x = symbols('x')
            derivative = diff(expr, x)
            integral = integrate(expr, x)
            return f"Derivative: {derivative}, Integral: {integral} + C"
        except Exception as e:
            return f"Error: {str(e)}"
