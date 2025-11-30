import json # Needed for pretty printing dicts
import asyncio
import datetime
from typing import Any, Dict
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

# session_service = InMemorySessionService()

# healthcare_runner = Runner(
#     agent=root_agent,
#     app_name=APP_NAME,
#     session_service=session_service
# )

# async def call_agent_and_print(
#     runner_instance: Runner,
#     agent_instance: LlmAgent,
#     session_id: str,
#     query_json: str
# ) -> bool: # Added return type hint for the new functionality
#     """Sends a query to the specified agent/runner and prints results.
#        Returns True if the conversation complete signal was detected, False otherwise.
#     """
#     print(f"\n>>> Calling Agent: '{agent_instance.name}' | Query: {query_json}")

#     user_content = types.Content(role='user', parts=[types.Part(text=query_json)])

#     final_response_content = "No final response received."
#     conversation_finished = False # Flag to indicate if agent signals completion

#     async for event in runner_instance.run_async(user_id=USER_ID, session_id=session_id, new_message=user_content):
#         if event.is_final_response() and event.content and event.content.parts:
#             final_response_content = event.content.parts[0].text
#             # Check for the conversation complete signal
#             if CONVERSATION_COMPLETE_SIGNAL in final_response_content:
#                 conversation_finished = True
#                 # Optionally remove the signal from the displayed response
#                 final_response_content = final_response_content.replace(CONVERSATION_COMPLETE_SIGNAL, "").strip()

#     print(f"<<< Agent '{agent_instance.name}' Response: {final_response_content}")

#     current_session = await session_service.get_session(app_name=APP_NAME,
#                                                   user_id=USER_ID,
#                                                   session_id=session_id)
#     # Check if current_session or current_session.state is None before calling .get()
#     if current_session and current_session.state:
#         stored_output = current_session.state.get(agent_instance.output_key)
#     else:
#         stored_output = None # Or handle as appropriate if session might be empty

#     # Pretty print if the stored output looks like JSON (likely from output_schema)
#     print(f"--- Session State ['{agent_instance.output_key}']: ", end="")
#     try:
#         if stored_output: # Only try to parse if there's content
#             parsed_output = json.loads(stored_output)
#             print(json.dumps(parsed_output, indent=2))
#         else:
#             print("No output stored in session state.")
#     except (json.JSONDecodeError, TypeError):
#          # Otherwise, print as string
#         print(stored_output)
#     print("-" * 30)
    
#     return conversation_finished # Return the flag

# async def main():
#     print("--- Starting Interactive Agent Session ---")
#     session_id = SESSION_ID_SCHEMA_AGENT # Use the predefined session ID
#     await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
#     print(f"Session '{session_id}' created for user '{USER_ID}'.")

#     # Initial greeting or prompt to kick off the conversation
#     # Agent will now initiate the information collection process
#     initial_message = "Hello."
#     conversation_complete = await call_agent_and_print(healthcare_runner, root_agent, session_id, initial_message)

#     while not conversation_complete: # Loop until agent signals completion
#         user_query = input("\nYour input: ")
#         if user_query.lower() == 'exit': # Still allow user to force exit
#             print("User forced exit. Ending session.")
#             break
        
#         conversation_complete = await call_agent_and_print(healthcare_runner, root_agent, session_id, user_query)

#     if conversation_complete:
#         print("\nAgent has signaled conversation completion. Session ended.")
# # # --- 7. Run Interactions ---
# # async def main():
# #     # Create separate sessions for clarity, though not strictly necessary if context is managed
# #     print("--- Creating Sessions ---")
# #     await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID_SCHEMA_AGENT)
# #     await call_agent_and_print(healthcare_runner, patient_intake_agent, SESSION_ID_SCHEMA_AGENT, 'Hi')

# if __name__ == "__main__":
#     asyncio.run(main()) 
