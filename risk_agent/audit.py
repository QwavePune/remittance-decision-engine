from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from .config import AgentConfig


def build_audit_metadata(config: AgentConfig, trace_id: str) -> Dict[str, str]:
    return {
        "trace_id": trace_id,
        "policy_version": config.policy_version,
        "features_version": config.features_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
