from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.mentari.services.algebra import AlgebraSolver
from apps.mentari.services.geometry import GeometryHelper
from apps.mentari.services.trigonometry import TrigSolver
from apps.mentari.services.calculus import CalculusSolver
from apps.mentari.services.visualizer import MathVisualizer
import json

@csrf_exempt
def math_support_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')
            operation = data.get('operation', 'solve')
            
            if operation == 'algebra':
                solver = AlgebraSolver()
                result = solver.solve_equation(expression)
            elif operation == 'calculus':
                solver = CalculusSolver()
                result = solver.analyze_expression(expression)
            elif operation == 'trigonometry':
                solver = TrigSolver()
                result = solver.solve_trig_expression(expression)
            elif operation == 'geometry':
                helper = GeometryHelper()
                result = helper.area_of_circle(expression)  # Default example
            else:
                # Default to algebra
                solver = AlgebraSolver()
                result = solver.solve_equation(expression)
            
            return JsonResponse({'result': result})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'mentari/math_support.html')

@csrf_exempt  
def plot_expression_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')
            
            visualizer = MathVisualizer()
            plot_data = visualizer.plot_expression(expression)
            
            return JsonResponse({'plot': plot_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
