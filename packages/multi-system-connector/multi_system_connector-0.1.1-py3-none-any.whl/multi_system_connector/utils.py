# multi_system_connector/utils.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env if present

# Required environment variables
REQUIRED_ENV_VARS = [
    "TENANT_ID",
    "CLIENT_ID",
    "CLIENT_SECRET",
    "SHAREPOINT_SITE_ID",
    "SHAREPOINT_LIST_NAME",
    "AZURE_AI_TENANT_ID",
    "AZURE_AI_CLIENT_ID",
    "AZURE_AI_CLIENT_SECRET",
    "AZURE_AI_PROJECT_ENDPOINT",
    "AZURE_AI_AGENT_ID"
]

# Check for missing env vars
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(
        f"\n Missing required environment variables: {', '.join(missing_vars)}\n"
        "Please create a .env file or set these variables in your environment.\n"
        "You can use the provided .env.example as a template."
    )

CONFIDENCE_THRESHOLD = 0.70

REQUIRED_ENTITIES = {
    "vendor_lookup": [],
    "create_vendor_request": ["vendor_name"],
    "search_text": []
}

SYSTEMS = {
    "SHAREPOINT": {
        "base_url": "https://graph.microsoft.com/v1.0",
        "site_path": os.getenv("SHAREPOINT_SITE_PATH"),
        "tenant_id": os.getenv("TENANT_ID"),
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "site_id": os.getenv("SHAREPOINT_SITE_ID"),
        "site_hostname": "nihilent.sharepoint.com",
        "list_name": os.getenv("SHAREPOINT_LIST_NAME")
    }
}

AZURE_AI_CONFIG = {
    "tenant_id": os.getenv("AZURE_AI_TENANT_ID"),
    "client_id": os.getenv("AZURE_AI_CLIENT_ID"),
    "client_secret": os.getenv("AZURE_AI_CLIENT_SECRET"),
    "project_endpoint": os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
    "agent_id": os.getenv("AZURE_AI_AGENT_ID")
}


def validate_entities_for_intent(intent_name: str, entities: dict) -> dict:
    """Check required entities for an intent"""
    required = REQUIRED_ENTITIES.get(intent_name, [])
    missing_required = [entity for entity in required if not entities.get(entity)]
    return {"valid": len(missing_required) == 0, "missing_required": missing_required}
