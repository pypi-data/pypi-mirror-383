# multi_system_connector/main.py

from fastapi import FastAPI, Request
from typing import Optional
from datetime import datetime
from .utils import CONFIDENCE_THRESHOLD, validate_entities_for_intent, SYSTEMS
from .sharepoint import execute_sharepoint_request
from .azure_ai import query_azure_ai_assistant

app = FastAPI(title="Multi-System Connector with AI Assistant")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "systems_configured": list(SYSTEMS.keys())}

@app.get("/systems")
async def get_systems():
    return {"systems": list(SYSTEMS.keys())}

@app.post("/process")
async def process_query(request: Request, use_mock: Optional[bool] = True):
    body = await request.json()
    intents = body.get("intents", [])
    entities_array = body.get("entities", [])

    if not intents:
        return {"error": "At least one intent is required"}

    entities = {e["type"]: e["value"] for e in entities_array if e.get("type") and e.get("value")}

    results = []
    for intent in intents:
        intent_name = intent.get("name")
        confidence = intent.get("confidence", 0)
        utterance = intent.get("utterance", "")

        if confidence < CONFIDENCE_THRESHOLD:
            results.append({"intent_name": intent_name, "status": "skipped", "reason": f"Confidence {confidence} below threshold"})
            continue

        entity_validation = validate_entities_for_intent(intent_name, entities)
        if not entity_validation["valid"]:
            results.append({"intent_name": intent_name, "status": "incomplete_entities", "missing_required": entity_validation["missing_required"]})
            continue

        if intent_name == "search_text":
            ai_response = query_azure_ai_assistant(utterance, entities)
            results.append({"intent_name": intent_name, "status": "success", "ai_response": ai_response})
        else:
            method_map = {"vendor_lookup": "GET", "create_vendor_request": "POST"}
            method = method_map.get(intent_name)
            result = execute_sharepoint_request(method=method, data=entities)
            results.append({"intent_name": intent_name, "status": "success" if "error" not in result else "error", "result": result})

    return {"results": results}
