"""DJ trivalente ZYQL em Braket (LocalSimulator) — mesmo circuito da casa."""
from braket.circuits import Circuit
from braket.devices import LocalSimulator

def dj_braket(case):
    c = Circuit().x(2).h(2).h(0).h(1)
    if case == "const-1": c = c.x(2)
    elif case == "balanced": c = c.cnot(0, 2).cnot(1, 2)
    c = c.h(0).h(1).probability([0, 1])
    return c
