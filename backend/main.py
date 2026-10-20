import os
import subprocess
from datetime import datetime
from pathlib import Path
import json
import httpx
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.models import (
    ChatRequest, ChatResponse, ValidationResult,
    TopologyValidateRequest, TopologyGenerateRequest, TopologyGenerateResponse,
    ProjectCreateRequest, ProjectItem, HealthResponse, Topology
)
from backend.services.validator import validate_topology
from backend.services.generator import generate_all_artifacts
from backend.services.intent import classify_intent
from backend.services.topology_agent import generate_topology, summarize_generated_topology
from backend.services.rag import search_knowledge, answer_rag_question
from backend.services import ollama_client
from backend.database import repo

load_dotenv()

app = FastAPI(
    title="TopoGemma API",
    description="Local AI Assistant for Cisco Packet Tracer (Net-Pilot-AI)",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    repo.init_db()


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    ollama_info = await ollama_client.check_health()
    db_ok = True
    try:
        repo.get_db_connection().close()
    except Exception:
        db_ok = False

    return HealthResponse(
        status="healthy" if db_ok else "degraded",
        ollama_online=ollama_info["online"],
        ollama_model=ollama_info["model"],
        database_online=db_ok,
        chroma_online=True,
        version="1.0.0"
    )


@app.post("/api/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    user_msg = request.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Record user message in DB
    repo.add_message(request.project_id, "user", user_msg)

    # Classify intent
    intent = await classify_intent(user_msg)

    if intent == "build":
        topology, validation = await generate_topology(user_msg, max_retries=2)
        if topology and not validation.errors:
            reply = summarize_generated_topology(topology, validation)
        elif topology:
            reply = f"Generated topology '{topology.name}' with some validation warnings/errors. Review the validation tab."
        else:
            reply = "I had trouble generating a fully compliant topology. Please adjust your prompt and try again."

        # Save assistant message
        repo.add_message(request.project_id, "assistant", reply, intent)

        # Auto-save generation artifacts if project exists
        if topology and request.project_id:
            script, configs = generate_all_artifacts(topology)
            repo.save_generation(request.project_id, script, configs)
            repo.save_project(f"Project #{request.project_id}", topology.model_dump(), request.project_id)

        return ChatResponse(
            reply=reply,
            intent="build",
            topology=topology,
            sources=["prompts/system_build.md", "prompts/examples.json"],
            validation=validation
        )

    else:
        # Question or Troubleshoot -> RAG workflow
        history = repo.get_messages(request.project_id) if request.project_id else []
        reply, sources = await answer_rag_question(
            user_msg,
            intent=intent,
            history=history
        )
        repo.add_message(request.project_id, "assistant", reply, intent)

        return ChatResponse(
            reply=reply,
            intent=intent,
            topology=None,
            sources=sources,
            validation=ValidationResult(errors=[], warnings=[])
        )


@app.post("/api/topology/validate", response_model=ValidationResult)
async def validate_topology_endpoint(request: TopologyValidateRequest):
    return validate_topology(request.topology)


@app.post("/api/topology/generate", response_model=TopologyGenerateResponse)
async def generate_topology_artifacts(request: TopologyGenerateRequest):
    script, configs = generate_all_artifacts(request.topology)
    return TopologyGenerateResponse(
        ptbuilder_script=script,
        cli_configs=configs
    )


@app.get("/api/projects", response_model=List[ProjectItem])
async def list_projects_endpoint():
    projects = repo.list_projects()
    return [
        ProjectItem(
            id=p["id"],
            name=p["name"],
            topology=p["topology"],
            created_at=str(p["created_at"]),
            updated_at=str(p["updated_at"])
        )
        for p in projects
    ]


@app.post("/api/projects")
async def save_project_endpoint(request: ProjectCreateRequest):
    topo = request.topology or {}
    pid = repo.save_project(request.name, topo)
    return {"id": pid, "name": request.name, "message": "Project saved successfully"}


@app.get("/api/projects/{project_id}")
async def get_project_endpoint(project_id: int):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    messages = repo.get_messages(project_id)
    project["messages"] = messages
    return project


@app.get("/api/knowledge/search")
async def search_knowledge_endpoint(q: str = Query(..., description="Query string")):
    chunks = await search_knowledge(q, k=4)
    return {"query": q, "results": chunks}


@app.post("/api/packet-tracer/push")
async def push_to_packet_tracer(request: TopologyGenerateRequest):
    """
    Optional live bridge push into Packet Tracer MCP or local Script Engine bridge.
    Checks Mats2208/MCP-Packet-Tracer or local port 39000/8080.
    """
    script, configs = generate_all_artifacts(request.topology)
    bundle_dir = Path(__file__).resolve().parent.parent / "bridge" / "bundles" / (
        f"{request.topology.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "topology.json").write_text(
        json.dumps(request.topology.model_dump(), indent=2), encoding="utf-8"
    )
    (bundle_dir / "topogemma_build.js").write_text(script, encoding="utf-8")
    config_dir = bundle_dir / "ios-configs"
    config_dir.mkdir()
    for device_id, config in configs.items():
        (config_dir / f"{device_id}.txt").write_text(config, encoding="utf-8")
    (bundle_dir / "README.txt").write_text(
        "This bundle was generated by NetBuilder. The JavaScript requires an "
        "external PTBuilder bridge; standard Cisco Packet Tracer cannot create "
        "a .pkt file automatically.\n",
        encoding="utf-8"
    )

    packet_tracer_candidates = [
        os.getenv("PACKET_TRACER_PATH", ""),
        r"C:\Program Files\Cisco Packet Tracer\bin\PacketTracer.exe",
        r"C:\Program Files (x86)\Cisco Packet Tracer\bin\PacketTracer.exe",
    ]
    for program_dir in (Path(r"C:\Program Files"), Path(r"C:\Program Files (x86)")):
        packet_tracer_candidates.extend(
            str(path)
            for path in program_dir.glob(r"Cisco Packet Tracer*\\bin\\PacketTracer.exe")
        )
    packet_tracer_path = next(
        (path for path in packet_tracer_candidates if path and Path(path).exists()),
        None
    )
    packet_tracer_started = False
    if packet_tracer_path:
        try:
            subprocess.Popen([packet_tracer_path], close_fds=True)
            packet_tracer_started = True
        except OSError:
            packet_tracer_started = False
    pt_bridge_url = os.getenv(
        "PACKET_TRACER_BRIDGE_URL",
        os.getenv("PT_BRIDGE_URL", "http://localhost:39000")
    ).rstrip("/")
    if not pt_bridge_url.endswith("/run"):
        pt_bridge_url = f"{pt_bridge_url}/run"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(pt_bridge_url, json={"script": script})
            if resp.status_code == 200:
                result = resp.json()
                bridge_message = result.get(
                    "message",
                    "Script received by the PTBuilder bridge."
                )
                launch_message = (
                    "Packet Tracer was opened."
                    if packet_tracer_started
                    else "Packet Tracer was not found or could not be opened."
                )
                return {
                    "success": True,
                    "message": (
                        f"{launch_message} {bridge_message} "
                        f"Bundle saved to {bundle_dir}."
                    ),
                    "bundle_path": str(bundle_dir),
                    "packet_tracer_started": packet_tracer_started,
                }
    except Exception:
        pass

    launch_message = (
        "Packet Tracer was opened and the topology bundle was prepared."
        if packet_tracer_started
        else "The topology bundle was prepared, but Packet Tracer was not found. "
        "Set PACKET_TRACER_PATH to PacketTracer.exe to launch it automatically."
    )
    return {
        "success": True,
        "message": (
            f"{launch_message} "
            "Automatic .pkt deployment requires a compatible PTBuilder bridge. "
            f"Bundle saved to {bundle_dir}."
        ),
        "bundle_path": str(bundle_dir),
        "packet_tracer_started": packet_tracer_started,
    }


@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            req = json.loads(data)
            user_msg = req.get("message", "")
            intent = await classify_intent(user_msg)

            if intent == "build":
                topology, validation = await generate_topology(user_msg)
                await websocket.send_text(json.dumps({
                    "type": "topology",
                    "intent": "build",
                    "topology": topology.model_dump() if topology else None,
                    "validation": validation.model_dump()
                }))
            else:
                # Stream answer tokens
                chunks = await search_knowledge(user_msg, k=4)
                sources = list(dict.fromkeys([c["source"] for c in chunks]))
                await websocket.send_text(json.dumps({
                    "type": "start",
                    "intent": intent,
                    "sources": sources
                }))
                reply, _ = await answer_rag_question(user_msg, intent)
                for word in reply.split(" "):
                    await websocket.send_text(json.dumps({
                        "type": "token",
                        "token": word + " "
                    }))
                await websocket.send_text(json.dumps({"type": "end"}))
    except WebSocketDisconnect:
        pass
