from dataclasses import dataclass
import pytest
from starlette.testclient import TestClient

from config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
from server import app


class TestStravaViews:
    @pytest.fixture
    def test_client(self):
        return TestClient(app)

    def test_strava_login(self, test_client):
        response = test_client.get('/strava/login', allow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers['location'] == (
            'https://www.strava.com/oauth/authorize?'
            'client_id=6218&'
            'redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fstrava%2Fcallback&'
            'approval_prompt=auto&'
            'response_type=code&'
            'scope=read%2Cactivity%3Aread'
        )

    def test_strava_callback(self, test_client, mocker):
        m = mocker.patch('stravalib.Client.exchange_code_for_token')
        m.return_value = {
            'access_token': 'some access token',
            'refresh_token': 'some refresh token',
            'expires_at':13371337
        }

        response = test_client.get(
            url='/strava/callback',
            params=dict(
                code='some code',
                scope='some scope'
            )
        )

        assert response.status_code == 200
        assert response.json() == {
            'access_token': 'some access token',
            'refresh_token': 'some refresh token',
            'expires_at':13371337
        }
        m.assert_called_once_with(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            code='some code')

    def test_strava_create_subscription(self, test_client, mocker):
        m = mocker.patch('stravalib.Client.create_subscription')

        response = test_client.post(url='/strava/subscription')

        assert response.status_code == 200
        m.assert_called_once_with(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            callback_url='http://localhost:8000/strava/webhook',
            verify_token='some verify token')

    def test_strava_delete_subscription(self, test_client, mocker):
        mocked_list = mocker.patch('stravalib.Client.list_subscriptions')

        @dataclass
        class MockedSubscription:
            id: int

        mocked_delete = mocker.patch('stravalib.Client.delete_subscription')
        mocked_delete.return_value = [MockedSubscription(i) for i in range(2)]

        response = test_client.delete(url='/strava/subscription')

        assert response.status_code == 200
        mocked_list.assert_called_once_with(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET)
        mocked_list.call_count == 3

    def test_strava_webhook(self, test_client):
        response = test_client.post(
            '/strava/webhook',
            json={
                'aspect_type': 'update',
                'event_time': 1516126040,
                'object_id': 1360128428,
                'object_type': 'activity',
                'owner_id': 134815,
                'subscription_id': 120475,
                'updates': {
                    'title': 'Messy'
                }
            }
        )
        
        assert response.status_code == 200
        assert response.json() == {'message': 'ok'}

    def test_strava_webhook_validation(self, test_client):
        response = test_client.get(
            url='/strava/webhook',
            params={
                'hub.mode': 'subscribe',
                'hub.challenge': 'some hub challenge',
                'hub.verify_token': 'some verify token'
            }
        )
        
        assert response.status_code == 200
        assert response.json() == {'hub.challenge': 'some hub challenge'}

    def test_strava_webhook_validation_no_verify_token(self, test_client):
        response = test_client.get(
            url='/strava/webhook',
            params={
                'hub.mode': 'subscribe',
                'hub.challenge': 'some hub challenge',
            }
        )
        
        assert response.status_code == 200
        assert response.json() == {'hub.challenge': 'some hub challenge'}
