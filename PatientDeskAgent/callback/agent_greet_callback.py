from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional

def check_if_agent_greet(callback_context: CallbackContext) -> Optional[types.Content]:
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id

    # The state property of CallbackContext is already a delta-aware State object.
    # You can access and modify its content directly.
    # If 'greeted_agent' is not present, .get() will return the default (False).
    has_greeted = callback_context.state.get("greeted_agent", False)

    print(f"\n[Callback] Entering agent: {agent_name} (Inv: {invocation_id})")
    # To print the full state dictionary, you can use callback_context.state.to_dict()
    print(f"[Callback] Current State: {callback_context.state.to_dict()}")

    if not has_greeted:
        print(f"[Callback] State condition 'greeted_agent=False.")

        # Directly update the state object
        callback_context.state["greeted_agent"] = True
        # If you were also managing 'skip_llm_agent' here, you'd set it directly too:
        # callback_context.state["skip_llm_agent"] = True

        return types.Content(
            parts=[types.Part(text="Hi, how can I help you today? Are you looking to learn about a register as a new patient, schedule an appointment, or medication?")],
            role="model"
        )
    else:
        print(f"[Callback] State condition already met: Proceeding with agent {agent_name}.")

        # Return None to allow the LlmAgent's normal execution
        return None

