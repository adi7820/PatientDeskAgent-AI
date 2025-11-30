import json # Needed for pretty printing dicts
from typing import Any, Dict
import os
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from prompts.patient_intake_system_prompt import patient_intake_prompt

os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")

APP_NAME = "agent_hackathon"
USER_ID = "test_user_456"
SESSION_ID_TOOL_AGENT = "session_tool_agent_xyz"
SESSION_ID_SCHEMA_AGENT = "session_schema_agent_xyz"
MODEL_NAME = "gemini-2.5-flash"


def save_to_json_file(data: Dict[str, Any], filename: str = "patient_data.json") -> str:
    """
    Saves a dictionary to a JSON file in the 'output' directory.

    Args:
        data: The dictionary to save.
        filename: The name of the JSON file (e.g., "patient_data.json").

    Returns:
        A message indicating the success or failure of the operation.
    """
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return f"Successfully saved patient information to {filepath}"
    except Exception as e:
        return f"Error saving patient information to {filepath}: {e}"
        
CONVERSATION_COMPLETE_SIGNAL = "[CONVERSATION_COMPLETE]"

root_agent = LlmAgent(
    model=MODEL_NAME,
    name="patient_intake_agent",
    description="""An agent that collects patient information and stores it locally.""",
    instruction=patient_intake_prompt,
    tools=[save_to_json_file]
)

a2a_app = to_a2a(
    root_agent,
    host="app1",
    port=8001,  # Choose a port for your A2A service
    protocol="http"
) 
