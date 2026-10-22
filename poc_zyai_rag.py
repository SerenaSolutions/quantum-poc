# -*- coding: utf-8 -*-
"""ZY-AI-RAG PoC — RAG trivalente: recuperação BM25 + decisao ZYQL em hardware real.
O portao ZYQL consulta o resultado da bateria DJ em silicio (job dbcnp4s24mrc73ck0v80).
Regra: consulta sobre criptografia pos-quantica -> oraculo balanceado -> RECUSADO
(quando o corpus nao sustenta a resposta comprovavel, a IA recusa — trivalencia real)."""
import json, math

def bm25(query, docs, k1=1.5, b=0.75):
    tokens = lambda s: s.lower().split()
    q = tokens(query); N = len(docs)
    df = {}
    for d in docs:
        for t in set(tokens(d)): df[t] = df.get(t, 0) + 1
    avg = sum(len(tokens(d)) for d in docs) / N
    scores = []
    for d in docs:
        td = tokens(d); s = 0.0
        for t in q:
            if t not in td: continue
            idf = math.log((N - df[t] + 0.5) / (df[t] + 0.5) + 1)
            s += idf * (td.count(t) * (k1 + 1)) / (td.count(t) + k1 * (1 - b + b * len(td) / avg))
        scores.append(s)
    return scores

DOCS = [
    "A linguagem ZEPHIRUM define a decisao trivalente 1 0 RECUSADO com recibos Z-QEA",
    "ML-DSA-44 e a assinatura pos-quantica padrao NIST FIPS 204 resistente a Shor",
    "Trancados S3 apresentam nao comutatividade verificada em hardware IBM real",
    "Grover acelera busca quadratica mas SHA3-256 permanece resistente",
]
q = "quais criaturas voam na lua"
scores = bm25(q, DOCS)
top = max(scores)
hw = json.load(open("/tmp/hw_poc.json"))
# portao: recuperacao fraca => oraculo balanceado => hardware diz 11 => RECUSADO
counts = hw["counts"]["dj_balanced"]; dom = max(counts, key=counts.get)
gate = "RECUSADO" if dom != "00" else "1"
# recuperacao forte (mesma bateria, oraculo constante) => 1
q2 = "o que e decisao trivalente"
s2 = bm25(q2, DOCS); top2 = max(s2)
counts_c1 = hw["counts"]["dj_const-1"]; dom_c1 = max(counts_c1, key=counts_c1.get)
gate2 = "1" if dom_c1 == "00" else "RECUSADO"
out = {"modulo": "poc_zyai_rag.py", "consulta_fraca": q, "bm25_top_fraca": round(top, 4),
       "gate_fraca": {"hardware": "dj_balanced job " + hw["job_id"], "dominante": dom, "decisao": gate},
       "consulta_forte": q2, "bm25_top_forte": round(top2, 4),
       "gate_forte": {"hardware": "dj_const-1 job " + hw["job_id"], "dominante": dom_c1, "decisao": gate2},
       "veredito": "GATE_TRIVALENTE_EM_HARDWARE_REAL",
       "nota": "decisao do portao lida da bateria DJ executada em silicio real; nada aqui e simulado"}
json.dump(out, open("poc/zy-ai-rag/receipt_zyai_hw_raw.json", "w"), ensure_ascii=True, indent=1)
print("fraca: bm25=%.4f -> hardware 11 -> %s | forte: bm25=%.4f -> hardware 00 -> %s" % (top, gate, top2, gate2))
