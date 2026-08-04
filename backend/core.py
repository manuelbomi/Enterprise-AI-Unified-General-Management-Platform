"""Core orchestration for the Enterprise AI management platform."""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List

from .models import (
    APIServiceDefinition,
    AgentRequest,
    GenerateRequest,
    GenerateResponse,
    ModelArtifactRegisterRequest,
    ModelRiskResponse,
    RAGRequest,
    SecurityPolicy,
    SecurityValidationResponse,
)
from .patterns.standard_agent import StandardAgent, Tool
from .patterns.standard_rag import StandardRAGPipeline
from .security.prompt_injection import PromptInjectionDefense
from .security.rag_security import RAGSecurity
from .security.supply_chain_security import ModelArtifact, ModelSupplyChainSecurity


class MockLLM:
    """A lightweight mock LLM to simulate plan generation and evaluation."""

    async def generate(self, prompt: str) -> str:
        if "plan" in prompt.lower():
            return json.dumps([
                {
                    "step_id": "step_1",
                    "action": "noop",
                    "parameters": {},
                    "reasoning": "Create a base execution plan and validate the request."
                }
            ])

        if "evaluate" in prompt.lower():
            return json.dumps({"score": 0.98, "recommendation": "production ready"})

        if "rag" in prompt.lower():
            return "The result is derived from trusted sources and verified context."

        return "simulated model output"


class APIServiceRegistry:
    """In-memory registry for API service definitions and routes."""

    def __init__(self):
        self.services: List[APIServiceDefinition] = []
        self._load_default_services()

    def _load_default_services(self) -> None:
        self.services.extend([
            APIServiceDefinition(
                name="ai-gateway",
                path="/gateway",
                description="Core AI API management gateway",
                owner="platform-team",
                tags=["gateway", "management", "enterprise"],
            ),
            APIServiceDefinition(
                name="ai-security",
                path="/gateway/security",
                description="Prompt, document and model security enforcement endpoints",
                owner="platform-security",
                tags=["security", "policy", "audit"],
            ),
            APIServiceDefinition(
                name="ai-supply-chain",
                path="/gateway/model",
                description="Model supply chain, registry and risk evaluation",
                owner="platform-models",
                tags=["model-registry", "governance"],
            ),
        ])

    def list_services(self) -> List[APIServiceDefinition]:
        return self.services

    def register_api(self, definition: APIServiceDefinition) -> APIServiceDefinition:
        self.services.append(definition)
        return definition

    def summary(self) -> Dict[str, Any]:
        return {
            "service_count": len(self.services),
            "api_count": len(self.services),
            "tenant_count": 1,
            "summary": "Enterprise AI API and governance platform with built-in route, policy and model catalog management.",
        }


class PolicyEngine:
    """Policy engine for enterprise prompt validation and security governance."""

    def __init__(self) -> None:
        self.prompt_defender = PromptInjectionDefense()
        self.rag_guard = RAGSecurity(tenant_id="default", data_boundaries={
            "allowed_classifications": ["public", "internal"]
        })
        self.policies: List[SecurityPolicy] = [
            SecurityPolicy(
                name="Prompt Injection Defense",
                category="input-safety",
                description="Reject prompts that attempt to override system instructions or exfiltrate sensitive data.",
            ),
            SecurityPolicy(
                name="Tenant Isolation",
                category="data-boundary",
                description="Enforce tenant-specific data access for RAG retrieval and AI responses.",
            ),
            SecurityPolicy(
                name="Model Supply Chain Verification",
                category="model-governance",
                description="Validate model source, license, integrity and security scan status before deployment.",
            ),
        ]

    def list_policies(self) -> List[SecurityPolicy]:
        return self.policies

    async def validate_prompt(self, prompt: str, context: Dict[str, Any] = None) -> SecurityValidationResponse:
        result = self.prompt_defender.validate_prompt(prompt, context or {})
        return SecurityValidationResponse(
            is_safe=result.is_safe,
            reason=result.reason,
            risk_score=result.risk_score,
            detected_patterns=result.detected_patterns,
        )

    def validate_retrieved_documents(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        security_checks = self.rag_guard.validate_retrieved_documents(docs)
        return [check.__dict__ for check in security_checks]


class EnterpriseAIPlatform:
    """Orchestrates the enterprise AI gateway, security and model governance layers."""

    def __init__(self):
        self.registry = APIServiceRegistry()
        self.policy_engine = PolicyEngine()
        self.model_registry = ModelSupplyChainSecurity(
            registry_url="https://registry.example.com",
            scan_service_url="https://scan.example.com",
        )
        self.llm = MockLLM()
        self.rag_pipeline = StandardRAGPipeline(self.llm)
        self.agent = StandardAgent(self.llm, tools=[Tool(name="noop", description="No operation tool", handler=self._noop_tool)])

    async def initialize(self) -> None:
        await asyncio.sleep(0)

    async def get_summary(self) -> Dict[str, Any]:
        return self.registry.summary()

    def list_services(self) -> List[APIServiceDefinition]:
        return self.registry.list_services()

    def list_policies(self) -> List[SecurityPolicy]:
        return self.policy_engine.list_policies()

    def register_api(self, payload: Dict[str, Any]) -> APIServiceDefinition:
        definition = APIServiceDefinition(**payload)
        return self.registry.register_api(definition)

    async def validate_prompt(self, prompt: str, context: Dict[str, Any] = None) -> SecurityValidationResponse:
        return await self.policy_engine.validate_prompt(prompt, context or {})

    async def register_model(self, payload: ModelArtifactRegisterRequest) -> ModelRiskResponse:
        artifact = ModelArtifact(
            name=payload.name,
            version=payload.version,
            hash=payload.hash,
            source=payload.source,
            license=payload.license,
            provenance=payload.provenance,
            security_scan={},
            timestamp=datetime.utcnow().isoformat(),
        )
        approved = self.model_registry.register_model(artifact)
        return ModelRiskResponse(
            model_name=artifact.name,
            version=artifact.version,
            risk_score=self.model_registry.get_model_risk_score(artifact.name, artifact.version),
            approved=approved,
        )

    async def generate(self, payload: GenerateRequest) -> GenerateResponse:
        prompt_safe = await self.validate_prompt(payload.prompt, {"tenant_id": payload.tenant_id})
        if not prompt_safe.is_safe:
            raise ValueError(prompt_safe.reason)

        start = datetime.utcnow()
        response_text = await self.llm.generate(payload.prompt)
        latency = (datetime.utcnow() - start).total_seconds() * 1000
        return GenerateResponse(
            response=response_text,
            model_used=payload.model or "default",
            latency_ms=latency,
            tokens_used=len(response_text.split()),
            cost=max(0.01, len(response_text.split()) * 0.0001),
            evaluations={"safety": prompt_safe.dict()},
        )

    async def rag_query(self, payload: RAGRequest) -> Dict[str, Any]:
        result = await self.rag_pipeline.process(payload.query, {"tenant_id": payload.tenant_id})
        return {
            "answer": result.answer,
            "confidence": result.confidence,
            "latency_ms": result.latency_ms,
            "citations": result.citations,
            "sources": result.sources,
        }

    async def run_agent(self, payload: AgentRequest) -> Dict[str, Any]:
        return await self.agent.run(payload.task, payload.context or {})

    async def _noop_tool(self, **kwargs: Any) -> Dict[str, Any]:
        return {"status": "noop", "details": "This tool simulates a controlled execution step."}
