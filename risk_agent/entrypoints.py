from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .agents import build_agents, run_aml_signal, run_explanation, run_fraud_signal
from .audit import build_audit_metadata
from .config import DEFAULT_CONFIG, AgentConfig
from .decisioning import blend_scores, evaluate_model, evaluate_rules
from .features import build_features
from .models import (
    DecisionOutput,
    DecisionPackage,
    ReasonCode,
    RecommendedAction,
    RiskLevel,
    TransactionContext,
)
from .tools import ml_fraud_score


def _risk_level(score: float) -> RiskLevel:
    if score >= 70.0:
        return RiskLevel.HIGH
    if score >= 30.0:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def _recommended_action(score: float, hard_blocks: List[str]) -> RecommendedAction:
    if hard_blocks:
        return RecommendedAction.BLOCK
    if score >= 70.0:
        return RecommendedAction.HOLD_FOR_REVIEW
    if score >= 30.0:
        return RecommendedAction.HOLD_FOR_REVIEW
    return RecommendedAction.ALLOW


def score_transaction(
    txn: TransactionContext,
    config: AgentConfig = DEFAULT_CONFIG,
    trace_id: str = "TRACE_PLACEHOLDER",
) -> DecisionPackage:
    agents = build_agents(config)

    features = build_features(txn)
    rule_eval = evaluate_rules(features)
    model_score = ml_fraud_score(features.model_dump())["score"]
    model_eval = evaluate_model(model_score, model_version="MODEL_VERSION_PLACEHOLDER")
    final_score, reason_codes = blend_scores(rule_eval, model_eval)

    fraud_signal = run_fraud_signal(
        agents.fraud_agent,
        {
            "corridor": txn.corridor,
            "features": features.model_dump(),
            "rule_reasons": rule_eval.rule_reasons,
            "model_reasons": model_eval.model_reasons,
        },
    )
    aml_signal = run_aml_signal(
        agents.aml_agent,
        {
            "corridor": txn.corridor,
            "features": features.model_dump(),
            "rule_reasons": rule_eval.rule_reasons,
            "model_reasons": model_eval.model_reasons,
        },
    )

    combined_reason_codes = reason_codes + [
        r.code for r in fraud_signal.reasons
    ] + [r.code for r in aml_signal.reasons]

    explanation = run_explanation(
        agents.explain_agent,
        {
            "corridor": txn.corridor,
            "score": final_score,
            "risk_level": _risk_level(final_score).value,
            "action": _recommended_action(final_score, rule_eval.hard_blocks).value,
            "reasons": combined_reason_codes,
            "evidence": {
                "features": features.model_dump(),
                "rules": rule_eval.model_dump(),
                "model": model_eval.model_dump(),
            },
        },
    )

    output = DecisionOutput(
        transaction_id=txn.transaction_id,
        risk_score=final_score,
        risk_level=_risk_level(final_score),
        recommended_action=_recommended_action(final_score, rule_eval.hard_blocks),
        reasons=[ReasonCode(code=code, weight=0.1) for code in combined_reason_codes],
        hard_blocks=rule_eval.hard_blocks,
        explanation=explanation.explanation,
        model_versions={
            "rules": config.rules_version,
            "ml_model": model_eval.model_version,
            "llm": config.explain_model,
        },
        audit=build_audit_metadata(config, trace_id=trace_id),
    )

    return DecisionPackage(
        input=txn,
        features=features,
        rules=rule_eval,
        model=model_eval,
        output=output,
    )


def score_batch(
    transactions: Iterable[TransactionContext],
    config: AgentConfig = DEFAULT_CONFIG,
    trace_id: str = "TRACE_PLACEHOLDER",
) -> List[DecisionPackage]:
    return [score_transaction(txn, config=config, trace_id=trace_id) for txn in transactions]


def score_batch_file(
    input_path: Path,
    output_path: Path,
    config: AgentConfig = DEFAULT_CONFIG,
    trace_id: str = "TRACE_PLACEHOLDER",
) -> None:
    decisions: List[DecisionPackage] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            txn = TransactionContext.model_validate_json(line)
            decisions.append(score_transaction(txn, config=config, trace_id=trace_id))

    with output_path.open("w", encoding="utf-8") as handle:
        for decision in decisions:
            handle.write(decision.model_dump_json())
            handle.write("\n")
