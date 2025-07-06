from sympy import Matrix, I, sqrt, simplify
from sympy.physics.quantum import TensorProduct
import random

class QuantumHelper:
    def __init__(self):
        self.gates = {
            "I": Matrix([[1, 0], [0, 1]]),
            "X": Matrix([[0, 1], [1, 0]]),
            "Y": Matrix([[0, -I], [I, 0]]),
            "Z": Matrix([[1, 0], [0, -1]]),
            "H": (1 / sqrt(2)) * Matrix([[1, 1], [1, -1]])
        }

    def get_gate(self, name):
        return self.gates.get(name.upper())

    def apply_gate(self, gate_name, state_vector):
        gate = self.get_gate(gate_name)
        if gate is None:
            return f"Unknown gate: {gate_name}"
        try:
            result = simplify(gate * Matrix(state_vector))
            return result
        except Exception as e:
            return f"Error applying gate: {str(e)}"

    def tensor_product(self, *states):
        try:
            result = states[0]
            for s in states[1:]:
                result = TensorProduct(result, s)
            return simplify(result)
        except Exception as e:
            return f"Tensor error: {str(e)}"

    def measure(self, state_vector):
        probs = [abs(x)**2 for x in state_vector]
        total = sum(probs)
        norm_probs = [float(p / total) for p in probs]
        outcome = random.choices(range(len(state_vector)), weights=norm_probs)[0]
        collapsed = [0] * len(state_vector)
        collapsed[outcome] = 1
        return {"outcome": outcome, "collapsed_state": collapsed}

    def pretty_state(self, state_vector):
        basis = [f"|{i:0{len(state_vector).bit_length()-1}b}⟩" for i in range(len(state_vector))]
        terms = []
        for i, amp in enumerate(state_vector):
            if amp != 0:
                terms.append(f"{amp}·{basis[i]}")
        return " + ".join(terms) if terms else "0"
