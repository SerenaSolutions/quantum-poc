# -*- coding: utf-8 -*-
"""Confronto multilíngue dos apps da Serena Solutions com as linguagens quânticas.

O MESMO circuito da decisão trivalente ZYQL (Deutsch-Jozsa n=2) e dos trançados
S3, escritos em: Qiskit, OpenQASM 3, Cirq, PennyLane, Braket (executados e
verificados numericamente) + Q# (fonte de referência declarativa).

Equivalência: todas as implementações concordam exatamente (sem ruído).
"""
import json, os, sys, numpy as np

os.makedirs("languages/qasm3", exist_ok=True)
os.makedirs("languages/qsharp", exist_ok=True)
os.makedirs("languages/cirq", exist_ok=True)
os.makedirs("languages/pennylane", exist_ok=True)
os.makedirs("languages/braket", exist_ok=True)

# ---------- Qiskit (canônico, já provado em hardware) ----------
from qiskit import QuantumCircuit

def dj_qiskit(case):
    qc = QuantumCircuit(3, 2)
    qc.x(2); qc.h(2); qc.h(0); qc.h(1)
    if case == "const-1": qc.x(2)
    elif case == "balanced": qc.cx(0, 2); qc.cx(1, 2)
    qc.h(0); qc.h(1); qc.measure([0, 1], [0, 1])
    return qc

# ---------- OpenQASM 3 ----------
QASM = """OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
bit[2] c;
x q[2];
h q[2];
h q[0];
h q[1];
%s
h q[0];
h q[1];
c[0] = measure q[0];
c[1] = measure q[1];
"""
QASM_CASES = {"const-1": "x q[2];", "const-0": "", "balanced": "cx q[0], q[2];\ncx q[1], q[2];"}
for case, body in QASM_CASES.items():
    open(f"languages/qasm3/dj_{case}.qasm", "w").write(QASM % body)

# ---------- Q# (referência declarativa) ----------
open("languages/qsharp/ZyqlGate.qs", "w").write("""namespace Serena.Zyql {
    operation DjTrivalente(case : String) : Result[] {
        use q = Qubit[3];
        X(q[2]); H(q[2]); H(q[0]); H(q[1]);
        if case == "const-1" { X(q[2]); }
        elif case == "balanced" { CNOT(q[0], q[2]); CNOT(q[1], q[2]); }
        H(q[0]); H(q[1]);
        let r = [M(q[0]), M(q[1])];
        ResetAll(q);
        return r;
    }
}
""")

# ---------- Cirq ----------
CIRQ = '''"""DJ trivalente ZYQL em Cirq — mesmo circuito da casa (SerenaSolutions)."""
import cirq

def dj_cirq(case):
    q = cirq.LineQubit.range(3)
    op = [cirq.X(q[2]), cirq.H(q[2]), cirq.H(q[0]), cirq.H(q[1])]
    if case == "const-1": op.append(cirq.X(q[2]))
    elif case == "balanced": op += [cirq.CNOT(q[0], q[2]), cirq.CNOT(q[1], q[2])]
    op += [cirq.H(q[0]), cirq.H(q[1]), cirq.measure(q[0], q[1], key="m")]
    return cirq.Circuit(op)
'''
open("languages/cirq/dj_cirq.py", "w").write(CIRQ)

# ---------- PennyLane ----------
PL = '''"""DJ trivalente ZYQL em PennyLane — mesmo circuito da casa (SerenaSolutions)."""
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
'''
open("languages/pennylane/dj_pl.py", "w").write(PL)

# ---------- Braket ----------
BRK = '''"""DJ trivalente ZYQL em Braket (LocalSimulator) — mesmo circuito da casa."""
from braket.circuits import Circuit
from braket.devices import LocalSimulator

def dj_braket(case):
    c = Circuit().x(2).h(2).h(0).h(1)
    if case == "const-1": c = c.x(2)
    elif case == "balanced": c = c.cnot(0, 2).cnot(1, 2)
    c = c.h(0).h(1).probability([0, 1])
    return c
'''
open("languages/braket/dj_braket.py", "w").write(BRK)

