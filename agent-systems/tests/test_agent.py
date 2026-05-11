import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200

@patch('app.main._agent')
def test_satellite_report_returns_200(mock_agent):
    mock_agent.invoke.return_value = {
        'output': '=== SATELLITE INTELLIGENCE REPORT ===\nISS: 420km altitude...',
        'intermediate_steps': [('action1','obs1'), ('action2','obs2')],
    }
    r = client.post('/satellite-report',
json={'satellite_name':'ISS','include_news':True})
    assert r.status_code == 200
    data = r.json()
    assert 'report' in data
    assert data['steps_taken'] == 2

def test_empty_satellite_name_rejected():
    r = client.post('/satellite-report',
json={'satellite_name':'','include_news':True})
    assert r.status_code == 422
