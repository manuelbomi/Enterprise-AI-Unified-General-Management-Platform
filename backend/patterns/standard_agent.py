"""Reusable enterprise agent workflow pattern."""
from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


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
    parameters: Dict[str, Any]
    status: str  # pending, executing, completed, failed
    result: Optional[Any]
    reasoning: str


@dataclass
class Tool:
    name: str
    description: str
    handler: Any

    async def execute(self, **kwargs: Any) -> Any:
        return await self.handler(**kwargs)


class StandardAgent:
    """Standard reusable agent pattern with planning and execution."""

    def __init__(self, llm: Any, tools: List[Tool], max_steps: int = 10):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.memory: List[Dict[str, Any]] = []
        self.state = AgentState.IDLE

    async def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the agent with a standard plan-execute-evaluate loop."""
        context = context or {}
        self.state = AgentState.PLANNING
        plan = await self._plan(task, context)

        self.state = AgentState.EXECUTING
        execution_history: List[Dict[str, Any]] = []

        for step in plan:
            result = await self._execute_step(step, context)
            execution_history.append(result)

            if self._should_replan(result):
                self.state = AgentState.PLANNING
                plan = await self._replan(task, execution_history, context)
                self.state = AgentState.EXECUTING

            if self._is_task_complete(result):
                self.state = AgentState.COMPLETED
                break

            if result.get("error"):
                self.state = AgentState.ERROR
                return {
                    "status": "error",
                    "error": result.get("error"),
                    "history": execution_history,
                }

        self.state = AgentState.EVALUATING
        final_result = await self._evaluate_results(execution_history, task)

        self.state = AgentState.COMPLETED
        return {
            "status": "completed",
            "result": final_result,
            "history": execution_history,
            "tool_usage": self._get_tool_usage_stats(execution_history),
        }

    async def _plan(self, task: str, context: Dict[str, Any]) -> List[AgentStep]:
        """Generate a plan for an incoming task."""
        prompt = self._build_planning_prompt(task, context)
        plan_json = await self.llm.generate(prompt)
        plan = self._parse_plan(plan_json)
        plan = self._validate_plan(plan)

        self.memory.append({"type": "plan", "task": task, "plan": [step.__dict__ for step in plan]})
        return plan

    async def _execute_step(self, step: AgentStep, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one step using the registered tools."""
        try:
            tool = self._find_tool(step.action)
            if not tool:
                return {"step_id": step.step_id, "success": False, "error": f"Tool {step.action} not found"}

            result = await tool.execute(**step.parameters)
            step.status = "completed"
            step.result = result

            self.memory.append({"type": "execution", "step": step.__dict__, "result": result})
            return {"step_id": step.step_id, "success": True, "result": result, "complete": result.get("status") == "done"}

        except Exception as exc:
            step.status = "failed"
            return {"step_id": step.step_id, "success": False, "error": str(exc)}

    async def _evaluate_results(self, history: List[Dict[str, Any]], task: str) -> Dict[str, Any]:
        """Evaluate the execution history and produce a summary."""
        prompt = self._build_evaluation_prompt(task, history)
        evaluation = await self.llm.generate(prompt)
        try:
            return json.loads(evaluation)
        except Exception:
            return {"summary": str(evaluation)}

    def _should_replan(self, result: Dict[str, Any]) -> bool:
        """Determine whether the current result requires replanning."""
        if not result.get("success", False):
            return True
        if result.get("confidence", 1.0) < 0.5:
            return True
        return False

    def _is_task_complete(self, result: Dict[str, Any]) -> bool:
        """Check whether the task has completed."""
        return result.get("complete", False)

    def _find_tool(self, action: str) -> Optional[Tool]:
        """Locate a tool by its action name."""
        for tool in self.tools:
            if tool.name == action:
                return tool
        return None

    def _get_tool_usage_stats(self, history: List[Dict[str, Any]]) -> Dict[str, int]:
        """Compute simple tool usage statistics from execution history."""
        stats: Dict[str, int] = {}
        for step in history:
            tool_name = step.get("step_id", "unknown").split("_")[0]
            stats[tool_name] = stats.get(tool_name, 0) + 1
        return stats

    def _build_planning_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Build an LLM prompt to generate an execution plan."""
        return f"Create a step-by-step plan for the task: {task}. Context: {context}."

    def _build_evaluation_prompt(self, task: str, history: List[Dict[str, Any]]) -> str:
        """Build an LLM prompt to evaluate the completed task."""
        return f"Evaluate the results of task: {task}. History: {history}."

    def _parse_plan(self, plan_json: str) -> List[AgentStep]:
        """Parse an LLM-generated plan into AgentStep objects."""
        try:
            plan_data = json.loads(plan_json)
        except Exception:
            plan_data = []

        steps: List[AgentStep] = []
        for index, item in enumerate(plan_data or []):
            steps.append(
                AgentStep(
                    step_id=item.get("step_id", f"step_{index + 1}"),
                    action=item.get("action", "noop"),
                    parameters=item.get("parameters", {}),
                    status="pending",
                    result=None,
                    reasoning=item.get("reasoning", ""),
                )
            )
        return steps

    def _validate_plan(self, plan: List[AgentStep]) -> List[AgentStep]:
        """Validate that each planned step is actionable."""
        validated = []
        for step in plan:
            if step.action and step.step_id:
                validated.append(step)
        return validated

    async def _replan(self, task: str, history: List[Dict[str, Any]], context: Dict[str, Any]) -> List[AgentStep]:
        """Generate a revised plan after a failed or incomplete step."""
        prompt = f"Replan task: {task} given history: {history}. Context: {context}."
        plan_json = await self.llm.generate(prompt)
        return self._parse_plan(plan_json)
