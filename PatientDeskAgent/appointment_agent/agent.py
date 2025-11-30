import json # Needed for pretty printing dicts
import asyncio
import datetime
from typing import Any, Dict, Optional
import os
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool, ToolContext
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import sqlite3
import pandas as pd
import shutil
from enum import Enum
from prompts.patient_appointment_sys_prompt import patient_appointment_prompt

os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
CONVERSATION_COMPLETE_SIGNAL = "[CONVERSATION_COMPLETE]"
APP_NAME = "agent_hackathon"
USER_ID = "test_user_456"
SESSION_ID_TOOL_AGENT = "session_tool_agent_xyz"
SESSION_ID_SCHEMA_AGENT = "session_schema_agent_xyz"
MODEL_NAME = "gemini-2.5-flash"
local_file_constant = "db/appointment_schedule_constant.db"
local_file_current = "db/appointment_schedule.db"

class ApptType(Enum):
    adult_physicals = "Adult physicals"
    pediatric_physicals = "Pediatric physicals"
    follow_up_appointments = "Follow-up appointments"
    sick_visits = "Sick visits"
    flu_shots = "Flu shots"
    other_vaccinations = "Other vaccinations"
    allergy_shots = "Allergy shots"
    b12_injections = "B12 injections"
    diabetes_management = "Diabetes management"
    hypertension_management = "Hypertension management"
    asthma_management = "Asthma management"
    chronic_pain_management  = "Chronic pain management"
    initial_mental_health = "Initial mental health consultations"
    follow_up_mental_health = "Follow-up mental health appointments"
    therapy_session = "Therapy sessions"
    blood_draws = "Blood draws"
    urine_tests = "Urine tests"
    ekgs = "EKGs"
    biopsies = "Biopsies"
    medication_management = "Medication management"
    wart_removals = "Wart removals"
    skin_tag_removals = "Skin tag removals"
    ear_wax_removals = "Ear wax removals"

def find_available_appointments(
    appointment_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list:
    """
    Look for available new appointments.
    
    Args:
        appointment_type: The type of appointment (e.g., "General", "Dental").
        start_date: The earliest date to check, in format "YYYY-MM-DD".
        end_date: The latest date to check, in format "YYYY-MM-DD".
    """
    
    # Ensure the current database is a copy of the constant one for a clean state per session
    shutil.copyfile(local_file_constant, local_file_current)

    conn = sqlite3.connect(local_file_current)
    
    # Use the string directly (ensure your Enum string values match what the LLM generates)
    query_datetime = f"SELECT * from appointment_schedule WHERE appointment_type = \"{appointment_type}\" AND patient IS NULL "

    if start_date:
        # We can treat the ISO string directly for SQL comparison, or validate it first
        query_datetime += f" AND datetime >= \"{start_date}\""

    if end_date:
        # We must convert the string back to a date object to do the math
        try:
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            # Add 24 hours to end_date to include the entire day
            next_day = end_date_obj + datetime.timedelta(days=1)
            query_datetime += f" AND datetime <= \"{next_day.isoformat()}\""
        except ValueError:
            # Handle potential format errors if necessary, or let it fail
            pass

    available_appts = pd.read_sql(
        query_datetime, conn
    )

    conn.close()
    
    # Convert datetime strings to more readable format for the model
    formatted_appointments = []
    for dt_str in available_appts['datetime']:
        dt_obj = datetime.datetime.fromisoformat(dt_str)
        formatted_appointments.append(dt_obj.strftime("%B %d %Y at %I %M %p").replace(" 0", " ").replace("AM", "A.M.").replace("PM", "P.M."))
        
    return formatted_appointments
    
def book_appointment(
    appointment_datetime: str, 
    appointment_type: str, # Changed ApptType to str
):
    """
    Book new appointments.
    
    Args:
        appointment_datetime: The string format returned by find_available_appointments (e.g. "October 15 2024 at 02 30 P.M.")
        appointment_type: The type of appointment (e.g., "General", "Dental").
    """
    
    conn = sqlite3.connect(local_file_current)
    
    # 1. Clean up the string for parsing
    # The previous function outputs "A.M."/"P.M.", but strptime %p expects "AM"/"PM"
    clean_datetime_str = appointment_datetime.replace("A.M.", "AM").replace("P.M.", "PM")
    
    try:
        # Attempt to parse in the human-readable format
        dt_obj = datetime.datetime.strptime(clean_datetime_str, "%B %d %Y at %I %M %p")
    except ValueError:
        # Fallback: try ISO format if the model decides to use that instead
        try:
            dt_obj = datetime.datetime.fromisoformat(clean_datetime_str)
        except ValueError:
            # Final safety net if formatting is completely different
            conn.close()
            raise ValueError(f"Could not parse date string: {appointment_datetime}")

    # 2. Logic Change: Used appointment_type directly (removed .value)
    booking_query = f"UPDATE appointment_schedule SET patient = \"current_patient\" WHERE datetime = \"{dt_obj.isoformat()}\" AND appointment_type = \"{appointment_type}\""
    
    cur = conn.cursor()    
    cur.execute(booking_query)
    conn.commit() 

    find_patient_appt_query = "SELECT * from appointment_schedule where patient = \"current_patient\""

    current_patient_entries = pd.read_sql(find_patient_appt_query, conn, index_col="index")

    cur.close()
    conn.close()
      
    return current_patient_entries.to_json(orient="records")
    
root_agent = LlmAgent(
    model=MODEL_NAME,
    name="patient_appointment_agent",
    description="""You are an AI appointment scheduling assistant for a healthcare clinic. Your persona is empathetic, encouraging, and friendly. Your primary goal is to guide a user through a conversational, step-by-step process to schedule a healthcare appointment, using the functions available to you to find and book appointments.""",
    instruction=patient_appointment_prompt,
    tools=[find_available_appointments, book_appointment]
)

a2a_app = to_a2a(
    root_agent,
    host="app2",
    port=8002,  # Choose a port for your A2A service
    protocol="http"
)
