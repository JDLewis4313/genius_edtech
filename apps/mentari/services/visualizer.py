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
            plt.close(fig)
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{image_base64}"
        except Exception as e:
            return f"Error generating plot: {str(e)}"
