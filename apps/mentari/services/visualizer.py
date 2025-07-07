import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io, base64
from sympy import symbols, sympify, lambdify
import numpy as np

class MathVisualizer:
    def plot_expression(self, expr_str):
        try:
            x = symbols('x')
            expr = sympify(expr_str)
            f = lambdify(x, expr, modules=['numpy'])
            x_vals = np.linspace(-10, 10, 400)
            y_vals = f(x_vals)

            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals)
            ax.set_title(f"y = {expr_str}")
            ax.grid(True)

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            
            # Convert to base64 for web display
            plot_data = base64.b64encode(buf.read()).decode()
            plt.close()
            
            return plot_data
        except Exception as e:
            return f"Error plotting: {str(e)}"
