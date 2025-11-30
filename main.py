import os

import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.plugins.logging_plugin import LoggingPlugin

AGENT_DIR = "./"
SERVE_WEB_INTERFACE = True

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=SERVE_WEB_INTERFACE,
    logo_text="Healthcare FrontDesk ADK",
    logo_image_url="healthcare_logo.jpg",
    extra_plugins=["google.adk.plugins.logging_plugin.LoggingPlugin"]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
