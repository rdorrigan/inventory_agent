# Autonomous Inventory Exception & Reorder Workflow

[![CI Pipeline](https://github.com/username/inventory-agentic-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/username/inventory-agentic-workflow/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, multi-agent state machine built with **LangGraph**, **FastAPI**, and **Pydantic** to automate inventory exception handling, stockout risk triage, and purchase order workflow execution.

---

## 📋 Overview

In supply chain operations, inventory exception alerts (e.g., stockout warnings, supplier delays, unexpected demand spikes) often arrive as unstructured text across email, Slack, or ERP log feeds. Processing these exceptions manually creates bottlenecks, delays replenishment, and increases risk.

This project implements an **autonomous agentic workflow** that:
1. **Parses & Triages** raw, unstructured inventory alerts using structured LLM outputs.
2. **Retrieves Real-Time Metadata** from backend database services (stock levels, safety stock thresholds, Economic Order Quantities).
3. **Applies Business & Risk Rules** to calculate total reorder exposure and dynamically route processing paths.
4. **Executes Action Paths**:
   * **Low-Risk (< $5,000):** Automatically generates purchase order payloads and commits transaction logs.
   * **High-Risk (≥ $5,000):** Halts automatic execution and routes the event into a **Human-in-the-Loop (HITL)** approval queue.

---

## 🏗 System Architecture & State Machine

The core workflow is modeled as a **Directed Acyclic Graph (DAG) state machine** using LangGraph. Each node represents an isolated agentic step with clear state boundaries, strict input/output schemas, and deterministic fallback paths.

### Workflow Diagram

```
                             ┌─────────────────────────┐
                             │   Unstructured Alert    │
                             │ (Email / Slack / Event) │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │      Triage Agent       │
                             │  (Structured Parsing)   │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │  Data Retrieval Agent   │
                             │ (ERP / DB Integration)  │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │     Decision Agent      │
                             │ (EOQ & Cost Evaluation) │
                             └────────────┬────────────┘
                                          │
                        ┌─────────────────┴─────────────────┐
                        │ Conditional Edge: Total Cost Gate │
                        └─────────────────┬─────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼ (< $5,000)                                   ▼ (≥ $5,000)
    ┌───────────────────────────┐                   ┌───────────────────────────┐
    │      Execution Agent      │                   │ Human-in-the-Loop Node    │
    │ (Auto PO Draft & Commit)  │                   │ (Escalation & Queue Entry)│
    └─────────────┬─────────────┘                   └─────────────┬─────────────┘
                  │                                               │
                  ▼                                               ▼
               [ END ]                                         [ END ]
```

---

## 🗺 Platform Equivalence Matrix

This architecture is built in pure Python to maximize flexibility, observability, and testing rigor. However, its modular agent-and-state layout directly maps to enterprise low-code / conversational AI platforms such as **Microsoft Copilot Studio** and **Power Automate**:

| Custom Agentic Framework (LangGraph) | Enterprise Low-Code Equivalent (Copilot Studio / Power Platform) |
| :--- | :--- |
| `InventoryState` (TypedDict / Pydantic) | **Global / Topic Variables** (`Global.SKU`, `Global.TotalCost`) |
| **Triage Agent** (`with_structured_output`) | **Generative AI Triggers & Entity Extraction** |
| **Data Retrieval Service** (`InventoryRepository`) | **Power Automate Cloud Flows / Custom Connectors** |
| **Conditional Routing Edge** (`route_decision`) | **Topic Condition Nodes & Branching** |
| **Execution Agent Node** | **Automated Action Flows** (ERP / Dataverse Writeback) |
| **Human-in-the-Loop Node** | **Power Automate Approvals Kit & Teams Adaptive Cards** |

---

## 📁 Repository Structure

```text
inventory-agentic-workflow/
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI Pipeline (Flake8, Pytest, Type Checking)
├── config/
│   └── settings.py                # Environment configuration & pydantic settings
├── data/
│   └── mock_db.json               # Seed inventory database records
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py               # LangGraph state machine assembly
│   │   ├── nodes.py               # Individual agent node definitions
│   │   └── state.py               # TypedDict state & Pydantic output schemas
│   ├── api/
│   │   ├── __init__.py
│   │   └── app.py                 # FastAPI Web API application
│   └── services/
│       ├── __init__.py
│       └── db_service.py          # Data abstraction repository layer
├── tests/
│   ├── __init__.py
│   ├── test_nodes.py              # Unit tests for individual node logic
│   └── test_workflow.py           # Integration tests for state machine execution
├── .env.example                   # Environment variable template
├── Dockerfile                     # Production container spec
├── docker-compose.yml             # Local service orchestration
├── README.md                      # Repository documentation
└── requirements.txt               # Project dependencies
```

---

## ⚡ Quickstart & Local Setup

### Prerequisites
* **Python 3.11+**
* **OpenAI API Key** (or compatible LLM endpoint)
* **Docker & Docker Compose** *(optional)*

### 1. Repository Installation
```bash
# Clone repository
git clone https://github.com/username/inventory-agentic-workflow.git
cd inventory-agentic-workflow

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy the example environment file and set your API keys:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4o-mini
LOG_LEVEL=INFO
APPROVAL_THRESHOLD=5000.00
```

### 3. Run the FastAPI Application
```bash
uvicorn src.api.app:app --reload --port 8000
```
* **Interactive API Docs (Swagger):** `http://localhost:8000/docs`
* **Health Check Endpoint:** `http://localhost:8000/health`

---

## 🐳 Running with Docker

Run the entire application stack in containerized mode:

```bash
# Build and run containers
docker-compose up --build

# Run in background mode
docker-compose up -d
```

---

## 🧪 Testing & Quality Assurance

This repository employs strict testing practices across unit node behaviors and full state-graph trajectories.

```bash
# Run full test suite with pytest
pytest

# Run tests with coverage report
pytest --cov=src --cov-report=term-missing

# Run code style linter
flake8 src/ tests/
```

### Test Coverage Highlights
* **Unit Tests (`tests/test_nodes.py`):** Mocks LLM response payloads to verify deterministic state transformations in `triage_agent`, `data_retrieval_agent`, and `decision_agent`.
* **Integration Tests (`tests/test_workflow.py`):** Validates path execution across high-value ($ \ge \$5,000 $) vs. standard ($ < \$5,000 $) scenarios.

---

## 🚀 Example Usage & API Payload

### Triggering a Low-Value Auto-Approval Workflow

**HTTP Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/triage" \
     -H "Content-Type: application/json" \
     -d '{"alert_text": "Warehouse A reports SKU-101 is down to 12 units. Need restock ASAP."}'
```

**Response (`200 OK`):**
```json
{
  "sku": "SKU-101",
  "recommended_order_qty": 100,
  "unit_cost": 45.0,
  "total_cost": 4500.0,
  "requires_approval": false,
  "status": "completed",
  "action_taken": "Purchase Order automatically generated."
}
```

---

### Triggering a High-Value Escalation Workflow

**HTTP Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/triage" \
     -H "Content-Type: application/json" \
     -d '{"alert_text": "Emergency stock alert: SKU-303 is down to 5 units in main DC!"}'
```

**Response (`200 OK`):**
```json
{
  "sku": "SKU-303",
  "recommended_order_qty": 20,
  "unit_cost": 1200.0,
  "total_cost": 24000.0,
  "requires_approval": true,
  "status": "pending_human_approval",
  "action_taken": "Escalated to Human-in-the-Loop queue due to financial threshold ($24,000.00 >= $5,000.00)."
}
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
