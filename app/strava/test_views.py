from dataclasses import dataclass
import pytest
from starlette.testclient import TestClient

from config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
from server import app
from strava.models import StravaAthlete


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

    @pytest.mark.asyncio
    async def test_strava_callback(self, test_client, mocker):
        mocked_exchange_code_for_token = mocker.patch('stravalib.Client.exchange_code_for_token')
        mocked_exchange_code_for_token.return_value = {
            'access_token': 'some access token',
            'refresh_token': 'some refresh token',
            'expires_at':13371337
        }

        @dataclass
        class StravaAthleteResponse:
            id: int

        mocked_get_athlete = mocker.patch('stravalib.Client.get_athlete')
        mocked_get_athlete.return_value = StravaAthleteResponse(id=1337)

        strava_athletes_count = await StravaAthlete.objects.count()

        response = test_client.get(
            url='/strava/callback',
            params=dict(
                code='some code',
                scope='some scope'
            )
        )

        assert response.status_code == 200
        assert response.json() == {
            'message': 'Athlete with id 1337 created'
        }
        mocked_exchange_code_for_token.assert_called_once_with(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            code='some code')

        mocked_get_athlete.assert_called_once()

        assert strava_athletes_count + 1 == await StravaAthlete.objects.count()


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

    def test_strava_webhook(self, test_client, mocker):
        m = mocker.patch('tasks.handle_new_event')
        response = test_client.post(
            '/strava/webhook',
            json={
                'aspect_type': 'update',
                'event_time': 1516126040,
                'object_id': 1360128428,
                'object_type': 'activity',
                'owner_id': 2,
                'subscription_id': 120475,
                'updates': {
                    'title': 'Messy'
                }
            }
        )
        
        assert response.status_code == 200
        assert response.json() == {'message': 'ok'}
        m.assert_called_once()

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

    def test_list_strava_athletes(self, test_client):
        response = test_client.get('/strava/athletes')
        
        athletes = response.json()

        assert len(athletes) == 5
        athlete = athletes[0]
        assert 'id' in athlete
        assert 'access_token' in athlete
        assert 'refresh_token' in athlete
        assert 'token_expiration_datetime' in athlete

    def test_get_strava_athlete(self, test_client):
        response = test_client.get('/strava/athletes/1')
        
        athlete = response.json()

        assert athlete['id'] == 1
        assert athlete['access_token'] == 'some access token'
        assert athlete['refresh_token'] == 'some refresh token'
        assert 'token_expiration_datetime' in athlete

    @pytest.mark.asyncio
    async def test_delete_strava_athlete(self, test_client, mocker):
        mocked_deauthorize = mocker.patch('stravalib.Client.deauthorize')

        assert await StravaAthlete.objects.count() == 5

        response = test_client.delete('/strava/athletes/1')

        athlete = response.json()

        assert athlete['id'] == 1
        assert athlete['access_token'] == 'some access token'
        assert athlete['refresh_token'] == 'some refresh token'
        assert 'token_expiration_datetime' in athlete

        assert await StravaAthlete.objects.count() == 4

        mocked_deauthorize.assert_called_once()
