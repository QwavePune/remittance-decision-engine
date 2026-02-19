from __future__ import annotations

from typing import Dict

try:
    from agents import function_tool
except Exception:  # pragma: no cover - placeholder for local environment
    def function_tool(fn):  # type: ignore
        return fn


@function_tool
def sanctions_screen(entity_id: str) -> Dict[str, float]:
    """
    Deterministic sanctions screening tool.
    Replace with your sanctions provider integration.
    """
    return {"match": 0.0, "confidence": 0.0}


@function_tool
def pep_screen(entity_id: str) -> Dict[str, float]:
    """
    Deterministic PEP screening tool.
    Replace with your PEP provider integration.
    """
    return {"match": 0.0, "confidence": 0.0}


@function_tool
def adverse_media_screen(entity_id: str) -> Dict[str, float]:
    """
    Deterministic adverse media screening tool.
    Replace with your adverse media provider integration.
    """
    return {"match": 0.0, "confidence": 0.0}


@function_tool
def device_reputation(device_id: str) -> Dict[str, float]:
    """
    Deterministic device reputation lookup.
    Replace with your device intelligence provider integration.
    """
    return {"score": 0.0}


@function_tool
def kyc_risk(sender_id: str, recipient_id: str) -> Dict[str, float]:
    """
    Deterministic KYC risk scoring.
    Replace with your KYC provider integration.
    """
    return {"sender_score": 0.0, "recipient_score": 0.0}


@function_tool
def ml_fraud_score(features: Dict[str, float]) -> Dict[str, float]:
    """
    Deterministic ML fraud/AML scoring.
    Replace with your model inference service.
    """
    return {"score": 0.0}
