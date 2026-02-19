from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentConfig:
    coordinator_model: str = "MODEL_COORDINATOR"
    fraud_model: str = "MODEL_FRAUD"
    aml_model: str = "MODEL_AML"
    explain_model: str = "MODEL_EXPLAIN"
    rules_version: str = "ruleset_v1.0"
    policy_version: str = "policy_2026_02"
    features_version: str = "feat_v1.0"


DEFAULT_CONFIG = AgentConfig()
