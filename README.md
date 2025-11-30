# PatientDeskAgent-AI
**Automated front-desk assistant for healthcare — scheduling appointments, patient registration, and fetching medication data via agents.**

## 🎯 Problem & Motivation

Patient front-desks in clinics/hospitals handle a lot of routine but critical tasks:  
- scheduling appointments,  
- registering new patients,  
- fetching patient medication details,  
- answering common queries about medicines.

These tasks are repetitive, time-consuming, and often involve switching between multiple systems (hospital database, FHIR servers, medication info services).  

**PatientDeskAgent-AI** aims to automate and streamline these front-desk operations — reducing manual overhead, minimizing errors, and enabling healthcare staff to focus on patient care rather than administrative overhead.

## 💡 Solution Overview

PatientDeskAgent-AI uses a multi-agent architecture to automate common front-desk tasks:

- **Appointment Agent**: schedules new appointments and checks existing ones.  
- **Medication Agent**: fetches a patient’s medication history using FHIR (based on patient ID), and — via a Tavily MCP server — obtains detailed information about medicines on demand.  
- **Patient Intake Agent**: registers new patients; stores the registration details (e.g. demographics, contact info) in an `output/` folder.  
- **Primary Agent**: acts as an orchestrator. It receives user queries and delegates tasks to the appropriate agent (Appointment, Medication, or Patient Intake) using an agent-to-agent (A2A) communication protocol.  

All subordinate agents (Appointment, Medication, Patient Intake) run remotely; they communicate with the Primary Agent over the A2A protocol. This decoupled, agent-based design makes the system modular, extensible, and easier to maintain or scale (e.g. adding more agents in future).

## 🏗 Architecture / Design

![PatientDeskAgent-AI Architecture Diagram](adk_arch_diagram.png)

- Primary Agent routes user requests/queries.  
- Sub-agents handle domain-specific tasks.  
- Remote communication — enables each sub-agent to operate independently.  
- Data (like patient info or appointment logs) output to local `output/` folder or returned to user as responses.

## ✅ Features / Capabilities

- Schedule new appointments or look up existing appointments.  
- Register new patients — storing their info for later reference.  
- Fetch patient’s medication history (via FHIR) given their ID.  
- On-demand retrieval of medicine information from an external medicine-info server (Tavily MCP).  
- Modular architecture: new agents (e.g. billing, lab-results, reminders) can be added easily.

## ✅ Feature Inculded in Agent

- Multi-Agent system: Agent powered by an LLM
- Tools: MCP, custom tools
- Session & Memory: Sessions & state management (e.g. InMemorySessionService)
- Context engineering
- Observability: Logging, Tracing
- Agent evaluation
- A2A Protocol

## 🚀 Quick Start — Setup & Run

### Prerequisites

- Docker & Docker Compose installed  
- Access to required remote services (FHIR server, Tavily MCP server)  
- Appropriate credentials / configuration: Google_API_KEY and Tavily_API_KEY. Example .env file is present in repo with name example.env.txt

### 🔧 Database Initialization — Before Starting the Server

Before launching the full stack, you also have to initialize the database used by the appointment agent. Although, it is already present in the repo:

```bash
# Move into the `appointment_agent` folder
cd PatientDeskAgent/appointment_agent

# Run the database initialization script
python db_init.py
```

This script sets up the necessary database schema (tables, initial state, etc.) required by the appointment-agent — ensuring that appointment booking and lookup works correctly once you bring up the containers.

### Build & Start

```bash
git clone https://github.com/adi7820/PatientDeskAgent-AI.git
cd PatientDeskAgent-AI

# Build and run all agents & services
docker compose up --build
```

This will build the Docker images and start all agents (Primary + sub-agents).

### Usage

Once containers are up, you can interact with the Primary Agent using ADK Web UI at [`http://localhost:8000`](http://localhost:8000). Based on your query (appointment scheduling, patient registration, med-info request), the Primary Agent will delegate to the proper sub-agent and return a response.

Example flows:

Schedule appointment → Primary Agent → Appointment Agent → returns confirmation / slot.

Register new patient → Primary Agent → Patient Intake Agent → patient data stored in output/.

Get medication history → Primary Agent → Medication Agent (interacts with FHIR) → returns meds list.

Ask about a medicine → Primary Agent → Medication Agent → queries Tavily MCP server → returns medicine details.

