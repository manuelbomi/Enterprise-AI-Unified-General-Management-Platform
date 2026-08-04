# patterns/standard_agent.py
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
import json

class AgentState(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentStep:
    step_id: str
    action: str
    parameters: Dict
    status: str  # pending, executing, completed, failed
    result: Optional[Any]
    reasoning: str

class StandardAgent:
    """Standard reusable agent pattern with planning and execution"""
    
    def __init__(self, llm, tools, max_steps=10):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.memory = []
        self.state = AgentState.IDLE
    
    async def run(self, task: str, context: Dict = None) -> Dict:
        """
        Run agent with standard flow:
        1. Plan
        2. Execute
        3. Evaluate
        4. Iterate if needed
        """
        self.state = AgentState.PLANNING
        plan = await self._plan(task, context)
        
        self.state = AgentState.EXECUTING
        execution_history = []
        
        for step in plan:
            # Execute step
            result = await self._execute_step(step, context)
            execution_history.append(result)
            
            # Check if need to re-plan
            if self._should_replan(result):
                self.state = AgentState.PLANNING
                plan = await self._replan(task, execution_history, context)
                self.state = AgentState.EXECUTING
            
            # Check if complete
            if self._is_task_complete(result):
                self.state = AgentState.COMPLETED
                break
            
            # Check for errors
            if result.get('error'):
                self.state = AgentState.ERROR
                return {
                    'status': 'error',
                    'error': result.get('error'),
                    'history': execution_history
                }
        
        # Final evaluation
        self.state = AgentState.EVALUATING
        final_result = await self._evaluate_results(execution_history, task)
        
        self.state = AgentState.COMPLETED
        return {
            'status': 'completed',
            'result': final_result,
            'history': execution_history,
            'tool_usage': self._get_tool_usage_stats(execution_history)
        }
    
    async def _plan(self, task: str, context: Dict) -> List[AgentStep]:
        """Generate execution plan"""
        # Build planning prompt
        prompt = self._build_planning_prompt(task, context, self.tools)
        
        # Get plan from LLM
        plan_json = await self.llm.generate(prompt)
        plan = self._parse_plan(plan_json)
        
        # Validate plan
        plan = self._validate_plan(plan)
        
        # Store in memory
        self.memory.append({
            'type': 'plan',
            'task': task,
            'plan': plan
        })
        
        return plan
    
    async def _execute_step(self, step: AgentStep, context: Dict) -> Dict:
        """Execute a single step"""
        try:
            # Find the right tool
            tool = self._find_tool(step.action)
            if not tool:
                return {'error': f'Tool {step.action} not found'}
            
            # Execute tool
            result = await tool.execute(**step.parameters)
            
            # Record step
            step.status = 'completed'
            step.result = result
            
            # Update memory
            self.memory.append({
                'type': 'execution',
                'step': step,
                'result': result
            })
            
            return {
                'step_id': step.step_id,
                'success': True,
                'result': result
            }
            
        except Exception as e:
            step.status = 'failed'
            return {
                'step_id': step.step_id,
                'success': False,
                'error': str(e)
            }
    
    async def _evaluate_results(self, history: List, task: str) -> Dict:
        """Evaluate execution results"""
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(task, history)
        
        # Get evaluation from LLM
        evaluation = await self.llm.generate(prompt)
        
        return json.loads(evaluation)
    
    def _should_replan(self, result: Dict) -> bool:
        """Check if plan needs adjustment"""
        # Failed step
        if not result.get('success', False):
            return True
        
        # Suboptimal result
        if result.get('confidence', 1.0) < 0.5:
            return True
        
        return False
    
    def _is_task_complete(self, result: Dict) -> bool:
        """Check if task is complete"""
        return result.get('complete', False)
    
    def _find_tool(self, action: str):
        """Find tool by name"""
        for tool in self.tools:
            if tool.name == action:
                return tool
        return None
    
    def _get_tool_usage_stats(self, history: List) -> Dict:
        """Get statistics on tool usage"""
        stats = {}
        for step in history:
            tool_name = step.get('step_id', '').split('_')[0]
            stats[tool_name] = stats.get(tool_name, 0) + 1
        return stats