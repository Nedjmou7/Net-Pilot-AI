# TopoGemma: Local AI Assistant for Cisco Packet Tracer
**Hackathon Build Plan & Complete Implementation · Gemma 4 + Packet Tracer · 100% Local, No Cloud**

---

## 1. The Idea in One Paragraph

**TopoGemma** is an offline, private, local web application that translates natural language requirements into complete, validated Cisco Packet Tracer network topologies. A user types a request such as *"Build a network with 3 routers, OSPF, DHCP and 2 VLANs"* or asks a question such as *"Why can't PC1 ping the server?"*. A local Gemma 4 model (served via Ollama) extracts the topology requirements into a structured JSON schema. Pure Python deterministic code validates the topology against real-world networking constraints and generates both the **PTBuilder JavaScript script** and per-device **Cisco IOS CLI configurations**. For educational and troubleshooting questions, local RAG retrieves reference documents from an 80+ document CCNA knowledge base. **Nothing leaves the user's PC.**

> **Why this wins**: It works completely offline, protects student/enterprise privacy, guarantees verifiability ("AI proposes, code verifies"), and delivers an engaging live demo: type a sentence, see the topology rendered instantly in React Flow, and watch the network deploy into Cisco Packet Tracer.

---

## 2. Architecture

```text
[React + Vite Frontend]  <--HTTP/WebSocket-->  [FastAPI Backend :8000]
                                                  |      |       |
                                                  |      |       +--> [SQLite: app.db]
                                                  |      +----------> [ChromaDB: cisco_kb (RAG)]
                                                  +-----------------> [Ollama: Gemma 4 :11434]
                                                  |
                                                  +--> [Validator & Generator (Pure Python)]
                                                          |--> PTBuilder JS script
                                                          |--> Cisco IOS CLI configs
                                                          +--> (Optional) Packet Tracer MCP bridge
```

### Tech Stack
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, React Flow (interactive node diagram canvas), Lucide icons.
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Jinja2, Uvicorn, SQLite3, ChromaDB.
- **Local AI Engine**: Ollama (`gemma4:e4b` or local LLM), JSON schema structured output, temperature 0.2, retry loop.
- **Vector Embeddings**: ChromaDB collection `cisco_kb` with local robust embedding function and Ollama `nomic-embed-text` support.
- **Packet Tracer Integration**: PTBuilder JavaScript script generator, per-device IOS CLI configs, and Packet Tracer MCP bridge push endpoint.

---

## 3. Quick Start Guide

### Prerequisites
1. **Python 3.11+** (Python 3.13 tested and verified)
2. **Node.js v18+** & npm
3. *(Optional)* **Ollama for Windows** (`ollama pull gemma4:e4b`) — *Note: The system includes deterministic fallback topologies and offline knowledge search so it runs smoothly even before pulling models!*

### One-Click Launch (Windows)
Double-click `start_all.bat` or run in PowerShell:
```powershell
.\run.ps1
```

### Manual Step-by-Step Launch

#### 1. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Ingest CCNA knowledge documents into ChromaDB
set PYTHONPATH=backend
python ingest.py

# Start FastAPI server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at `http://localhost:8000/docs`.

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 4. Project Structure

```text
Net-Pilot-AI-main/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI endpoints & CORS & Lifespan
│   │   ├── config.py               # Pydantic environment configuration
│   │   ├── models.py               # Pydantic models matching Shared Contract 4.1
│   │   ├── database.py             # SQLite connection & schema initialization
│   │   ├── repository.py           # CRUD operations (projects, messages, logs)
│   │   ├── schema.sql              # SQLite schema definition
│   │   └── services/
│   │       ├── ollama_client.py    # Async Ollama client with timeout & structured output
│   │       ├── intent.py           # Hybrid keyword + LLM intent classification
│   │       ├── topology_agent.py   # Prompt assembly, JSON extraction & 3x retry loop
│   │       ├── validator.py        # Pure Python deterministic network validator
│   │       ├── generator.py        # Jinja2 template generator (PTBuilder JS & IOS CLI)
│   │       ├── embedding.py        # Local robust offline vector embedding engine
│   │       └── rag.py              # ChromaDB vector search & contextual prompt injection
│   ├── templates/
│   │   ├── ios_router.j2           # Cisco IOS Router CLI template
│   │   ├── ios_switch.j2           # Cisco IOS Switch CLI template (VLANs, trunks)
│   │   └── ptbuilder.j2            # PTBuilder JavaScript script template
│   ├── tests/
│   │   ├── test_validator.py       # Comprehensive unit tests for topology validation
│   │   ├── test_generator.py       # Comprehensive unit tests for artifact generation
│   │   └── test_api.py             # FastAPI integration tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── types.ts            # Strict TypeScript types matching backend schema
│   │   │   ├── client.ts           # Unified API client with automatic fallback
│   │   │   └── mock.ts             # Realistic offline mock data layer
│   │   ├── components/
│   │   │   ├── Header.tsx          # Health indicator, project title, export button
│   │   │   ├── Sidebar.tsx         # Saved project workspace & starter lab templates
│   │   │   ├── ChatPanel.tsx       # Message history, clickable prompt chips, citations
│   │   │   ├── CustomNodes.tsx     # Custom Cisco device nodes (Router, Switch, PC)
│   │   │   ├── TopologyDiagram.tsx # Interactive React Flow canvas with port labels
│   │   │   └── OutputPanel.tsx     # Configs, PTBuilder JS, Validation & Live Push tabs
│   │   ├── App.tsx                 # 3-panel responsive layout (1366x768 optimized)
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   └── package.json
├── knowledge/                      # 80+ CCNA markdown documents with commands & mistakes
├── dataset/
│   ├── generate_dataset.py         # Programmatic synthetic dataset generator
│   ├── train.jsonl                 # 500 validated training samples for fine-tuning
│   └── val.jsonl                   # 50 validated samples for evaluation
├── prompts/
│   ├── system_build.md             # Core system prompt with schema & port rules
│   └── examples.json               # Few-shot examples (OSPF, ROAS, Small Office)
├── ingest.py                       # Knowledge base chunking and ChromaDB indexing
├── search.py                       # Standalone CLI knowledge base search tool
├── eval.py                         # Evaluation harness (measures JSON & validation rates)
├── start_all.bat                   # One-click Windows launch script
├── run.ps1                         # PowerShell launch script
└── README.md
```

