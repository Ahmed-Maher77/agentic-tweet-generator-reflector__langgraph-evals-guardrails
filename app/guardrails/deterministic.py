"""Deterministic input guardrails: length, formatting, and pattern-based security detection."""

import re
from dataclasses import dataclass
from typing import Any

from prompt_injection_sanitizer import (
    detect_injection_patterns,
    detect_leet_injection,
    detect_typoglycemia,
    normalize_text,
)

from app.config import Settings, get_settings
from app.guardrails.schemas import GuardrailCheckResult
from app.logging_config import get_logger

logger = get_logger(__name__)


# =====================================================================
# Targeted Application-Specific Security Policies (Small, Justified)
# =====================================================================
# Covers specific risks unique to an API-driven AI agent:
# 1. Secret / API key exfiltration attempts
# 2. Explicit security filter & guardrail disabling commands
# 3. Delimiter / chat template role injection tokens (<system>, [developer])
PROJECT_SPECIFIC_POLICIES: list[dict[str, Any]] = [
    {
        "category": "system_prompt_extraction",
        "pattern_name": "system_prompt_exfiltration",
        "pattern": re.compile(
            r"\b(?:reveal|show|print|leak|give|display|get|expose|repeat|output)\s+(?:me\s+)?(?:your\s+)?(?:system\s*prompt|initial\s*instructions|hidden\s*instructions|developer\s*message|developer\s*prompt)\b",
            re.IGNORECASE,
        ),
        "risk_level": "critical",
        "weight": 0.40,
    },
    {
        "category": "secret_extraction",
        "pattern_name": "api_key_exfiltration",
        "pattern": re.compile(
            r"\b(?:reveal|show|print|leak|give|display|get|expose)\s+(?:me\s+)?(?:your\s+)?(?:api\s*key|secret\s*key|token|password|credentials?|secret)\b",
            re.IGNORECASE,
        ),
        "risk_level": "critical",
        "weight": 0.40,
    },
    {
        "category": "guardrail_bypass",
        "pattern_name": "guardrail_deactivation",
        "pattern": re.compile(
            r"\b(?:disable|bypass|turn\s+off|deactivate|override|ignore)\s+(?:all\s+)?(?:the\s+)?(?:guardrails?|safety\s+filter|safety\s+checks?|system\s+rules?|restrictions?|policies)\b",
            re.IGNORECASE,
        ),
        "risk_level": "critical",
        "weight": 0.40,
    },
    {
        "category": "delimiter_injection",
        "pattern_name": "role_tag_injection",
        "pattern": re.compile(
            r"(?:<\s*(?:system|developer|assistant|admin)\s*>|\[\s*(?:system|developer|user|assistant|admin)\s*\])",
            re.IGNORECASE,
        ),
        "risk_level": "high",
        "weight": 0.30,
    },
]


@dataclass
class SecurityFinding:
    """Normalized security detection finding."""

    category: str
    pattern_name: str
    matched_text: str
    risk_level: str  # "critical", "high", "medium", "low"
    risk_weight: float


