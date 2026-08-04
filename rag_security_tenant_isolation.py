# security/rag_security.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib
import re

@dataclass
class DocumentSecurityCheck:
    is_safe: bool
    risk_level: str  # LOW, MEDIUM, HIGH
    contains_pii: bool
    contains_ph: bool  # Protected Health Information
    contains_confidential: bool
    sensitive_patterns: List[str]

class RAGSecurity:
    """Security controls for RAG pipeline"""
    
    # PII patterns (simplified)
    PII_PATTERNS = {
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'address': r'\b\d{1,5}\s\w+\s\w+',  # Simplified
        'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    }
    
    # Confidential data patterns
    CONFIDENTIAL_PATTERNS = {
        'internal_team': r'(?i)(internal|confidential|secret|restricted)',
        'project_codes': r'[A-Z]{2,4}-\d{3,5}',
        'client_names': [],  # Would be loaded from context
    }
    
    def __init__(self, tenant_id: str, data_boundaries: Dict[str, Any]):
        self.tenant_id = tenant_id
        self.data_boundaries = data_boundaries
        self._init_patterns()
    
    def _init_patterns(self):
        """Initialize regex patterns"""
        self.pii_regex = {
            name: re.compile(pattern) 
            for name, pattern in self.PII_PATTERNS.items()
        }
        self.confidential_regex = {
            name: re.compile(pattern)
            for name, pattern in self.CONFIDENTIAL_PATTERNS.items()
            if isinstance(pattern, str)
        }
    
    def validate_retrieved_documents(self, documents: List[Dict]) -> List[DocumentSecurityCheck]:
        """
        Validate retrieved documents before passing to LLM
        
        Args:
            documents: List of retrieved document chunks
            
        Returns:
            Security check results for each document
        """
        results = []
        
        for doc in documents:
            text = doc.get('text', doc.get('content', ''))
            
            # Check for sensitive information
            pii_found = self._check_pii(text)
            ph_found = self._check_phi(text)
            confidential_found = self._check_confidential(text)
            
            # Check against tenant data boundaries
            boundary_violation = self._check_data_boundaries(doc)
            
            # Determine risk level
            risk_level = self._assess_risk_level(
                pii_found, 
                ph_found, 
                confidential_found,
                boundary_violation
            )
            
            is_safe = (
                risk_level != 'HIGH' and
                not pii_found and
                not ph_found and
                not boundary_violation
            )
            
            results.append(DocumentSecurityCheck(
                is_safe=is_safe,
                risk_level=risk_level,
                contains_pii=pii_found,
                contains_ph=ph_found,
                contains_confidential=confidential_found,
                sensitive_patterns=self._get_sensitive_patterns(text)
            ))
        
        # If any high-risk document, filter them out
        if any(r.risk_level == 'HIGH' for r in results):
            results = [r for r in results if r.risk_level != 'HIGH']
            # Also add a placeholder/documentation about filtering
        
        return results
    
    def _check_pii(self, text: str) -> bool:
        """Check for PII in text"""
        for name, regex in self.pii_regex.items():
            if regex.search(text):
                return True
        return False
    
    def _check_phi(self, text: str) -> bool:
        """Check for Protected Health Information"""
        # PHI specific patterns (simplified)
        phi_patterns = [
            r'(?i)medical', r'(?i)diagnosis', r'(?i)treatment',
            r'(?i)patient', r'(?i)doctor', r'(?i)hospital',
            r'\b\d{3}-\d{3}-\d{4}\b',  # Medical record number format
        ]
        for pattern in phi_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _check_confidential(self, text: str) -> bool:
        """Check for confidential information"""
        for name, regex in self.confidential_regex.items():
            if regex.search(text):
                return True
        return False
    
    def _check_data_boundaries(self, doc: Dict) -> bool:
        """Check if document violates tenant data boundaries"""
        # Check tenant isolation
        doc_tenant = doc.get('tenant_id', doc.get('metadata', {}).get('tenant_id'))
        if doc_tenant and doc_tenant != self.tenant_id:
            return True
        
        # Check data classification
        classification = doc.get('classification', doc.get('metadata', {}).get('classification'))
        if classification and classification not in self.data_boundaries.get('allowed_classifications', []):
            return True
        
        return False
    
    def _assess_risk_level(self, pii: bool, phi: bool, confidential: bool, boundary: bool) -> str:
        """Assess overall risk level"""
        if pii or phi:
            return 'HIGH'
        if confidential:
            return 'MEDIUM'
        if boundary:
            return 'HIGH'
        return 'LOW'
    
    def _get_sensitive_patterns(self, text: str) -> List[str]:
        """Extract sensitive patterns found in text"""
        patterns = []
        for name, regex in self.pii_regex.items():
            if regex.search(text):
                patterns.append(f"PII-{name}")
        for name, regex in self.confidential_regex.items():
            if regex.search(text):
                patterns.append(f"CONFIDENTIAL-{name}")
        return patterns
    
    def sanitize_document_for_context(self, doc: Dict) -> Dict:
        """
        Sanitize document by redacting sensitive information
        
        Returns:
            Sanitized document dictionary
        """
        sanitized = doc.copy()
        text = doc.get('text', doc.get('content', ''))
        
        # Redact PII
        for name, regex in self.pii_regex.items():
            text = regex.sub(f'[REDACTED_{name.upper()}]', text)
        
        # Redact confidential information
        for name, regex in self.confidential_regex.items():
            text = regex.sub(f'[REDACTED_{name.upper()}]', text)
        
        # Add a warning header
        sanitized['text'] = text
        sanitized['sanitized'] = True
        sanitized['security_level'] = 'sanitized'
        
        return sanitized

# Example: Multi-tenant RAG isolation
class TenantIsolation:
    """Enforce tenant isolation in multi-tenant RAG"""
    
    def __init__(self, vector_store, metadata_store):
        self.vector_store = vector_store
        self.metadata_store = metadata_store
    
    def get_tenant_filter(self, tenant_id: str) -> Dict:
        """Get filter for tenant isolation"""
        return {
            'must': [
                {'term': {'tenant_id': tenant_id}},
                {'term': {'status': 'active'}}
            ],
            'should': [
                {'term': {'visibility': 'public'}},
                {'term': {'visibility': f'tenant_{tenant_id}'}}
            ],
            'minimum_should_match': 1
        }
    
    def tenant_safe_search(self, query: str, tenant_id: str, top_k: int = 5):
        """Perform tenant-safe vector search"""
        filter_dict = self.get_tenant_filter(tenant_id)
        # Apply filter to vector search
        results = self.vector_store.similarity_search(
            query=query,
            k=top_k,
            filter=filter_dict
        )
        return results