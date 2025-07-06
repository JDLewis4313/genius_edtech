# apps/mentari/services/code.py
from apps.code_editor.services import CodeService

def handle_code_request(message, user=None):
    """Handle code execution requests"""
    try:
        service = CodeService()
        
        # Extract code
        if "run code:" in message.lower():
            code = message.split("run code:", 1)[1].strip()
        elif "execute:" in message.lower():
            code = message.split("execute:", 1)[1].strip()
        else:
            return {
                "text": "To run code, use: 'run code: print(\"Hello\")'",
                "card": {
                    "type": "code_examples",
                    "examples": [
                        "run code: print('Hello World')",
                        "run code: sum([1, 2, 3, 4, 5])",
                        "run code: [x**2 for x in range(5)]"
                    ]
                }
            }
        
        # Detect language
        language = "python"  # Default
        if "console.log" in code:
            language = "javascript"
        elif "SELECT" in code.upper():
            language = "sql"
        
        # Execute
        result = service.run_code(code, language)
        
        return {
            "text": f"**Output ({language}):**\n```\n{result}\n```",
            "card": {
                "type": "code_result",
                "language": language,
                "code": code,
                "output": result
            }
        }
        
    except Exception as e:
        return {"text": f"Code execution error: {str(e)}"}