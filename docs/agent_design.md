# Remittance Risk/AML Agent Design (US/UK -> India)

## Goals
- Deliver deterministic risk scores with explainable, compliance-safe reasoning.
- Support real-time scoring (p95 100 ms target) and batch decisioning.
- Preserve full auditability: evidence, model versions, rules, agent traces.

## Scope
- Corridors: US -> IN, UK -> IN
- Outputs: risk score + recommended action (ALLOW, HOLD_FOR_REVIEW, BLOCK)

## End-to-End Flow (Online)
1. Ingress validates a strict TransactionContext schema.
2. Deterministic enrichment (sanctions/PEP/adverse media, KYC, device, velocity).
3. Rules engine applies hard blocks and adds rule score.
4. ML model produces a fraud/AML score.
5. Blend rule + ML into final score.
6. Agent layer generates reason codes and a short explanation.
7. Decision package + audit metadata are persisted to an immutable ledger.

## Batch Flow
- Accept a JSONL file of transactions.
- Bulk-enrich and score with the same pipeline.
- LLM explanations can be limited to high-risk items to control cost.
- Write JSONL of decision packages, plus a manifest for audit.

## Deterministic vs LLM Responsibilities
- Deterministic: rules, ML scoring, sanctions and KYC checks.
- LLM: explanation generation, evidence summarization, reason code narrative.

## Compliance and Auditability
- Version rules/models/features/prompts with each decision.
- Store tool inputs/outputs, agent traces, and reason codes in an immutable store.
- Restrict LLM access to minimal fields; never expose full PII if not required.

## Latency Strategy (p95 100 ms)
- Cache corridor-level and static lists (sanctions, PEP index).
- Keep enrichers and model inference local or on low-latency endpoints.
- Allow explanation generation to be toggled to async later.

## Interfaces
- `score_transaction(txn)` for real-time.
- `score_batch_file(input_jsonl, output_jsonl)` for daily batch.
