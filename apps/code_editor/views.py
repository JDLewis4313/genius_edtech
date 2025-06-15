# apps/code_editor/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import subprocess
import tempfile
import os
import json
import re
from apps.tutorials.models import Tutorial, UserTutorialProgress

# Define safe imports for Python execution
SAFE_PYTHON_IMPORTS = [
    'math', 'datetime', 'json', 'collections', 'itertools',
    'functools', 'operator', 'string', 'random', 'decimal',
    'fractions', 'statistics', 'heapq', 'bisect', 'array',
    'enum', 'dataclasses', 'typing', 'pprint', 'textwrap',
    # Chemistry/Science specific
    'numpy', 'scipy', 'pandas', 'matplotlib.pyplot',
]

def code_editor(request):
    """Main code editor view with tutorial support"""
    context = {
        'tutorial': None,
        'tutorial_slug': None,
    }
    
    # Check if coming from a tutorial
    tutorial_slug = request.GET.get('tutorial')
    if tutorial_slug:
        try:
            tutorial = Tutorial.objects.get(slug=tutorial_slug, is_published=True)
            context['tutorial'] = tutorial
            context['tutorial_slug'] = tutorial_slug
        except Tutorial.DoesNotExist:
            pass
    
    return render(request, 'code_editor/code_editor.html', context)

@require_http_methods(["POST"])
def run_code(request):
    """Execute code safely with timeout and resource limits"""
    try:
        data = json.loads(request.body.decode())
        code = data.get('code', '')
        language = data.get('language', 'python')
        tutorial_slug = data.get('tutorial_slug', None)
        
        # Track tutorial progress if user is logged in
        if request.user.is_authenticated and tutorial_slug:
            try:
                tutorial = Tutorial.objects.get(slug=tutorial_slug)
                progress, created = UserTutorialProgress.objects.get_or_create(
                    user=request.user,
                    tutorial=tutorial
                )
                # You can add more progress tracking logic here
            except Tutorial.DoesNotExist:
                pass
        
        # Execute code based on language
        if language == 'python':
            output = execute_python_code(code)
        elif language == 'javascript':
            output = execute_javascript_code(code)
        elif language == 'sql':
            output = execute_sql_code(code)
        else:
            output = f'Execution for {language} is not implemented yet.'
        
        return JsonResponse({'output': output, 'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON', 'success': False}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e), 'success': False}, status=500)

