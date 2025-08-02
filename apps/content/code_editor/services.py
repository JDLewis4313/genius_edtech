# apps/code_editor/services.py
from .models import CodeSnippet

class CodeService:
    def run_code(self, code, language="python"):
        """Execute code safely"""
        if language == "python":
            return self._run_python(code)
        elif language == "javascript":
            return self._run_javascript(code)
        elif language == "sql":
            return "SQL execution not yet implemented for safety reasons."
        else:
            return f"Language '{language}' not supported. Supported: python, javascript"
    
    def _run_python(self, code):
        """Execute Python code safely"""
        try:
            # Create a restricted environment
            safe_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "set": set,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "round": round,
                }
            }
            
            # Capture output
            output_lines = []
            def captured_print(*args, **kwargs):
                output_lines.append(' '.join(str(arg) for arg in args))
            
            safe_globals["__builtins__"]["print"] = captured_print
            
            # Execute code
            exec(code, safe_globals)
            
            return '\n'.join(output_lines) if output_lines else "Code executed successfully (no output)"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _run_javascript(self, code):
        """Mock JavaScript execution"""
        # In production, you'd use a sandboxed JS environment
        if "console.log" in code:
            # Extract console.log content (simplified)
            import re
            matches = re.findall(r'console\.log\((.*?)\)', code)
            if matches:
                return '\n'.join(matches)
        return "JavaScript execution requires a browser environment."
    
    def save_snippet(self, user, code, language="python"):
        """Save code snippet for user"""
        if not user or not user.is_authenticated:
            return "Please log in to save code snippets."
        
        snippet = CodeSnippet.objects.create(
            user=user,
            code=code,
            language=language,
            title=f"{language} snippet"
        )
        
        return f"{language.capitalize()} code saved! Snippet ID: {snippet.id}"
    
    def get_snippet(self, user, snippet_id):
        """Retrieve a saved snippet"""
        try:
            snippet = CodeSnippet.objects.get(id=snippet_id, user=user)
            return f"```{snippet.language}\n{snippet.code}\n```"
        except CodeSnippet.DoesNotExist:
            return "Snippet not found."
    
    def get_last_snippet(self, user):
        """Get user's most recent snippet"""
        if not user or not user.is_authenticated:
            return "Please log in to view saved snippets."
        
        snippet = CodeSnippet.objects.filter(user=user).order_by('-created_at').first()
        if snippet:
            return f"Your last {snippet.language} snippet:\n```{snippet.language}\n{snippet.code}\n```"
        else:
            return "No saved snippets found."