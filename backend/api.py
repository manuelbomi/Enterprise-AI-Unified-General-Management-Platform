"""FastAPI application for the Enterprise AI General Management Platform."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .core import EnterpriseAIPlatform
from .models import (
    APIRegistrationRequest,
    APIServiceDefinition,
    AgentRequest,
    AgentResponse,
    GenerateRequest,
    GenerateResponse,
    ModelArtifactRegisterRequest,
    ModelRiskResponse,
    RAGRequest,
    RAGResponse,
    SecurityPolicy,
    SecurityValidationResponse,
    ServiceSummary,
)

app = FastAPI(
    title="Enterprise AI General Management Platform",
    description="In-house AI API management, governance, and model supply-chain routing platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

platform = EnterpriseAIPlatform()


@app.on_event("startup")
async def startup():
    await platform.initialize()


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy", "service": "Enterprise AI General Management Platform"}


@app.get("/gateway/services", response_model=List[APIServiceDefinition])
def list_services() -> List[APIServiceDefinition]:
    return platform.list_services()


@app.get("/gateway/policies", response_model=List[SecurityPolicy])
def list_policies() -> List[SecurityPolicy]:
    return platform.list_policies()


@app.get("/gateway/summary", response_model=ServiceSummary)
async def platform_summary() -> ServiceSummary:
    return await platform.get_summary()


@app.post("/gateway/apis", response_model=APIServiceDefinition)
def register_api(payload: APIRegistrationRequest) -> APIServiceDefinition:
    return platform.register_api(payload.dict())


@app.post("/gateway/security/validate", response_model=SecurityValidationResponse)
async def validate_prompt(payload: GenerateRequest):
    return await platform.validate_prompt(payload.prompt, {"tenant_id": payload.tenant_id})


@app.post("/gateway/model/register", response_model=ModelRiskResponse)
async def register_model(payload: ModelArtifactRegisterRequest):
    return await platform.register_model(payload)


@app.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest):
    try:
        return await platform.generate(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/rag", response_model=RAGResponse)
async def rag_query(payload: RAGRequest) -> RAGResponse:
    return await platform.rag_query(payload)


@app.post("/agent", response_model=AgentResponse)
async def agent_task(payload: AgentRequest) -> AgentResponse:
    return await platform.run_agent(payload)
