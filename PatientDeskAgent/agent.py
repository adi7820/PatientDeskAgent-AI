import datetime
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.apps import App
from google.adk.runners import Runner
from dotenv import load_dotenv
import json # Needed for pretty printing dicts
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.plugins.logging_plugin import LoggingPlugin
import os
from .callback.agent_greet_callback import check_if_agent_greet

os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
CONVERSATION_COMPLETE_SIGNAL = "[CONVERSATION_COMPLETE]"
APP_NAME = "agent_hackathon"
USER_ID = "test_user_456"
SESSION_ID_TOOL_AGENT = "session_tool_agent_xyz"
SESSION_ID_SCHEMA_AGENT = "session_schema_agent_xyz"

patient_intake_agent_remote = RemoteA2aAgent(
    name="patient_intake_agent_remote",
    description="An agent that collects patient information and stores it locally.",
    agent_card="http://app1:8001/.well-known/agent-card.json"
)

patient_appointment_agent_remote = RemoteA2aAgent(
    name="patient_appointment_agent_remote",
    description="An agent that helps with scheduling and managing patient appointments.",
    agent_card="http://app2:8002/.well-known/agent-card.json"
)

medical_lookup_agent_remote = RemoteA2aAgent(
    name="medical_lookup_agent_remote",
    description="An agent that provides information about medications and medical conditions.",
    agent_card="http://app3:8003/.well-known/agent-card.json"
)

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

root_agent = LlmAgent(
    model="gemini-2.0-flash",  # Or an appropriate model for your use case
    name="primary_assistant",
    instruction=f"""
        You are a helpful customer support assistant for healthcare patients and administrators.
        Your primary role is to determine what the customer needs help with, whether they want to inquire about medication, make appointments, or register as a new patient.

        If a customer requests to see the list of current medications for a patient, describe their symptoms for making an appointment, mention they want to register as a patient,
        delegate the task to the appropriate specialized assistant by invoking the corresponding tool. You are not able to retrieve these information or make these types of changes yourself.
        Only the specialized assistants are given permission to do this for the user.

        The user is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls.
        Provide detailed information to the customer, and always double-check the database before concluding that information is unavailable.
        When searching, be persistent. Expand your query bounds if the first search returns no results.
        If a search comes up empty, expand your search before giving up.

        Current time: {current_time}.
        """,
    sub_agents=[
        patient_intake_agent_remote,
        patient_appointment_agent_remote,
        medical_lookup_agent_remote,
    ],
    before_agent_callback=check_if_agent_greet
)

# session_service = InMemorySessionService()

# healthcare_runner = Runner(
#     agent=root_agent,
#     app_name=APP_NAME,
#     session_service=session_service,
#     plugins = [LoggingPlugin()]
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