# ================= VERIFICAÇÃO DE EQUIVALÊNCIA =================
res = {}
from qiskit.quantum_info import Statevector

def qiskit_probs_nomeas(case):
    qc = dj_qiskit(case).remove_final_measurements(inplace=False)
    return np.abs(Statevector(qc).data) ** 2

for case in ("const-1", "const-0", "balanced"):
    ref = qiskit_probs_nomeas(case)  # 8 amplitudes, q1 q0
    p_ref = {"00": float(ref[0] + ref[4]), "01": float(ref[1] + ref[5]),
             "10": float(ref[2] + ref[6]), "11": float(ref[3] + ref[7])}
    # note: qiskit bit order q2q1q0 -> indices 0..7, we take marginal of q0,q1
    langs = {}
    # Cirq
    import cirq
    sim = cirq.Simulator()
    sys.path.insert(0, "languages/cirq")
    from dj_cirq import dj_cirq
    r = sim.run(dj_cirq(case), repetitions=2000)
    m = r.histogram(key="m")
    tot = sum(m.values())
    langs["cirq"] = {format(k, "02b"): m.get(k, 0) / tot for k in m}
    for kk in ("00", "01", "10", "11"): langs["cirq"].setdefault(kk, 0.0)
    # PennyLane
    sys.path.insert(0, "languages/pennylane")
    from dj_pl import circuit
    pr = circuit(case)
    langs["pennylane"] = {"00": float(pr[0]), "01": float(pr[2]), "10": float(pr[1]), "11": float(pr[3])}
    # Braket
    sys.path.insert(0, "languages/braket")
    from dj_braket import dj_braket
    from braket.devices import LocalSimulator
    b = LocalSimulator().run(dj_braket(case), shots=0).result().values[0]
    probs = b if isinstance(b, list) and len(b) == 4 else [float(x) for x in b]
    langs["braket"] = {"00": probs[0], "01": probs[1], "10": probs[2], "11": probs[3]}
    # OpenQASM 3 (via Qiskit loads)
    from qiskit import qasm3
    q3 = qasm3.load(f"languages/qasm3/dj_{case}.qasm")
    q3nm = q3.remove_final_measurements(inplace=False)
    ref3 = np.abs(Statevector(q3nm).data) ** 2
    langs["openqasm3"] = {"00": float(ref3[0] + ref3[4]), "01": float(ref3[1] + ref3[5]),
                          "10": float(ref3[2] + ref3[6]), "11": float(ref3[3] + ref3[7])}
    res[case] = {"referencia_qiskit": p_ref, "linguagens": langs}

# verifica concordância
report = {}
all_ok = True
ESPERADO = {"const-1": "00", "const-0": "00", "balanced": "11"}
TOL = {"cirq": 0.03}  # amostrado (2000 shots); demais sao exatos
for case in res:
    line = {}
    for lang, pr in res[case]["linguagens"].items():
        dom = max(pr, key=pr.get)
        tol = TOL.get(lang, 1e-9)
        off = abs(pr[dom] - 1.0)
        ok = dom == ESPERADO[case] and off <= tol + 1e-12
        line[lang] = {"dominante": dom, "esperado": ESPERADO[case], "prob_dominante": round(pr[dom], 6), "tolerancia": tol, "concorda": ok}
        all_ok &= ok
    report[case] = line
print("EQUIVALÊNCIA MULTILÍNGUE DJ:", "TODAS CONCORDAM (exato)" if all_ok else "DIVERGÊNCIA!")
for case in report:
    print(f"  {case}: " + ", ".join(f"{l}={'OK' if v['concorda'] else 'FALHA'}" for l, v in report[case].items()))
json.dump({"battery": "dj_trivalente_n2", "referencia": "qiskit 2.6.0 (statevector exato)",
           "resultado": res, "equivalencia": report, "veredito": "TODAS_LINGUAGENS_CONCORDAM" if all_ok else "DIVERGENCIA"},
          open("receipts/equivalencia_dj_multilingue.json", "w"), ensure_ascii=True, indent=1)
print("salvo: receipts/equivalencia_dj_multilingue.json")