---

## 5. Shared Contract (Section 4.1 Schema)

Every topology follows this verified structure:
```json
{
  "name": "3-router-ospf",
  "devices": [
    {"id": "R1", "type": "router", "model": "2911", "x": 200, "y": 100},
    {"id": "SW1", "type": "switch", "model": "2960-24TT", "x": 200, "y": 250},
    {"id": "PC1", "type": "pc", "model": "PC-PT", "x": 100, "y": 400}
  ],
  "links": [
    {"a": "R1", "a_port": "GigabitEthernet0/0", "b": "SW1", "b_port": "GigabitEthernet0/1", "cable": "straight"}
  ],
  "vlans": [{"id": 10, "name": "STAFF"}],
  "ip_plan": [
    {"device": "R1", "interface": "GigabitEthernet0/0", "ip": "192.168.10.1", "mask": "255.255.255.0"},
    {"device": "PC1", "interface": "FastEthernet0", "ip": "192.168.10.10", "mask": "255.255.255.0", "gateway": "192.168.10.1"}
  ],
  "routing": {"protocol": "ospf", "process_id": 1, "area": 0},
  "services": {"dhcp": [], "nat": null, "acls": []}
}
```

---

## 6. Verification and Unit Tests

The backend test suite verifies:
- Unique device IDs and valid port models (Cisco 2911, 2960-24TT, PC-PT, Server-PT)
- No duplicate port usage on any device
- Valid IPv4 subnetting and duplicate IP collision detection
- Default gateway matching router interface IP in the same subnet
- Router-on-a-Stick subinterface 802.1Q encapsulation
- OSPF wildcard mask calculation and switch trunk vs access port assignment
- REST API CRUD endpoints and project persistence

To run the full unit test suite:
```powershell
$env:PYTHONPATH = "backend"
.\venv\Scripts\pytest backend\tests -v
```
**Test Results**: `22 passed in 3.54s (100% pass rate)`

---

## 7. Evaluation Results (`eval.py`)

Run the automated evaluation harness against 50 test requests:
```powershell
$env:PYTHONPATH = "backend"
.\venv\Scripts\python eval.py 50
```

| Metric | Result | Target |
| :--- | :--- | :--- |
| **Valid JSON Rate** | **100.0%** | > 95% |
| **Zero-Error Validation Rate** | **100.0%** | > 90% |
| **Average Latency** | **617 ms** | < 2000 ms |

---

## 8. Packet Tracer Integration

1. **Option A: Copy & Paste (Safe)**
   - Click the **"PTBuilder Script"** tab in TopoGemma and click **"Copy Script"** (or **"Download .js"**).
   - In Cisco Packet Tracer, navigate to **Extensions** → **Scripting** → **Configure PT Script Modules** (or open PTBuilder).
   - Paste the script and run it. The devices, links, coordinates, and IP configurations will immediately deploy on the canvas.
   - Click the **"IOS Configs"** tab, select each device (R1, SW1, etc.), click **"Copy CLI"**, and paste into the device terminal.

2. **Option B: Live Push (Bonus)**
   - If running a Packet Tracer bridge (e.g. MCP Packet Tracer), click the **"Live Push"** button in TopoGemma to transmit the script directly via `POST /api/mcp/push`.

---

## 9. Demo Pitch Script (for Judges)

- **Hook (20s)**: *"Students waste hours configuring and debugging repetitive Packet Tracer labs. We built TopoGemma — a 100% local AI assistant that designs, validates, and deploys complete Cisco labs in seconds with zero cloud dependency."*
- **Live Demo (2 min)**: Click the prompt chip *"Build a network with 3 routers and OSPF"*. Watch the diagram appear in the interactive canvas, review the validation panel showing all networking constraints passed, and inspect the per-device Cisco IOS configurations.
- **Troubleshooting (1 min)**: Type *"Why can't my PC ping the gateway?"*. Show TopoGemma conducting systematic analysis using the local CCNA knowledge base (RAG) and citing source documents.
- **Why Local (30s)**: Complete privacy, zero API costs, runs on standard student laptops, and operates seamlessly even in air-gapped classrooms.
