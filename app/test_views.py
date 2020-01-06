import pytest
from starlette.testclient import TestClient

from .auth import create_jwt_token
from .config import ADMIN_IDS, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
from .server import app
from .strava.models import StravaAthlete


class TestViews:
    @pytest.fixture
    def test_client(self):
        return TestClient(app)

    def test_home(self, test_client):
        response = test_client.get(
            url='/',
            allow_redirects=False)

        assert response.status_code == 307
        assert response.headers['location'] == '/reports'

    def test_about(self, test_client):
        response = test_client.get('/about')

        assert response.status_code == 200
        assert '<i>The Sweat Notebooks</i> is an application' in response.text

    def test_login(self, test_client):
        response = test_client.get('/login')

        assert response.status_code == 200
        assert '<a href="/strava/login">' in response.text

    def test_logout(self, test_client):
        response = test_client.get(
            url='/logout',
            cookies={'some cookie': 'some cookie value'},
            allow_redirects=False)

        assert response.status_code == 307
        assert response.headers['location'] == '/login'
        assert 'some cookie' not in response.cookies

    def test_static(self, test_client):
        response = test_client.get('/static/favicon.png')

        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/png'
        assert response.headers['content-length'] == '1124'
