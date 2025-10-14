# test_main.py
import os
from fastapi.testclient import TestClient

# Import the app from your installed package
# If your package is named multi_system_connector
from multi_system_connector.main import app

# Ensure .env file is present
os.environ["TENANT_ID"] = "dummy"
os.environ["CLIENT_ID"] = "dummy"
os.environ["CLIENT_SECRET"] = "dummy"
os.environ["SHAREPOINT_SITE_ID"] = "dummy"
os.environ["SHAREPOINT_LIST_NAME"] = "dummy"
os.environ["AZURE_AI_TENANT_ID"] = "dummy"
os.environ["AZURE_AI_CLIENT_ID"] = "dummy"
os.environ["AZURE_AI_CLIENT_SECRET"] = "dummy"
os.environ["AZURE_AI_PROJECT_ENDPOINT"] = "https://dummy-endpoint/"
os.environ["AZURE_AI_AGENT_ID"] = "dummy"

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    print("Health endpoint output:", json_data)
    assert "status" in json_data
    assert json_data["status"] == "healthy"

def test_systems():
    response = client.get("/systems")
    assert response.status_code == 200
    json_data = response.json()
    print("Systems endpoint output:", json_data)
    assert "SHAREPOINT" in json_data["systems"]
