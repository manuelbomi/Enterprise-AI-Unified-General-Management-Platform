# security/prompt_injection_defense.py
import re
from typing import List, Tuple, Set
from dataclasses import dataclass

@dataclass
class SecurityCheckResult:
    is_safe: bool
    reason: str
    risk_score: float
    detected_patterns: List[str]

class PromptInjectionDefense:
    """Comprehensive prompt injection defense system"""
    
    # Known injection patterns
    INJECTION_PATTERNS = {
        'instruction_override': [
            r'(?i)ignore (previous|above|all) instructions',
            r'(?i)forget (your|the) (instructions|training)',
            r'(?i)disregard (previous|all|system) prompts',
            r'(?i)override (system|safety|security) constraints',
        ],
        'role_manipulation': [
            r'(?i)you are now (acting as|pretending to be)',
            r'(?i)your new (role|identity|persona) is',
            r'(?i)from now on (you|you\'re) (are|will be)',
            r'(?i)assume the (role|identity|persona) of',
        ],
        'data_exfiltration': [
            r'(?i)output (sensitive|private|confidential|internal) data',
            r'(?i)reveal (your|the) (system|training) (prompt|data)',
            r'(?i)show (me|us) (everything|all details) about',
        ],
        'jailbreak_attempts': [
            r'(?i)jailbreak',
            r'(?i)unrestricted mode',
            r'(?i)developer mode',
            r'(?i)no (restrictions|limitations|filters)',
            r'(?i)without (any|the) (restrictions|limitations)',
            r'(?i)bypass (safety|security|ethical) (measures|controls)',
        ],
        'delimiters': [
            r'```(\w+)?.*?```',  # Code blocks
            r'``.*?``',          # Inline code
            r'---.*?---',        # Markdown horizontal rules
            r'###.*?###',        # Markdown headers
        ],
    }
    
    # LLM-specific escape patterns
    ESCAPE_SEQUENCES = [
        r'\\n', r'\\t', r'\\r', r'\\b', r'\\f',
        r'\\x[0-9a-fA-F]{2}',
        r'\\u[0-9a-fA-F]{4}',
    ]
    
    def __init__(self):
        self.compiled_patterns = {
            category: [re.compile(pattern) for pattern in patterns]
            for category, patterns in self.INJECTION_PATTERNS.items()
        }
        
    def validate_prompt(self, prompt: str, context: dict = None) -> SecurityCheckResult:
        """
        Validate prompt for injection attempts
        
        Args:
            prompt: User input prompt
            context: Optional context for enhanced detection
            
        Returns:
            SecurityCheckResult with validation details
        """
        detected_patterns = []
        risk_score = 0.0
        warnings = []
        
        # 1. Check against known injection patterns
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(prompt)
                if matches:
                    detected_patterns.extend(matches)
                    risk_score += len(matches) * 0.2
                    warnings.append(f"{category}: {matches[0]}")
        
        # 2. Check for escaped sequences (obfuscation attempts)
        escape_matches = re.findall(r'|'.join(self.ESCAPE_SEQUENCES), prompt)
        if escape_matches:
            risk_score += len(escape_matches) * 0.15
            warnings.append(f"Escaped sequences detected")
        
        # 3. Check for excessive special characters
        special_chars = re.findall(r'[^a-zA-Z0-9\s.,!?]', prompt)
        if len(special_chars) > len(prompt) * 0.1:  # More than 10%
            risk_score += 0.2
            warnings.append("Excessive special characters")
        
        # 4. Check for token boundary manipulation
        token_boundaries = re.findall(r'<<|>>|[[\]]|{{|}}', prompt)
        if token_boundaries:
            risk_score += len(token_boundaries) * 0.05
            warnings.append("Token boundary manipulation")
        
        # 5. LLM-based semantic analysis (for advanced detection)
        # This would call a lightweight model to detect semantic anomalies
        
        # 6. Contextual validation
        if context:
            risk_score += self._contextual_validation(prompt, context)
        
        # Determine if safe
        is_safe = risk_score < 0.5  # Threshold
        
        return SecurityCheckResult(
            is_safe=is_safe,
            reason=f"Risk score: {risk_score:.2f}. {'Safe' if is_safe else 'Blocked'}",
            risk_score=risk_score,
            detected_patterns=detected_patterns if detected_patterns else []
        )
    
    def _contextual_validation(self, prompt: str, context: dict) -> float:
        """Validate prompt against context"""
        extra_risk = 0.0
        
        # Check if prompt attempts to access context
        context_keywords = ['context', 'system prompt', 'instruction', 'template']
        for keyword in context_keywords:
            if keyword in prompt.lower():
                extra_risk += 0.1
        
        # Check if prompt contains anything from context
        for key, value in context.items():
            if str(value) in prompt:
                extra_risk += 0.1
        
        return extra_risk

    def sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt by removing/escaping dangerous patterns"""
        # Remove code blocks
        prompt = re.sub(r'```(\w+)?.*?```', '[CODE_BLOCK]', prompt, flags=re.DOTALL)
        # Escape special characters
        prompt = prompt.replace('{{', '{ {').replace('}}', '} }')
        prompt = prompt.replace('<<', '< <').replace('>>', '> >')
        return prompt