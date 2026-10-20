import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import httpx

from app.config import settings
from app.database import init_db
from app.models import (
    Topology, ValidationResult, ChatRequest, ChatResponse,
    GenerateRequest, GenerateResponse, ProjectCreate, ProjectResponse
)
from app.services.ollama_client import ollama_client
from app.services.intent import classify_intent
from app.services.topology_agent import build_topology
from app.services.validator import validate_topology
from app.services.generator import generate_artifacts
from app.services.rag import answer_with_rag, query_chromadb
import app.repository as repo

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("topogemma.main")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("TopoGemma backend initialized. SQLite ready.")
    yield

app = FastAPI(
    title="TopoGemma API",
    description="100% Local AI Assistant for Cisco Packet Tracer",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    """Checks that Ollama and the DB are up."""
    ollama_status = await ollama_client.check_health()
    db_ok = True
    try:
        repo.get_projects()
    except Exception as e:
        db_ok = False
        logger.error(f"Database health check failed: {e}")

    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "online" if db_ok else "offline",
        "ollama": ollama_status,
        "config": {
            "model": settings.OLLAMA_MODEL,
            "ollama_url": settings.OLLAMA_URL
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Main chat route:
    1. Classifies intent ('build', 'question', 'troubleshoot')
    2. For 'build': calls topology agent, validates schema, produces topology & validation
    3. For 'question' / 'troubleshoot': searches RAG and synthesizes answer
    4. Logs message history to SQLite
    """
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    intent = await classify_intent(user_msg)
    repo.save_message(project_id=req.project_id, role="user", content=user_msg, intent=intent)

    if intent == "build":
        topology, val_result = await build_topology(user_msg)
        status_msg = "Here is the network topology based on your specifications."
        if val_result.is_valid:
            status_msg += " All networking constraints and IP schemas passed validation."
        else:
            status_msg += f" Note: {len(val_result.errors)} validation issues were detected."

        reply = f"{status_msg}\n\nReview the topology diagram and generated configurations."
        repo.save_message(project_id=req.project_id, role="assistant", content=reply, intent="build")

        return ChatResponse(
            reply=reply,
            intent="build",
            topology=topology,
            sources=[],
            validation=val_result
        )
    else:
        # Question or Troubleshoot
        reply, sources = await answer_with_rag(user_msg, intent=intent)
        repo.save_message(project_id=req.project_id, role="assistant", content=reply, intent=intent)

        return ChatResponse(
            reply=reply,
            intent=intent,
            topology=None,
            sources=sources,
            validation=ValidationResult(errors=[], warnings=[], is_valid=True)
        )

@app.post("/api/topology/validate", response_model=ValidationResult)
async def validate_endpoint(topology: Topology):
    """Validate a topology JSON; returns errors and warnings."""
    return validate_topology(topology)

@app.post("/api/topology/generate", response_model=GenerateResponse)
async def generate_endpoint(req: GenerateRequest):
    """Topology JSON in; PTBuilder script and per-device CLI configs out."""
    return generate_artifacts(req.topology)

@app.get("/api/projects")
async def list_projects():
    """List saved projects."""
    return repo.get_projects()

@app.post("/api/projects")
async def save_project(payload: ProjectCreate):
    """Save a new project or update existing."""
    topo_str = payload.topology.model_dump_json()
    proj = repo.create_project(name=payload.name, topology_json=topo_str)
    return proj

@app.get("/api/projects/{project_id}")
async def get_project(project_id: int):
    """Load a project and its chat history."""
    proj = repo.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    messages = repo.get_messages(project_id)
    return {
        "project": proj,
        "messages": messages
    }

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int):
    """Delete a saved project."""
    success = repo.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True, "id": project_id}

@app.get("/api/knowledge/search")
async def search_knowledge(q: str = Query(..., description="Query text to search")):
    """Search the local knowledge base chunks."""
    results = query_chromadb(q, k=4)
    return {"query": q, "count": len(results), "results": results}

@app.post("/api/mcp/push")
async def push_to_packet_tracer(payload: GenerateRequest):
    """Push generated script to Packet Tracer MCP bridge if running."""
    gen = generate_artifacts(payload.topology)
    bridge_url = f"{settings.PACKET_TRACER_BRIDGE_URL}/execute"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(bridge_url, json={"script": gen.ptbuilder_script})
            return {
                "success": res.status_code == 200,
                "bridge_status": res.status_code,
                "message": "Script pushed to Packet Tracer bridge"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Packet Tracer bridge unreachable on {settings.PACKET_TRACER_BRIDGE_URL}: {str(e)}"
        }

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time streaming tokens."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                parsed = json.loads(data)
                message = parsed.get("message", "")
            except Exception:
                message = data

            intent = await classify_intent(message)
            await websocket.send_json({"type": "intent", "intent": intent})

            if intent == "build":
                topology, val = await build_topology(message)
                gen = generate_artifacts(topology)
                await websocket.send_json({
                    "type": "result",
                    "reply": "Topology created successfully.",
                    "intent": "build",
                    "topology": topology.model_dump(),
                    "validation": val.model_dump(),
                    "generation": gen.model_dump()
                })
            else:
                chunks = query_chromadb(message, k=4)
                sources = list(dict.fromkeys([c["source"] for c in chunks]))
                reply, _ = await answer_with_rag(message, intent=intent)
                await websocket.send_json({
                    "type": "result",
                    "reply": reply,
                    "intent": intent,
                    "sources": sources
                })
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
