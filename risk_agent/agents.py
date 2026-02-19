from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from .config import AgentConfig
from .models import Explanation, RiskSignal

try:
    from agents import Agent, Runner, input_guardrail, GuardrailResult, GuardrailTripwireTriggered
except Exception:  # pragma: no cover - placeholder for local environment
    Agent = object  # type: ignore
    Runner = object  # type: ignore

    class GuardrailResult:  # type: ignore
        def __init__(self, output: Any, tripwire_triggered: bool = False):
            self.output = output
            self.tripwire_triggered = tripwire_triggered

    class GuardrailTripwireTriggered(Exception):
        pass

    def input_guardrail(fn):  # type: ignore
        return fn


@input_guardrail
def corridor_guardrail(input_data: Dict[str, Any]) -> GuardrailResult:
    corridor = input_data.get("corridor")
    ok = corridor in {"US-IN", "UK-IN"}
    return GuardrailResult(output=input_data, tripwire_triggered=not ok)


@dataclass
class AgentBundle:
    fraud_agent: Any
    aml_agent: Any
    explain_agent: Any


def build_agents(config: AgentConfig) -> AgentBundle:
    fraud_agent = Agent(
        name="Fraud Risk Agent",
        model=config.fraud_model,
        instructions=(
            "Analyze fraud and behavioral risk signals using provided features. "
            "Return reason codes and a short narrative. Do not assign the final score."
        ),
        output_type=RiskSignal,
        input_guardrails=[corridor_guardrail],
    )

    aml_agent = Agent(
        name="AML Compliance Agent",
        model=config.aml_model,
        instructions=(
            "Analyze AML and compliance risk signals (sanctions, PEP, adverse media, corridor risk). "
            "Return reason codes and a short narrative. Do not assign the final score."
        ),
        output_type=RiskSignal,
        input_guardrails=[corridor_guardrail],
    )

    explain_agent = Agent(
        name="Explainability Agent",
        model=config.explain_model,
        instructions=(
            "Produce a compliance-safe explanation for the final score and action. "
            "Use only provided evidence and reason codes. Do not change scores."
        ),
        output_type=Explanation,
        input_guardrails=[corridor_guardrail],
    )

    return AgentBundle(
        fraud_agent=fraud_agent,
        aml_agent=aml_agent,
        explain_agent=explain_agent,
    )


def run_fraud_signal(agent: Any, payload: Dict[str, Any]) -> RiskSignal:
    result = Runner.run_sync(agent, input=payload)
    return result.output


def run_aml_signal(agent: Any, payload: Dict[str, Any]) -> RiskSignal:
    result = Runner.run_sync(agent, input=payload)
    return result.output


def run_explanation(agent: Any, payload: Dict[str, Any]) -> Explanation:
    result = Runner.run_sync(agent, input=payload)
    return result.output
