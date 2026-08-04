# security/supply_chain_security.py
from dataclasses import dataclass
from typing import Optional, List, Dict
import hashlib
import json
from datetime import datetime

@dataclass
class ModelArtifact:
    name: str
    version: str
    hash: str
    source: str  # huggingface, custom, azure, etc.
    license: str
    provenance: Dict
    security_scan: Dict
    timestamp: str

class ModelSupplyChainSecurity:
    """Secure the AI model supply chain"""
    
    def __init__(self, registry_url: str, scan_service_url: str):
        self.registry_url = registry_url
        self.scan_service_url = scan_service_url
        self.registry = {}
        self.allowed_sources = {
            'huggingface': ['microsoft', 'meta', 'google', 'openai'],
            'custom': ['company-internal'],
            'azure': ['azure-openai'],
        }
        self.license_approved = [
            'MIT', 'Apache-2.0', 'BSD-3', 'Commercial'
        ]
    
    def register_model(self, model_artifact: ModelArtifact) -> bool:
        """
        Register a new model with supply chain verification
        """
        # 1. Verify source
        if not self._verify_source(model_artifact):
            return False
        
        # 2. Verify license
        if not self._verify_license(model_artifact):
            return False
        
        # 3. Verify hash/integrity
        if not self._verify_integrity(model_artifact):
            return False
        
        # 4. Security scan
        if not self._security_scan(model_artifact):
            return False
        
        # 5. Provenance verification
        if not self._verify_provenance(model_artifact):
            return False
        
        # 6. Store in registry
        self.registry[f"{model_artifact.name}:{model_artifact.version}"] = model_artifact
        
        return True
    
    def _verify_source(self, artifact: ModelArtifact) -> bool:
        """Verify model source is allowed"""
        source, org = artifact.source.split('/') if '/' in artifact.source else (artifact.source, '')
        if source not in self.allowed_sources:
            return False
        if org and org not in self.allowed_sources.get(source, []):
            return False
        return True
    
    def _verify_license(self, artifact: ModelArtifact) -> bool:
        """Verify license is approved"""
        return artifact.license in self.license_approved
    
    def _verify_integrity(self, artifact: ModelArtifact) -> bool:
        """Verify model hash integrity"""
        # Would fetch actual model from registry and compute hash
        # For now, simulate
        expected_hash = self._fetch_model_hash(artifact)
        return artifact.hash == expected_hash
    
    def _security_scan(self, artifact: ModelArtifact) -> bool:
        """Run security scan on model"""
        # Scan for vulnerabilities, backdoors, etc.
        # This would call a security scanning service
        scan_results = self._call_scan_service(artifact)
        artifact.security_scan = scan_results
        return scan_results.get('passed', False)
    
    def _verify_provenance(self, artifact: ModelArtifact) -> bool:
        """Verify model provenance"""
        # Check training data provenance
        # Check lineage
        # Check for known issues
        return True
    
    def _fetch_model_hash(self, artifact: ModelArtifact) -> str:
        """Fetch actual hash from registry"""
        # Simulate
        return f"hash_{artifact.name}_{artifact.version}"
    
    def _call_scan_service(self, artifact: ModelArtifact) -> Dict:
        """Call external security scanning service"""
        # Simulate security scan
        return {
            'passed': True,
            'vulnerabilities': [],
            'severity': 'none',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_model_risk_score(self, model_name: str, version: str) -> float:
        """Calculate risk score for a model"""
        artifact = self.registry.get(f"{model_name}:{version}")
        if not artifact:
            return 1.0
        
        score = 0.0
        # Source risk
        if artifact.source not in ['huggingface/microsoft', 'azure']:
            score += 0.1
        
        # License risk
        if artifact.license == 'Commercial':
            score += 0.1
        
        # Security scan risk
        if artifact.security_scan and artifact.security_scan.get('vulnerabilities'):
            score += len(artifact.security_scan['vulnerabilities']) * 0.05
        
        # Provenance risk
        if not artifact.provenance.get('verified', True):
            score += 0.2
        
        return min(score, 1.0)