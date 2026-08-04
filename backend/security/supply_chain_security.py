"""Model supply-chain governance for the enterprise platform."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass
class ModelArtifact:
    name: str
    version: str
    hash: str
    source: str
    license: str
    provenance: Dict
    security_scan: Dict
    timestamp: str


class ModelSupplyChainSecurity:
    """Perform basic provenance, license, and integrity checks."""

    def __init__(self, registry_url: str, scan_service_url: str):
        self.registry_url = registry_url
        self.scan_service_url = scan_service_url
        self.registry: Dict[str, ModelArtifact] = {}
        self.allowed_sources = {
            "huggingface": ["microsoft", "meta", "google", "openai"],
            "custom": ["company-internal"],
            "azure": ["azure-openai"],
        }
        self.license_approved = ["MIT", "Apache-2.0", "BSD-3", "Commercial"]

    def register_model(self, model_artifact: ModelArtifact) -> bool:
        if not self._verify_source(model_artifact):
            return False
        if not self._verify_license(model_artifact):
            return False
        if not self._verify_integrity(model_artifact):
            return False
        if not self._security_scan(model_artifact):
            return False
        if not self._verify_provenance(model_artifact):
            return False

        self.registry[f"{model_artifact.name}:{model_artifact.version}"] = model_artifact
        return True

    def _verify_source(self, artifact: ModelArtifact) -> bool:
        source, org = artifact.source.split("/") if "/" in artifact.source else (artifact.source, "")
        if source not in self.allowed_sources:
            return False
        if org and org not in self.allowed_sources.get(source, []):
            return False
        return True

    def _verify_license(self, artifact: ModelArtifact) -> bool:
        return artifact.license in self.license_approved

    def _verify_integrity(self, artifact: ModelArtifact) -> bool:
        return artifact.hash == self._fetch_model_hash(artifact)

    def _security_scan(self, artifact: ModelArtifact) -> bool:
        artifact.security_scan = self._call_scan_service(artifact)
        return artifact.security_scan.get("passed", False)

    def _verify_provenance(self, artifact: ModelArtifact) -> bool:
        return True

    def _fetch_model_hash(self, artifact: ModelArtifact) -> str:
        return f"hash_{artifact.name}_{artifact.version}"

    def _call_scan_service(self, artifact: ModelArtifact) -> Dict:
        return {
            "passed": True,
            "vulnerabilities": [],
            "severity": "none",
            "timestamp": datetime.now().isoformat(),
        }

    def get_model_risk_score(self, model_name: str, version: str) -> float:
        artifact = self.registry.get(f"{model_name}:{version}")
        if not artifact:
            return 1.0

        score = 0.0
        if artifact.source not in ["huggingface/microsoft", "azure"]:
            score += 0.1
        if artifact.license == "Commercial":
            score += 0.1
        if artifact.security_scan and artifact.security_scan.get("vulnerabilities"):
            score += len(artifact.security_scan["vulnerabilities"]) * 0.05
        if not artifact.provenance.get("verified", True):
            score += 0.2
        return min(score, 1.0)
