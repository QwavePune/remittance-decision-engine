from __future__ import annotations

from .models import FeatureSet, TransactionContext
from .tools import (
    adverse_media_screen,
    device_reputation,
    kyc_risk,
    pep_screen,
    sanctions_screen,
)


def build_features(txn: TransactionContext) -> FeatureSet:
    sanctions = sanctions_screen(txn.sender_id)
    pep = pep_screen(txn.sender_id)
    adverse = adverse_media_screen(txn.sender_id)
    device = device_reputation(txn.device_id or "unknown")
    kyc = kyc_risk(txn.sender_id, txn.recipient_id)

    return FeatureSet(
        sanctions_match=sanctions["match"] > 0.5,
        sanctions_confidence=float(sanctions["confidence"]),
        pep_match=pep["match"] > 0.5,
        adverse_media_match=adverse["match"] > 0.5,
        velocity_7d=0,
        velocity_24h=0,
        corridor_risk_score=0.0,
        device_reputation_score=float(device["score"]),
        kyc_risk_score=max(float(kyc["sender_score"]), float(kyc["recipient_score"])),
        historical_chargebacks_90d=0,
        provenance={
            "sanctions": "PROVIDER_SANCTIONS",
            "pep": "PROVIDER_PEP",
            "adverse": "PROVIDER_ADVERSE",
            "device": "PROVIDER_DEVICE",
            "kyc": "PROVIDER_KYC",
        },
    )
