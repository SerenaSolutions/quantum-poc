"""DJ trivalente ZYQL em Cirq — mesmo circuito da casa (SerenaSolutions)."""
import cirq

def dj_cirq(case):
    q = cirq.LineQubit.range(3)
    op = [cirq.X(q[2]), cirq.H(q[2]), cirq.H(q[0]), cirq.H(q[1])]
    if case == "const-1": op.append(cirq.X(q[2]))
    elif case == "balanced": op += [cirq.CNOT(q[0], q[2]), cirq.CNOT(q[1], q[2])]
    op += [cirq.H(q[0]), cirq.H(q[1]), cirq.measure(q[0], q[1], key="m")]
    return cirq.Circuit(op)
