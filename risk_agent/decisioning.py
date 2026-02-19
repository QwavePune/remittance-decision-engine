from __future__ import annotations

from typing import List, Tuple

from .models import FeatureSet, ModelEvaluation, RuleEvaluation


def evaluate_rules(features: FeatureSet) -> RuleEvaluation:
    hard_blocks: List[str] = []
    rule_reasons: List[str] = []
    rule_score = 0.0

    if features.sanctions_match and features.sanctions_confidence >= 0.9:
        hard_blocks.append("SANCTIONS_MATCH_CONFIDENCE>=0.9")
        rule_score = 100.0
        rule_reasons.append("SANCTIONS_MATCH")

    if features.velocity_24h > 10:
        rule_score += 15.0
        rule_reasons.append("VELOCITY_SPIKE_24H")

    if features.corridor_risk_score >= 0.7:
        rule_score += 10.0
        rule_reasons.append("CORRIDOR_RISK")

    return RuleEvaluation(
        hard_blocks=hard_blocks,
        rule_score=min(rule_score, 100.0),
        rule_reasons=rule_reasons,
    )


def evaluate_model(model_score: float, model_version: str) -> ModelEvaluation:
    reasons = []
    if model_score >= 0.8:
        reasons.append("MODEL_HIGH_RISK")
    elif model_score >= 0.5:
        reasons.append("MODEL_MEDIUM_RISK")
    return ModelEvaluation(
        model_score=model_score,
        model_reasons=reasons,
        model_version=model_version,
    )


def blend_scores(rule_eval: RuleEvaluation, model_eval: ModelEvaluation) -> Tuple[float, List[str]]:
    if rule_eval.hard_blocks:
        return 100.0, rule_eval.rule_reasons + model_eval.model_reasons

    blended = min(rule_eval.rule_score + (model_eval.model_score * 100.0 * 0.7), 100.0)
    return blended, rule_eval.rule_reasons + model_eval.model_reasons
