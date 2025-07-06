from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.mentari.services.algebra import AlgebraSolver
from apps.mentari.services.geometry import GeometryHelper
from apps.mentari.services.trigonometry import TrigSolver
from apps.mentari.services.calculus import CalculusSolver
from apps.mentari.services.visualizer import MathVisualizer
import json  

solver = AlgebraSolver()
geo = GeometryHelper()
trig = TrigSolver()
visualizer = MathVisualizer()

@csrf_exempt
def plot_expression_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        expr = data.get("expression", "")
        image_data = visualizer.plot_expression(expr)
        return JsonResponse({"image": image_data})
@csrf_exempt
def math_support_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        topic = data.get("topic")
        question = data.get("question", "")

        if topic == "algebra":
            result = solver.solve_equation(question)
        elif topic == "geometry":
            if "radius" in data:
                result = geo.area_of_circle(data["radius"])
            elif "a" in data and "b" in data:
                result = geo.pythagorean_theorem(data["a"], data["b"])
            else:
                result = "Missing geometry parameters."
        elif topic == "trigonometry":
            result = trig.solve_trig_expression(question)
        elif topic == "calculus":
            result = trig.solve_calculus_expression(question)
        else:
            result = "Unknown topic."

        return JsonResponse({"result": result})
    return render(request, "mentari/math_support.html")
