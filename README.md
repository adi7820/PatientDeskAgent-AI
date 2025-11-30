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