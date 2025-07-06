from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.mentari.services.quantum import QuantumHelper
import json

@csrf_exempt
def quantum_chat_view(request):
    data = json.loads(request.body)
    gate = data.get("gate", "H")
    state = data.get("state", [[1], [0]])  # Default to |0⟩

    q = QuantumHelper()
    result = q.apply_gate(gate, state)
    pretty = q.pretty_state(result) if isinstance(result, Matrix) else result

    return JsonResponse({
        "input_state": state,
        "gate": gate,
        "result": pretty
    })
