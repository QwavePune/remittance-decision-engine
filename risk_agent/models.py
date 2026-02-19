from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecommendedAction(str, Enum):
    ALLOW = "ALLOW"
    HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"
    BLOCK = "BLOCK"


class TransactionContext(BaseModel):
    transaction_id: str
    corridor: str = Field(..., description="Expected values: US-IN or UK-IN")
    amount: float
    currency: str
    sender_id: str
    recipient_id: str
    sender_country: str
    recipient_country: str
    sender_kyc_status: str
    recipient_kyc_status: str
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    payment_rail: Optional[str] = None
    created_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FeatureSet(BaseModel):
    sanctions_match: bool
    sanctions_confidence: float
    pep_match: bool
    adverse_media_match: bool
    velocity_7d: int
    velocity_24h: int
    corridor_risk_score: float
    device_reputation_score: float
    kyc_risk_score: float
    historical_chargebacks_90d: int
    provenance: Dict[str, str]


class RuleEvaluation(BaseModel):
    hard_blocks: List[str]
    rule_score: float
    rule_reasons: List[str]


class ModelEvaluation(BaseModel):
    model_score: float
    model_reasons: List[str]
    model_version: str


class ReasonCode(BaseModel):
    code: str
    weight: float


class DecisionOutput(BaseModel):
    transaction_id: str
    risk_score: float
    risk_level: RiskLevel
    recommended_action: RecommendedAction
    reasons: List[ReasonCode]
    hard_blocks: List[str]
    explanation: str
    model_versions: Dict[str, str]
    audit: Dict[str, str]


class DecisionPackage(BaseModel):
    input: TransactionContext
    features: FeatureSet
    rules: RuleEvaluation
    model: ModelEvaluation
    output: DecisionOutput


class RiskSignal(BaseModel):
    reasons: List[ReasonCode]
    narrative: str


class Explanation(BaseModel):
    explanation: str
