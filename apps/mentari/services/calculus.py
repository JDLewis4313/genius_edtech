from sympy import symbols, diff, integrate, simplify

class CalculusSolver:
    def analyze_expression(self, expr):
        try:
            x = symbols('x')
            simplified = simplify(expr)
            derivative = diff(simplified, x)
            integral = integrate(simplified, x)
            return f"Expression: {simplified}\nDerivative: {derivative}\nIntegral: {integral} + C"
        except Exception as e:
            return f"Error analyzing expression: {str(e)}"
