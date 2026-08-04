"""Security controls for the enterprise RAG pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
import re


@dataclass
class DocumentSecurityCheck:
    is_safe: bool
    risk_level: str
    contains_pii: bool
    contains_ph: bool
    contains_confidential: bool
    sensitive_patterns: List[str]


class RAGSecurity:
    """Validate and sanitize documents before they reach the model."""

    PII_PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "address": r"\b\d{1,5}\s\w+\s\w+",
        "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
        "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    }

    CONFIDENTIAL_PATTERNS = {
        "internal_team": r"(?i)(internal|confidential|secret|restricted)",
        "project_codes": r"[A-Z]{2,4}-\d{3,5}",
    }

    def __init__(self, tenant_id: str, data_boundaries: Dict[str, Any]):
        self.tenant_id = tenant_id
        self.data_boundaries = data_boundaries
        self.pii_regex = {name: re.compile(pattern) for name, pattern in self.PII_PATTERNS.items()}
        self.confidential_regex = {
            name: re.compile(pattern)
            for name, pattern in self.CONFIDENTIAL_PATTERNS.items()
        }

    def validate_retrieved_documents(self, documents: List[Dict[str, Any]]) -> List[DocumentSecurityCheck]:
        """Return a security summary for each document chunk."""
        results: List[DocumentSecurityCheck] = []

        for doc in documents:
            text = doc.get("text", doc.get("content", ""))
            pii_found = self._check_pii(text)
            phi_found = self._check_phi(text)
            confidential_found = self._check_confidential(text)
            boundary_violation = self._check_data_boundaries(doc)

            risk_level = self._assess_risk_level(pii_found, phi_found, confidential_found, boundary_violation)
            is_safe = risk_level != "HIGH" and not pii_found and not phi_found and not boundary_violation

            results.append(
                DocumentSecurityCheck(
                    is_safe=is_safe,
                    risk_level=risk_level,
                    contains_pii=pii_found,
                    contains_ph=phi_found,
                    contains_confidential=confidential_found,
                    sensitive_patterns=self._get_sensitive_patterns(text),
                )
            )

        return [result for result in results if result.risk_level != "HIGH"]

    def sanitize_document_for_context(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive patterns before the document is passed to the model."""
        sanitized = doc.copy()
        text = doc.get("text", doc.get("content", ""))

        for name, regex in self.pii_regex.items():
            text = regex.sub(f"[REDACTED_{name.upper()}]", text)

        for name, regex in self.confidential_regex.items():
            text = regex.sub(f"[REDACTED_{name.upper()}]", text)

        sanitized["text"] = text
        sanitized["sanitized"] = True
        sanitized["security_level"] = "sanitized"
        return sanitized

    def _check_pii(self, text: str) -> bool:
        return any(regex.search(text) for regex in self.pii_regex.values())

    def _check_phi(self, text: str) -> bool:
        phi_patterns = [
            r"(?i)medical",
            r"(?i)diagnosis",
            r"(?i)treatment",
            r"(?i)patient",
            r"(?i)doctor",
            r"(?i)hospital",
            r"\b\d{3}-\d{3}-\d{4}\b",
        ]
        return any(re.search(pattern, text) for pattern in phi_patterns)

    def _check_confidential(self, text: str) -> bool:
        return any(regex.search(text) for regex in self.confidential_regex.values())

    def _check_data_boundaries(self, doc: Dict[str, Any]) -> bool:
        doc_tenant = doc.get("tenant_id", doc.get("metadata", {}).get("tenant_id"))
        if doc_tenant and doc_tenant != self.tenant_id:
            return True

        classification = doc.get("classification", doc.get("metadata", {}).get("classification"))
        if classification and classification not in self.data_boundaries.get("allowed_classifications", []):
            return True

        return False

    def _assess_risk_level(self, pii: bool, phi: bool, confidential: bool, boundary: bool) -> str:
        if pii or phi or boundary:
            return "HIGH"
        if confidential:
            return "MEDIUM"
        return "LOW"

    def _get_sensitive_patterns(self, text: str) -> List[str]:
        patterns: List[str] = []
        for name, regex in self.pii_regex.items():
            if regex.search(text):
                patterns.append(f"PII-{name}")
        for name, regex in self.confidential_regex.items():
            if regex.search(text):
                patterns.append(f"CONFIDENTIAL-{name}")
        return patterns
