from django.shortcuts import render
from django.http import JsonResponse
import subprocess
import tempfile
import os
import json

def code_editor(request):
    return render(request, 'code_editor/code_editor.html')

def run_code(request):
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=400)
    data = json.loads(request.body.decode())
    code = data.get('code', '')
    language = data.get('language', 'python')
    if language == 'python':
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            fname = f.name
        try:
            result = subprocess.run(
                ["python3", fname],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout + result.stderr
        except Exception as e:
            output = str(e)
        finally:
            os.unlink(fname)
        return JsonResponse({'output': output})
    return JsonResponse({'output': f'Execution for {language} is not implemented yet.'})