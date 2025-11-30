import json # Needed for pretty printing dicts
import asyncio
import datetime
from typing import Any, Dict, Optional
import os
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool, ToolContext
from google.adk.tools import google_search
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import sqlite3
import pandas as pd
import shutil
from enum import Enum
from prompts.medical_lookup_sys_prompt import medical_search_prompt, medical_diagnose_prompt, medical_lookup_prompt
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from mcp import StdioServerParameters
from fhirclient import client
from fhirclient.models.patient import Patient
from fhirclient.models.medication import Medication
from fhirclient.models.medicationrequest import MedicationRequest

import logging

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
# )

os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
CONVERSATION_COMPLETE_SIGNAL = "[CONVERSATION_COMPLETE]"
APP_NAME = "agent_hackathon"
USER_ID = "test_user_456"
SESSION_ID_TOOL_AGENT = "session_tool_agent_xyz"
SESSION_ID_SCHEMA_AGENT = "session_schema_agent_xyz"
MODEL_NAME = "gemini-2.5-flash"
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
patient_id = '14867dba-fb11-4df3-9829-8e8e081b39e6'

settings = {
    'app_id': 'my_web_app',
    'api_base': 'https://r4.smarthealthit.org'
}

smart = client.FHIRClient(settings=settings)

def get_patient_dob() -> str:
    """Retrieve the patient's date of birth.

    Raises:
        ValueError: If patient_id is not set.
    """
    if not patient_id or patient_id == 'example_patient_id':
        raise ValueError("Patient ID is not set. Please set a valid patient_id before calling this tool.")
    
    # In a real application, consider error handling for FHIR client operations
    # and potential missing data.
    patient = Patient.read(patient_id, smart.server)
    return patient.birthDate.isostring

def get_patient_medications() -> list:
    """Retrieve the patient's list of medications.

    Raises:
        ValueError: If patient_id is not set.
    """
    if not patient_id or patient_id == 'example_patient_id':
        raise ValueError("Patient ID is not set. Please set a valid patient_id before calling this tool.")

    def _med_name(med):
        if med.coding:
            name = next((coding.display for coding in med.coding if coding.system == 'http://www.nlm.nih.gov/research/umls/rxnorm'), None)
            if name:
                return name
        if med.text and med.text:
            return med.text
        return "Unnamed Medication(TM)"

    def _get_medication_by_ref(ref, smart_client):
        med_id = ref.split("/")[1]
        return Medication.read(med_id, smart_client.server).code
    
    def _get_med_name(prescription, client_fhir=None):
        if prescription.medicationCodeableConcept is not None:
            med = prescription.medicationCodeableConcept
            return _med_name(med)
        elif prescription.medicationReference is not None and client_fhir is not None:
            med = _get_medication_by_ref(prescription.medicationReference.reference, client_fhir)
            return _med_name(med)
        else:
            return 'Error: medication not found'
    
    # In a real application, consider error handling for FHIR client operations
    # and potential empty bundles.
    bundle = MedicationRequest.where({'patient': patient_id}).perform(smart.server)
    prescriptions = [be.resource for be in bundle.entry] if bundle is not None and bundle.entry is not None else None
  
    return [_get_med_name(p, smart) for p in prescriptions]

medical_search_agent = LlmAgent(
    model=MODEL_NAME,
    name="medical_search_agent",
    description="When patient ask regarding medical general query.",
    instruction=medical_search_prompt,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "tavily-mcp@latest",
                    ],
                    env={
                        "TAVILY_API_KEY": TAVILY_API_KEY,
                    }
                ),
                timeout=30,
            ),
        )
    ],
)

medical_diagnosis_agent = LlmAgent(
    model=MODEL_NAME,
    name="medical_diagnosis_agent",
    instruction=medical_diagnose_prompt,
    description="When patient wants to know about his/her prescription details.",
    tools=[get_patient_dob, get_patient_medications]
)

root_agent = LlmAgent(
    model=MODEL_NAME,
    name="medical_lookup_agent",
    instruction=medical_lookup_prompt,
    # generate_content_config=types.GenerateContentConfig(automatic_function_calling = types.AutomaticFunctionCallingConfig(disable=True)),
    sub_agents=[medical_search_agent, medical_diagnosis_agent]
)

a2a_app = to_a2a(
    root_agent,
    host="app3",
    port=8003,  # Choose a port for your A2A service
    protocol="http"
)