def execute_python_code(code):
    """Execute Python code safely"""
    # Basic security check - prevent obvious dangerous operations
    dangerous_patterns = [
        r'__import__', r'exec\s*\(', r'eval\s*\(', r'compile\s*\(',
        r'open\s*\(', r'file\s*\(', r'input\s*\(', r'raw_input\s*\(',
        r'subprocess', r'os\.', r'sys\.', r'globals\s*\(',
        r'locals\s*\(', r'vars\s*\(', r'dir\s*\('
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return f"Security Error: Usage of '{pattern}' is not allowed in the code editor."
    
    # Add safe imports header for chemistry calculations
    safe_header = """
# Safe imports for chemistry calculations
import math
import json
from collections import defaultdict, Counter
from decimal import Decimal
from fractions import Fraction
import statistics

# Chemistry constants
AVOGADRO = 6.022e23
GAS_CONSTANT = 8.314  # J/(mol·K)
FARADAY = 96485  # C/mol

# Atomic masses dictionary (simplified)
atomic_masses = {
    'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012,
    'B': 10.81, 'C': 12.01, 'N': 14.01, 'O': 16.00,
    'F': 19.00, 'Ne': 20.18, 'Na': 22.99, 'Mg': 24.31,
    'Al': 26.98, 'Si': 28.09, 'P': 30.97, 'S': 32.07,
    'Cl': 35.45, 'Ar': 39.95, 'K': 39.10, 'Ca': 40.08,
    'Fe': 55.85, 'Cu': 63.55, 'Zn': 65.39, 'Br': 79.90,
    'Ag': 107.87, 'I': 126.90, 'Au': 196.97
}

"""
    
    # Combine safe header with user code
    full_code = safe_header + "\n" + code
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(full_code)
        fname = f.name
    
    try:
        # Run with resource limits
        result = subprocess.run(
            ["python3", fname],
            capture_output=True,
            text=True,
            timeout=5,  # 5 second timeout
            env={**os.environ, 'PYTHONPATH': ''}  # Clean environment
        )
        output = result.stdout
        if result.stderr:
            # Clean up the error message to remove the safe header line numbers
            error_lines = result.stderr.split('\n')
            cleaned_error = []
            for line in error_lines:
                # Adjust line numbers in error messages
                match = re.search(r'line (\d+)', line)
                if match:
                    line_num = int(match.group(1))
                    # Subtract the number of lines in the safe header
                    adjusted_line = line_num - safe_header.count('\n')
                    if adjusted_line > 0:
                        line = line.replace(f'line {line_num}', f'line {adjusted_line}')
                cleaned_error.append(line)
            output += '\n'.join(cleaned_error)
            
    except subprocess.TimeoutExpired:
        output = "Error: Code execution timed out (5 second limit)"
    except Exception as e:
        output = f"Error: {str(e)}"
    finally:
        try:
            os.unlink(fname)
        except:
            pass
    
    return output.strip()

def execute_javascript_code(code):
    """Execute JavaScript code using Node.js"""
    # Check if Node.js is available
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
    except:
        return "Error: Node.js is not installed on the server. JavaScript execution is unavailable."
    
    # Basic security checks
    dangerous_patterns = [
        r'require\s*\(', r'import\s+', r'process\.', r'child_process',
        r'fs\.', r'eval\s*\(', r'Function\s*\(', r'setTimeout',
        r'setInterval', r'__dirname', r'__filename'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return f"Security Error: Usage of '{pattern}' is not allowed in the code editor."
    
    # Add chemistry constants
    js_header = """
// Chemistry constants
const AVOGADRO = 6.022e23;
const GAS_CONSTANT = 8.314; // J/(mol·K)
const FARADAY = 96485; // C/mol

// Atomic masses
const atomicMasses = {
    'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012,
    'B': 10.81, 'C': 12.01, 'N': 14.01, 'O': 16.00,
    'F': 19.00, 'Ne': 20.18, 'Na': 22.99, 'Mg': 24.31,
    'Al': 26.98, 'Si': 28.09, 'P': 30.97, 'S': 32.07,
    'Cl': 35.45, 'Ar': 39.95, 'K': 39.10, 'Ca': 40.08,
    'Fe': 55.85, 'Cu': 63.55, 'Zn': 65.39, 'Br': 79.90,
    'Ag': 107.87, 'I': 126.90, 'Au': 196.97
};

"""
    
    full_code = js_header + "\n" + code
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write(full_code)
        fname = f.name
    
    try:
        result = subprocess.run(
            ["node", fname],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
    except subprocess.TimeoutExpired:
        output = "Error: Code execution timed out (5 second limit)"
    except Exception as e:
        output = f"Error: {str(e)}"
    finally:
        try:
            os.unlink(fname)
        except:
            pass
    
    return output.strip()

def execute_sql_code(code):
    """Execute SQL code in a safe in-memory SQLite database"""
    import sqlite3
    
    # Create in-memory database with sample chemistry data
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Create sample tables
        cursor.executescript("""
        CREATE TABLE elements (
            atomic_number INTEGER PRIMARY KEY,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            atomic_mass REAL NOT NULL,
            category TEXT,
            period INTEGER,
            group_number INTEGER
        );
        
        INSERT INTO elements VALUES
        (1, 'H', 'Hydrogen', 1.008, 'Nonmetal', 1, 1),
        (2, 'He', 'Helium', 4.003, 'Noble Gas', 1, 18),
        (3, 'Li', 'Lithium', 6.941, 'Alkali Metal', 2, 1),
        (4, 'Be', 'Beryllium', 9.012, 'Alkaline Earth Metal', 2, 2),
        (5, 'B', 'Boron', 10.81, 'Metalloid', 2, 13),
        (6, 'C', 'Carbon', 12.01, 'Nonmetal', 2, 14),
        (7, 'N', 'Nitrogen', 14.01, 'Nonmetal', 2, 15),
        (8, 'O', 'Oxygen', 16.00, 'Nonmetal', 2, 16),
        (9, 'F', 'Fluorine', 19.00, 'Halogen', 2, 17),
        (10, 'Ne', 'Neon', 20.18, 'Noble Gas', 2, 18),
        (11, 'Na', 'Sodium', 22.99, 'Alkali Metal', 3, 1),
        (12, 'Mg', 'Magnesium', 24.31, 'Alkaline Earth Metal', 3, 2);
        
        CREATE TABLE compounds (
            id INTEGER PRIMARY KEY,
            formula TEXT NOT NULL,
            name TEXT NOT NULL,
            molecular_weight REAL,
            state_at_stp TEXT
        );
        
        INSERT INTO compounds VALUES
        (1, 'H2O', 'Water', 18.015, 'liquid'),
        (2, 'CO2', 'Carbon Dioxide', 44.01, 'gas'),
        (3, 'NaCl', 'Sodium Chloride', 58.44, 'solid'),
        (4, 'H2SO4', 'Sulfuric Acid', 98.08, 'liquid'),
        (5, 'NH3', 'Ammonia', 17.03, 'gas');
        """)
        
        # Execute user's SQL
        cursor.execute(code)
        
        # Fetch results
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Format output
        if results:
            output = " | ".join(columns) + "\n"
            output += "-" * (len(output) - 1) + "\n"
            for row in results:
                output += " | ".join(str(val) for val in row) + "\n"
        else:
            output = "Query executed successfully. No results to display."
            
        conn.close()
        return output
        
    except sqlite3.Error as e:
        return f"SQL Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

@require_http_methods(["GET"])
def get_tutorial_template(request, slug, template_type='starter'):
    """Get tutorial template code for the editor"""
    tutorial = get_object_or_404(Tutorial, slug=slug, is_published=True)
    
    if template_type == 'starter':
        code = tutorial.starter_code
    elif template_type == 'solution':
        # Check if user has made progress or is authenticated
        if request.user.is_authenticated:
            code = tutorial.solution_code
        else:
            return JsonResponse({
                'error': 'Please log in to view solutions',
                'success': False
            }, status=403)
    else:
        return JsonResponse({
            'error': 'Invalid template type',
            'success': False
        }, status=400)
    
    return JsonResponse({
        'code': code,
        'language': tutorial.language,
        'title': tutorial.title,
        'success': True
    })

@login_required
@require_http_methods(["POST"])
def save_tutorial_progress(request, slug):
    """Save user's progress on a tutorial"""
    tutorial = get_object_or_404(Tutorial, slug=slug)
    
    try:
        data = json.loads(request.body.decode())
        code = data.get('code', '')
        step_id = data.get('step_id', None)
        
        progress, created = UserTutorialProgress.objects.get_or_create(
            user=request.user,
            tutorial=tutorial
        )
        
        # Save the current code
        progress.current_code = code
        
        # Mark step as completed if provided
        if step_id:
            completed_steps = progress.completed_steps or []
            if step_id not in completed_steps:
                completed_steps.append(step_id)
                progress.completed_steps = completed_steps
        
        progress.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Progress saved'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)