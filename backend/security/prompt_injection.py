"""Prompt injection detection and sanitization for AI request validation."""

import re
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class SecurityCheckResult:
    is_safe: bool
    reason: str
    risk_score: float
    detected_patterns: List[str]


class PromptInjectionDefense:
    """Comprehensive prompt injection defense system."""

    INJECTION_PATTERNS = {
        "instruction_override": [
            r"(?i)ignore (previous|above|all) instructions",
            r"(?i)forget (your|the) (instructions|training)",
            r"(?i)disregard (previous|all|system) prompts",
            r"(?i)override (system|safety|security) constraints",
        ],
        "role_manipulation": [
            r"(?i)you are now (acting as|pretending to be)",
            r"(?i)your new (role|identity|persona) is",
            r"(?i)from now on (you|you're) (are|will be)",
            r"(?i)assume the (role|identity|persona) of",
        ],
        "data_exfiltration": [
            r"(?i)output (sensitive|private|confidential|internal) data",
            r"(?i)reveal (your|the) (system|training) (prompt|data)",
            r"(?i)show (me|us) (everything|all details) about",
        ],
        "jailbreak_attempts": [
            r"(?i)jailbreak",
            r"(?i)unrestricted mode",
            r"(?i)developer mode",
            r"(?i)no (restrictions|limitations|filters)",
            r"(?i)bypass (safety|security|ethical) (measures|controls)",
        ],
    }

    ESCAPE_SEQUENCES = [r"\\n", r"\\t", r"\\r", r"\\b", r"\\f", r"\\x[0-9a-fA-F]{2}", r"\\u[0-9a-fA-F]{4}"]

    def __init__(self) -> None:
        self.compiled_patterns = {
            category: [re.compile(pattern) for pattern in patterns]
            for category, patterns in self.INJECTION_PATTERNS.items()
        }

    def validate_prompt(self, prompt: str, context: Dict[str, Any] = None) -> SecurityCheckResult:
        detected_patterns: List[str] = []
        risk_score = 0.0
        warnings: List[str] = []
        context = context or {}

        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(prompt)
                if matches:
                    detected_patterns.extend(matches)
                    risk_score += len(matches) * 0.2
                    warnings.append(f"{category}: {matches[0]}")

        escape_matches = re.findall(r"|".join(self.ESCAPE_SEQUENCES), prompt)
        if escape_matches:
            risk_score += len(escape_matches) * 0.15
            warnings.append("Escaped sequences detected")

        special_chars = re.findall(r"[^a-zA-Z0-9\s.,!?]", prompt)
        if len(special_chars) > len(prompt) * 0.1:
            risk_score += 0.2
            warnings.append("Excessive special characters")

        token_boundaries = re.findall(r"<<|>>|[[\]]|{{|}}", prompt)
        if token_boundaries:
            risk_score += len(token_boundaries) * 0.05
            warnings.append("Token boundary manipulation")

        risk_score += self._contextual_validation(prompt, context)
        is_safe = risk_score < 0.5

        return SecurityCheckResult(
            is_safe=is_safe,
            reason=f"Risk score: {risk_score:.2f}. {'Safe' if is_safe else 'Blocked'}",
            risk_score=risk_score,
            detected_patterns=detected_patterns,
        )

    def _contextual_validation(self, prompt: str, context: Dict[str, Any]) -> float:
        extra_risk = 0.0
        context_keywords = ["context", "system prompt", "instruction", "template"]
        for keyword in context_keywords:
            if keyword in prompt.lower():
                extra_risk += 0.1

        for key, value in context.items():
            if str(value) in prompt:
                extra_risk += 0.1

        return extra_risk

    def sanitize_prompt(self, prompt: str) -> str:
        prompt = re.sub(r'```(\w+)?[\s\S]*?```', '[CODE_BLOCK]', prompt)
        prompt = prompt.replace('{{', '{ {').replace('}}', '} }')
        prompt = prompt.replace('<<', '< <').replace('>>', '> >')
        return prompt
