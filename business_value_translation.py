# consulting/business_value.py

class ConsultingAITranslator:
    """
    Translate AI capabilities to business outcomes for consulting context
    """
    
    def __init__(self):
        self.value_mappings = {
            'document_review': {
                'capability': 'RAG + Document Analysis',
                'metric': 'time reduction',
                'target': '80% reduction in document review time',
                'client_value': 'Auditors can review 5x more documents',
                'cost_saving': '$500K/year per team'
            },
            'memo_generation': {
                'capability': 'LLM + Template System',
                'metric': 'generation time',
                'target': '5-minute memos from 2-hour drafts',
                'client_value': 'Analysts spend less time on documentation',
                'cost_saving': '$200K/year per analyst'
            },
            'decision_support': {
                'capability': 'Agent + Analytics',
                'metric': 'decision quality',
                'target': '95% accurate recommendations',
                'client_value': 'Better client outcomes',
                'cost_saving': 'Reduced risk by 30%'
            }
        }
    
    def translate_to_business_value(self, ai_capability: str, 
                                   client_context: Dict) -> Dict:
        """
        Translate AI capabilities to measurable business outcomes
        """
        mapping = self.value_mappings.get(ai_capability)
        if not mapping:
            return self._generic_translation(ai_capability, client_context)
        
        # Customize for client context
        team_size = client_context.get('team_size', 10)
        annual_budget = client_context.get('annual_budget', 5_000_000)
        
        return {
            'capability': ai_capability,
            'description': mapping['capability'],
            'key_metric': mapping['metric'],
            'target': mapping['target'],
            'client_value': mapping['client_value'],
            'estimated_savings': self._calculate_savings(
                team_size, 
                annual_budget,
                mapping.get('cost_saving')
            ),
            'roi': self._calculate_roi(annual_budget, team_size),
            'implementation_effort': '3-6 months',
            'client_testimonial': self._get_testimonial_template(ai_capability)
        }
    
    def _generic_translation(self, capability: str, context: Dict) -> Dict:
        """Generic translation for any AI capability"""
        return {
            'capability': capability,
            'description': f'AI-powered {capability}',
            'key_metric': 'operational efficiency',
            'target': '10-30% improvement',
            'client_value': 'Improved productivity and quality',
            'estimated_savings': '$100K-$500K/year',
            'roi': '2.5x-5x',
            'implementation_effort': '2-6 months'
        }
    
    def _calculate_savings(self, team_size: int, budget: float, 
                          cost_saving: str) -> float:
        """Calculate estimated savings"""
        # Parse cost saving string
        if not cost_saving:
            return budget * 0.1
        
        # Extract number from cost_saving
        import re
        numbers = re.findall(r'\$?([\d.]+)[K|M]?', cost_saving)
        if numbers:
            base = float(numbers[0])
            if 'K' in cost_saving:
                base *= 1000
            elif 'M' in cost_saving:
                base *= 1000000
            return base * team_size
        return budget * 0.1
    
    def _calculate_roi(self, budget: float, team_size: int) -> str:
        """Calculate ROI"""
        savings = budget * 0.2  # Assume 20% efficiency gain
        investment = budget * 0.1  # Assume 10% investment
        roi = savings / investment if investment > 0 else 1
        return f"{roi:.1f}x"
    
    def _get_testimonial_template(self, capability: str) -> str:
        """Get a testimonial template"""
        testimonial_templates = {
            'document_review': (
                "Our audit team reduced document review time by 80%, "
                "allowing us to take on 40% more clients without "
                "increasing headcount."
            ),
            'memo_generation': (
                "Analysts now spend 2 hours per week on memos instead "
                "of 10 hours. This has significantly improved our "
                "margins on consulting engagements."
            ),
            'decision_support': (
                "The AI decision support system has reduced our risk "
                "exposure by 30% and improved client satisfaction scores "
                "by 15 points."
            )
        }
        return testimonial_templates.get(capability, "")

# Example usage for Financial & Auditing Applications
def create_consulting_presentation_slides(translator, ai_capabilities, client):
    """Generate consulting presentation slides"""
    slides = []
    
    for capability in ai_capabilities:
        value = translator.translate_to_business_value(
            capability,
            {'team_size': client.team_size, 'annual_budget': client.budget}
        )
        
        slide = {
            'title': f"AI Capability: {value['capability']}",
            'content': {
                'capability_description': value['description'],
                'key_metric': value['key_metric'],
                'target_improvement': value['target'],
                'client_value': value['client_value'],
                'estimated_savings': f"${value['estimated_savings']:,.0f}",
                'roi': value['roi'],
                'implementation_timeline': value['implementation_effort'],
                'testimonial': value['client_testimonial']
            },
            'chart': {
                'type': 'bar',
                'data': {
                    'Current': 100,
                    'With AI': 20 if capability == 'document_review' else 30
                }
            }
        }
        slides.append(slide)
    
    return slides