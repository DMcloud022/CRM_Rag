import pytest
from fastapi.testclient import TestClient
from main import app  # Assuming your FastAPI app is in main.py
from models.lead import Lead
from models.oauth import OAuthCredentials

client = TestClient(app)

def test_send_to_crm():
    lead = Lead(name="John Doe", email="john@example.com")
    response = client.post("/send-to-crm/salesforce", json=lead.dict())
    assert response.status_code == 200
    assert "Lead sent to salesforce CRM" in response.json()["message"]

def test_oauth_initiate():
    response = client.get("/oauth/salesforce/initiate")
    assert response.status_code == 200
    assert "authUrl" in response.json()

def test_oauth_callback():
    response = client.get("/oauth/salesforce/callback?code=test_code")
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_unsupported_crm():
    response = client.post("/send-to-crm/unsupported", json={})
    assert response.status_code == 400
    assert "Unsupported CRM" in response.json()["detail"]