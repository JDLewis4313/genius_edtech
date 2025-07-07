from sympy import pi, sqrt, symbols, solve
import math

class GeometryHelper:
    """Enhanced geometry service for shapes, areas, and geometric calculations"""
    
    def area_of_circle(self, radius):
        """Calculate area of a circle"""
        try:
            r = float(radius)
            area = pi * r**2
            return f"Area of circle with radius {r}: π × {r}² = {area} ≈ {float(area):.2f} square units"
        except Exception as e:
            return f"Error calculating circle area: {str(e)}"
    
    def circumference_of_circle(self, radius):
        """Calculate circumference of a circle"""
        try:
            r = float(radius)
            circumference = 2 * pi * r
            return f"Circumference of circle with radius {r}: 2π × {r} = {circumference} ≈ {float(circumference):.2f} units"
        except Exception as e:
            return f"Error calculating circumference: {str(e)}"
    
    def pythagorean_theorem(self, a=None, b=None, c=None):
        """Solve for missing side in right triangle"""
        try:
            if a is not None and b is not None and c is None:
                # Find hypotenuse
                a, b = float(a), float(b)
                c = sqrt(a**2 + b**2)
                return f"Hypotenuse: √({a}² + {b}²) = √{a**2 + b**2} = {c} ≈ {float(c):.2f} units"
            elif a is not None and c is not None and b is None:
                # Find side b
                a, c = float(a), float(c)
                if c**2 - a**2 < 0:
                    return "Invalid triangle: hypotenuse must be longer than other sides"
                b = sqrt(c**2 - a**2)
                return f"Side b: √({c}² - {a}²) = √{c**2 - a**2} = {b} ≈ {float(b):.2f} units"
            elif b is not None and c is not None and a is None:
                # Find side a
                b, c = float(b), float(c)
                if c**2 - b**2 < 0:
                    return "Invalid triangle: hypotenuse must be longer than other sides"
                a = sqrt(c**2 - b**2)
                return f"Side a: √({c}² - {b}²) = √{c**2 - b**2} = {a} ≈ {float(a):.2f} units"
            else:
                return "Please provide exactly two values to find the third"
        except Exception as e:
            return f"Error with Pythagorean theorem: {str(e)}"
    
    def triangle_area(self, base, height):
        """Calculate area of triangle"""
        try:
            b, h = float(base), float(height)
            area = 0.5 * b * h
            return f"Triangle area: ½ × {b} × {h} = {area} square units"
        except Exception as e:
            return f"Error calculating triangle area: {str(e)}"
    
    def rectangle_area(self, length, width):
        """Calculate area of rectangle"""
        try:
            l, w = float(length), float(width)
            area = l * w
            perimeter = 2 * (l + w)
            return f"Rectangle area: {l} × {w} = {area} square units\nPerimeter: 2({l} + {w}) = {perimeter} units"
        except Exception as e:
            return f"Error calculating rectangle properties: {str(e)}"
