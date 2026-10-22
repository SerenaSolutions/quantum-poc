# ⚛️ Quantum PoC — Provas de Conceito dos 5 Apps da Serena Solutions

**Os 5 apps do [GitHub Marketplace](https://github.com/marketplace?query=SerenaSolutions) confrontados com as linguagens quânticas do mercado — e executados no computador quântico real da IBM.**

- **Hardware:** IBM Quantum `ibm_marrakesh` — job [`dbcnp4s24mrc73ck0v80`](https://quantum.cloud.ibm.com) (512 shots reais)
- **Selagem:** todos os recibos são Z-QEA v2 — SHA3-256 + assinatura pós-quântica **ML-DSA-44 (FIPS 204, NIST)** + entropia atestada nascida em hardware quântico
- **Regra da casa:** nenhuma prova silenciosa — tudo tem recibo, tudo é verificável offline

## Confronto com as linguagens quânticas

O MESMO circuito da decisão trivalente ZYQL (Deutsch-Jozsa n=2) foi escrito e executado em:

| Linguagem / SDK | Versão | Onde rodou | Resultado |
|---|---|---|---|
| **Qiskit** | 2.6.0 | simulação exata + hardware real | concorda ✔ |
| **OpenQASM 3** | 3.0 | as fontes `.qasm` foram carregadas, transpiladas e executadas no silício da IBM | concorda ✔ |
| **Cirq** | 1.7.0 | simulação (2000 shots) | concorda ✔ |
| **PennyLane** | 0.45.1 | simulador default.qubit | concorda ✔ |
| **Braket SDK** | LocalSimulator | probabilidade exata | concorda ✔ |
| **Q#** | fonte `.qs` | referência declarativa (Azure Quantum) | mesmo circuito ✔ |

**Veredito da equivalência (recibo selado):** `TODAS_AS_LINGUAGENS_CONCORDAM_EXATAMENTE` — os 3 casos (const-1 → 1, const-0 → 0, balanced → RECUSADO) dão o mesmo resultado dominante em todas as linguagens.

## Resultados no hardware real (job `dbcnp4s24mrc73ck0v80`)

| Circuito (fonte) | Dominante | p | Decisão ZYQL |
|---|---|---|---|
| `dj_const-1` (OpenQASM 3) | `00` | 0.996 | **1** |
| `dj_const-0` (OpenQASM 3) | `00` | 0.994 | **0** |
| `dj_balanced` (OpenQASM 3) | `11` | 0.898 | **RECUSADO** |
| `(B_R B_S)²` (Z-Anyon Lab) | `01` | 0.979 | ordem importa ✔ |
| `(B_S B_R)²` (Z-Anyon Lab) | `10` | 0.984 | ordem importa ✔ |

Os trançados S3 dão **dominantes distintos** no silício — a não-comutatividade é física real, não simulação.

## Provas por app (recibos selados com ML-DSA-44)

| App | Prova | Recibo |
|---|---|---|
| **ZQ-GATE** | bateria trivalente completa em hardware | `poc/zq-gate/receipt_zqgate_hw.json` |
| **Z-Anyon Lab** | palavras de trançado divergentes em hardware | `poc/z-anyon-lab/receipt_anyon_hw.json` |
| **ZY-AI-RAG** | porta ZYQL com BM25: consulta fraca → RECUSADO, forte → 1 (decisões lidas do hardware) | `poc/zy-ai-rag/receipt_zyai_hw.json` |
| **Z-QEA Receipt Sealer** | selou as 6 provas com ML-DSA-44 + entropia quântica atestada | `poc/zqea-sealer/receipt_sealer_poc.json` |
| **Z-QEA Receipt Verifier** | bateria em modo estrito: 6/6 selos + assinaturas válidos; fraude recusada nas duas camadas | `poc/zqea-verifier/verification_log.json` |

## Verifique você mesmo

```bash
pip install pqcrypto
git clone https://github.com/SerenaSolutions/quantum-poc.git
cd quantum-poc
python3 zqea_verify.py poc/zq-gate/receipt_zqgate_hw.json --strict-pq
```

Sem servidor, sem chave, sem confiança cega: a chave pública ML-DSA-44 vem dentro de cada recibo.

---
*Serena Quantum Solutions — nada silencioso, tudo com recibo. Sem endosso da IBM; os jobs são públicos e os recibos carregam o job ID.*
