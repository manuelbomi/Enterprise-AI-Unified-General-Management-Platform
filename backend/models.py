from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class APIServiceDefinition(BaseModel):
    name: str
    path: str
    description: str
    owner: str
    tags: List[str] = Field(default_factory=list)
    enabled: bool = True


class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = "default"
    temperature: float = 0.7
    max_tokens: int = 1000
    context: Optional[List[str]] = None
    tenant_id: str = Field(..., description="Tenant identifier for isolation")
    request_id: Optional[str] = None


class GenerateResponse(BaseModel):
    response: str
    model_used: str
    latency_ms: float
    tokens_used: int
    cost: float
    evaluations: Optional[Dict[str, Any]] = None


class RAGRequest(BaseModel):
    query: str
    context: Optional[List[str]] = None
    tenant_id: str


class AgentRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None
    tenant_id: str


class SecurityValidationResponse(BaseModel):
    is_safe: bool
    reason: str
    risk_score: float
    detected_patterns: List[str]


class ModelArtifactRegisterRequest(BaseModel):
    name: str
    version: str
    source: str
    license: str
    hash: str
    provenance: Dict[str, Any] = {}


class ModelRiskResponse(BaseModel):
    model_name: str
    version: str
    risk_score: float
    approved: bool


class ServiceSummary(BaseModel):
    service_count: int
    api_count: int
    tenant_count: int
    summary: str


class SecurityPolicy(BaseModel):
    name: str
    category: str
    description: str
    enabled: bool = True


class APIRegistrationRequest(BaseModel):
    name: str
    path: str
    description: str
    owner: str
    tags: Optional[List[str]] = Field(default_factory=list)


class RAGResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    latency_ms: float
    citations: List[Dict[str, Any]]


class AgentResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, Any]]] = None
    tool_usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None


class ModelArtifactRegisterRequest(BaseModel):
    name: str
    version: str
    source: str
    license: str
    hash: str
    provenance: Dict[str, Any] = Field(default_factory=dict)
