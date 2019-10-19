import pytest
from starlette.testclient import TestClient

from server import app


class TestStravaViews:
    @pytest.fixture
    def test_client(self):
        return TestClient(app)

    def test_strava_login(self, test_client):
        response = test_client.get('/strava/login')
        
        assert response.status_code == 200
        assert response.json() == {'response': 'strava login endpoint'}

    def test_strava_callback(self, test_client):
        response = test_client.get('/strava/callback')
        
        assert response.status_code == 200
        assert response.json() == {'response': 'strava callback endpoint'}

    def test_strava_webhook(self, test_client):
        response = test_client.get('/strava/webhook')
        
        assert response.status_code == 200
        assert response.json() == {'response': 'strava webhook endpoint'}
