from sympy import symbols, Eq, solve, pi

class GeometryHelper:
    def area_of_circle(self, radius):
        try:
            r = float(radius)
            return f"Area of circle: {pi * r**2:.2f} units²"
        except:
            return "Invalid radius."

    def pythagorean_theorem(self, a, b):
        try:
            a, b = float(a), float(b)
            c = (a**2 + b**2)**0.5
            return f"Hypotenuse: {c:.2f} units"
        except:
            return "Invalid input."
