"""Shared financial-risk assessment for VAJRA Trust Intelligence.

Every detection result maps to a risk level plus an actionable response
playbook, per the PS: "create an actionable path for review, reporting,
or response" for financial communications.
"""

from typing import Dict, List, Tuple

RISK_LEVELS = ("CRITICAL", "HIGH", "MEDIUM", "LOW")

_PLAYBOOK: Dict[str, List[str]] = {
    "CRITICAL": [
        "Do NOT act on any payment or transfer instruction in this media.",
        "Call back the sender on an independently verified number (out-of-band).",
        "Escalate to the fraud desk / compliance team immediately.",
        "Quarantine the file and preserve the original for evidence.",
        "File an incident report with message headers and metadata.",
    ],
    "HIGH": [
        "Pause any transaction linked to this communication.",
        "Verify the sender through a second, independent channel.",
        "Get a second analyst review before acting on it.",
        "Preserve the original file for the audit trail.",
    ],
    "MEDIUM": [
        "Treat this content as UNVERIFIED — do not rely on it alone.",
        "Request the original source file directly from the sender.",
        "Re-scan if a higher-quality original becomes available.",
    ],
    "LOW": [
        "No manipulation detected — proceed with standard controls.",
        "Retain this report for the audit trail.",
    ],
}


def assess(verdict: str, fake_prob: float) -> Tuple[str, List[str]]:
    """Map (verdict, P(fake)) to (risk_level, recommended_actions)."""
    v = (verdict or "").upper()
    try:
        p = float(fake_prob)
    except (TypeError, ValueError):
        p = 0.5
    if v == "FAKE":
        level = "CRITICAL" if p >= 0.8 else "HIGH"
    else:
        level = "LOW" if p <= 0.2 else "MEDIUM"
    return level, list(_PLAYBOOK[level])


def attach(result: Dict) -> Dict:
    """Add risk_level + recommended_actions to a detection result dict."""
    verdict = result.get("verdict") or result.get("decision", "unknown")
    fake_prob = result.get("fake_prob", result.get("score", 0.5))
    level, actions = assess(verdict, fake_prob)
    result["risk_level"] = level
    result["recommended_actions"] = actions
    return result
