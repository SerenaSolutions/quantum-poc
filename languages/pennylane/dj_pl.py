"""DJ trivalente ZYQL em PennyLane — mesmo circuito da casa (SerenaSolutions)."""
import pennylane as qml

dev = qml.device("default.qubit", wires=3, shots=None)

def dj_pl(case):
    qml.X(2); qml.Hadamard(2); qml.Hadamard(0); qml.Hadamard(1)
    if case == "const-1": qml.X(2)
    elif case == "balanced": qml.CNOT(wires=[0, 2]); qml.CNOT(wires=[1, 2])
    qml.Hadamard(0); qml.Hadamard(1)
    return qml.probs(wires=[0, 1])

@qml.qnode(dev)
def circuit(case):
    return dj_pl(case)