def run_deterministic_security_detector(
    user_query: str,
) -> tuple[list[SecurityFinding], float]:
    """Run comprehensive offline, deterministic security analysis.

    Techniques:
    1. NFKC Unicode normalization, homoglyph de-aliasing, and zero-width character removal.
    2. Comprehensive prompt injection regex pattern detection via `prompt-injection-sanitizer`.
    3. Leet-speak obfuscation de-aliasing detection.
    4. Typoglycemia (character scrambling / fuzzy matching) detection.
    5. Project-specific rule detection (secret exfiltration, explicit guardrail bypasses, delimiter injection).
    6. Aggregate risk score calculation.
    """
    findings: list[SecurityFinding] = []

    # 1. Unicode & Homoglyph Normalization
    normalized = normalize_text(user_query)

    # 2. Injection Pattern Detection (Standard, Leet, and Typoglycemia)
    detected_patterns = detect_injection_patterns(user_query)
    leet_patterns = detect_leet_injection(user_query)
    # Filter typoglycemia matches: exclude bare "system prompt" nouns without injection intent
    typo_patterns = [
        p
        for p in detect_typoglycemia(user_query)
        if p.risk_level in ("critical", "high") and p.pattern_name != "typoglycemia_phrase:system_prompt"
    ]

    all_pkg_patterns = detected_patterns + leet_patterns + typo_patterns

    for pat in all_pkg_patterns:
        # Categorize pattern accurately
        category = "prompt_injection"
        name = pat.pattern_name.lower()
        if "role_tag" in name or "delimiter" in name or "tag_injection" in name:
            category = "delimiter_injection"
        elif "system_prompt" in name or "developer" in name:
            category = "system_prompt_extraction"
        elif "pretend" in name or "role" in name or "mode" in name:
            category = "role_manipulation"
        elif "leet" in name or "typoglycemia" in name:
            category = "obfuscated_injection"

        weight = 0.40 if pat.risk_level == "critical" else (0.25 if pat.risk_level == "high" else 0.15)
        findings.append(
            SecurityFinding(
                category=category,
                pattern_name=pat.pattern_name,
                matched_text=pat.matched_text,
                risk_level=pat.risk_level,
                risk_weight=weight,
            )
        )

    # 3. Project-Specific Security Policies
    for policy in PROJECT_SPECIFIC_POLICIES:
        match = policy["pattern"].search(normalized)
        if match:
            findings.append(
                SecurityFinding(
                    category=policy["category"],
                    pattern_name=policy["pattern_name"],
                    matched_text=match.group(0),
                    risk_level=policy["risk_level"],
                    risk_weight=policy["weight"],
                )
            )

    # 4. Calculate Aggregate Risk Score
    if not findings:
        return [], 0.0

    # Sum distinct finding weights up to 1.0
    total_score = min(1.0, sum(f.risk_weight for f in findings))
    return findings, total_score


def evaluate_security_policy(
    findings: list[SecurityFinding],
    risk_score: float,
    threshold: float = 0.20,
) -> tuple[bool, str | None, str | None, str | None]:
    """Decoupled policy evaluator: Translates detection findings into ALLOW / BLOCK decision.

    Returns:
        Tuple of (passed: bool, reason: str | None, category: str | None, highest_risk: str | None).
    """
    if not findings or risk_score < threshold:
        return True, None, None, None

    # Determine highest risk level
    risk_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    highest_finding = max(findings, key=lambda f: risk_order.get(f.risk_level, 0))

    category = highest_finding.category
    reason = (
        f"Input query contains prohibited adversarial instructions or injection attempts: "
        f"detected {category.replace('_', ' ')} (risk: {highest_finding.risk_level}, score: {risk_score:.2f})."
    )
    return False, reason, category, highest_finding.risk_level


def check_deterministic_input(
    user_query: str,
    settings: Settings | None = None,
) -> GuardrailCheckResult:
    """Run fast deterministic checks on the incoming user query.

    Checks:
    1. Empty or whitespace-only string
    2. Maximum character length limit
    3. Multi-layer deterministic security analysis (Unicode, Obfuscation, Injections, Secret leaks)
    """
    cfg = settings or get_settings()

    # 1. Non-empty check
    if not user_query or not user_query.strip():
        return GuardrailCheckResult(
            passed=False,
            reason="Input query cannot be empty or whitespace-only.",
            check_name="non_empty_check",
            category="validation_error",
            risk_level="critical",
            risk_score=1.0,
        )

    # 2. Length check
    if len(user_query) > cfg.max_input_length:
        return GuardrailCheckResult(
            passed=False,
            reason=f"Input query length ({len(user_query)}) exceeds maximum allowed limit ({cfg.max_input_length}).",
            check_name="length_check",
            category="validation_error",
            risk_level="medium",
            risk_score=0.5,
        )

    # 3. Deterministic Security Detection & Policy Evaluation
    try:
        findings, risk_score = run_deterministic_security_detector(user_query)
        passed, reason, category, risk_level = evaluate_security_policy(
            findings=findings,
            risk_score=risk_score,
            threshold=cfg.deterministic_risk_threshold,
        )

        if not passed:
            logger.warning(
                "deterministic_security_policy_block",
                category=category,
                risk_level=risk_level,
                risk_score=risk_score,
                findings_count=len(findings),
            )
            return GuardrailCheckResult(
                passed=False,
                reason=reason or "Input query contains prohibited adversarial instructions or injection attempts.",
                check_name="deterministic_security_check",
                category=category,
                risk_level=risk_level,
                risk_score=risk_score,
            )
    except Exception as exc:
        logger.error("deterministic_detector_exception", error=str(exc))

    return GuardrailCheckResult(
        passed=True,
        reason=None,
        check_name="deterministic_input_checks",
        risk_score=0.0,
    )
