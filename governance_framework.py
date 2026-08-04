# governance/ai_governance.py
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import json
from datetime import datetime

class ModelRiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class GovernancePolicy:
    name: str
    version: str
    description: str
    requirements: List[str]
    risk_level: ModelRiskLevel
    approval_matrix: Dict
    
class AIGovernanceFramework:
    """Enterprise AI governance framework"""
    
    def __init__(self):
        self.policies = {
            'model_registration': GovernancePolicy(
                name='Model Registration',
                version='2.0',
                description='Standards for model registration',
                requirements=[
                    'Model card with all metadata',
                    'Training data provenance',
                    'Performance benchmarks',
                    'Security scan results',
                    'Bias evaluation report'
                ],
                risk_level=ModelRiskLevel.HIGH,
                approval_matrix={
                    'low': ['Team Lead'],
                    'medium': ['Team Lead', 'Security Lead'],
                    'high': ['Security Lead', 'Compliance Lead', 'AI Council'],
                    'critical': ['Executive Review Board']
                }
            ),
            'data_governance': GovernancePolicy(
                name='Data Governance',
                version='2.0',
                description='Data handling and privacy standards',
                requirements=[
                    'Data classification',
                    'PII/PHI handling',
                    'Data retention policies',
                    'Data minimization',
                    'Consent management'
                ],
                risk_level=ModelRiskLevel.CRITICAL,
                approval_matrix={}
            )
        }
    
    def evaluate_model_risk(self, model: Dict) -> ModelRiskLevel:
        """Evaluate risk level of a model"""
        risk_score = 0
        
        # Consider model size
        if model.get('parameters', 0) > 1e11:  # >100B
            risk_score += 2
        
        # Consider training data
        if model.get('training_data_source') == 'user_data':
            risk_score += 3
        
        # Consider capabilities
        if model.get('capabilities', []):
            if 'code_generation' in model['capabilities']:
                risk_score += 1
            if 'autonomous_action' in model['capabilities']:
                risk_score += 3
        
        # Consider deployment environment
        if model.get('deployment') == 'on_premise':
            risk_score += 1
        elif model.get('deployment') == 'cloud':
            risk_score += 2
        
        # Determine risk level
        if risk_score >= 7:
            return ModelRiskLevel.CRITICAL
        elif risk_score >= 5:
            return ModelRiskLevel.HIGH
        elif risk_score >= 3:
            return ModelRiskLevel.MEDIUM
        else:
            return ModelRiskLevel.LOW
    
    def get_approval_workflow(self, model: Dict) -> Dict:
        """Get approval workflow for model"""
        risk_level = self.evaluate_model_risk(model)
        policy = self.policies['model_registration']
        
        approvers = policy.approval_matrix.get(risk_level.value, ['Team Lead'])
        
        return {
            'risk_level': risk_level.value,
            'required_approvers': approvers,
            'sequential': True,
            'review_steps': self._get_review_steps(risk_level)
        }
    
    def _get_review_steps(self, risk_level: ModelRiskLevel) -> List[Dict]:
        """Get review steps based on risk level"""
        steps = [
            {'name': 'Technical Review', 'status': 'pending'},
            {'name': 'Security Review', 'status': 'pending'},
            {'name': 'Bias Evaluation', 'status': 'pending'}
        ]
        
        if risk_level in [ModelRiskLevel.HIGH, ModelRiskLevel.CRITICAL]:
            steps.append({'name': 'Legal Review', 'status': 'pending'})
            steps.append({'name': 'Executive Review', 'status': 'pending'})
        
        if risk_level == ModelRiskLevel.CRITICAL:
            steps.append({'name': 'Board Review', 'status': 'pending'})
            steps.append({'name': 'External Audit', 'status': 'pending'})
        
        return steps
    
    def create_model_card(self, model: Dict) -> Dict:
        """Create comprehensive model card"""
        return {
            'model_name': model.get('name'),
            'version': model.get('version'),
            'release_date': datetime.now().isoformat(),
            'framework': model.get('framework'),
            'parameters': model.get('parameters'),
            'architecture': model.get('architecture'),
            'training_data': {
                'source': model.get('training_data_source'),
                'size': model.get('training_data_size'),
                'description': model.get('training_data_description'),
                'bias_analysis': model.get('bias_analysis', {})
            },
            'performance': {
                'benchmarks': model.get('benchmarks', {}),
                'accuracy': model.get('accuracy'),
                'latency': model.get('latency'),
                'cost_per_token': model.get('cost_per_token')
            },
            'intended_use': model.get('intended_use'),
            'limitations': model.get('limitations', []),
            'risks': model.get('risks', []),
            'safety': {
                'security_scan': model.get('security_scan', {}),
                'prompt_injection_score': model.get('prompt_injection_score'),
                'toxicity_score': model.get('toxicity_score')
            },
            'governance': {
                'risk_level': self.evaluate_model_risk(model).value,
                'approval_status': 'pending',
                'approvers': [],
                'review_comments': []
            }
        }