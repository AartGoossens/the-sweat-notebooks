from dataclasses import dataclass
import pytest
from starlette.testclient import TestClient

from ..auth import create_jwt_token
from ..config import ADMIN_IDS, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
from ..server import app
from .models import StravaAthlete


class TestStravaViews:
    @pytest.fixture
    def test_client(self):
        return TestClient(app)

    @pytest.fixture
    def jwt_token_admin(self):
        return create_jwt_token(ADMIN_IDS[0])

    @pytest.fixture
    def jwt_token_not_admin(self):
        return create_jwt_token('some sub')

    def test_strava_login(self, test_client):
        response = test_client.get('/strava/login', allow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers['location'] == (
            'https://www.strava.com/oauth/authorize?'
            'client_id=1337&'
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
        mocked_get_activities = mocker.patch('stravalib.Client.get_activities')
        mocked_get_activities = []

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
            ),
            allow_redirects=False

        )

        assert response.status_code == 307
        assert response.headers['location'] == '/reports'
        mocked_exchange_code_for_token.assert_called_once_with(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            code='some code')

        mocked_get_athlete.assert_called_once()

        assert strava_athletes_count + 1 == await StravaAthlete.objects.count()


    def test_strava_create_subscription(self, test_client, mocker, jwt_token_admin):
        m = mocker.patch('stravalib.Client.create_subscription')

        response = test_client.post(
            url='/strava/subscription',
            cookies={'jwt_token': jwt_token_admin})

        assert response.status_code == 200
        m.assert_called_once_with(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            callback_url='http://localhost:8000/strava/webhook',
            verify_token='some verify token')

    def test_strava_create_subscription_unauthenticated(self, test_client, mocker):
        m = mocker.patch('stravalib.Client.create_subscription')

        response = test_client.post(url='/strava/subscription')

        assert response.status_code == 401

    def test_strava_create_subscription_unauthorized(self, test_client, mocker, jwt_token_not_admin):
        m = mocker.patch('stravalib.Client.create_subscription')

        response = test_client.post(
            url='/strava/subscription',
            cookies={'jwt_token': jwt_token_not_admin})

        assert response.status_code == 403

    def test_strava_delete_subscription(self, test_client, mocker, jwt_token_admin):
        mocked_list = mocker.patch('stravalib.Client.list_subscriptions')

        @dataclass
        class MockedSubscription:
            id: int

        mocked_delete = mocker.patch('stravalib.Client.delete_subscription')
        mocked_delete.return_value = [MockedSubscription(i) for i in range(2)]

        response = test_client.delete(
            url='/strava/subscription',
            cookies={'jwt_token': jwt_token_admin})

        assert response.status_code == 200
        mocked_list.assert_called_once_with(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET)
        mocked_list.call_count == 3

    def test_strava_delete_subscription_unauthenticated(self, test_client):
        response = test_client.delete(url='/strava/subscription')

        assert response.status_code == 401

    def test_strava_delete_subscription_unauthorized(self, test_client, jwt_token_not_admin):
        response = test_client.delete(
            url='/strava/subscription',
            cookies={'jwt_token': jwt_token_not_admin})

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_strava_webhook(self, test_client, mocker):
        # @TODO figure out why it has to be mocked like this, not reports.utils.generate_report
        m = mocker.patch('app.strava.tasks.generate_report')
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

        athlete = await StravaAthlete.objects.get(id=2)

        m.assert_called_once_with(athlete, 1360128428)

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

    def test_list_strava_athletes(self, test_client, jwt_token_admin):
        response = test_client.get(
            url='/strava/athletes',
            cookies={'jwt_token': jwt_token_admin})
        
        assert response.status_code == 200
        athletes = response.json()

        assert len(athletes) == 5
        athlete = athletes[0]
        assert 'id' in athlete
        assert 'access_token' in athlete
        assert 'refresh_token' in athlete
        assert 'token_expiration_datetime' in athlete

    def test_list_strava_athletes_unauthenticated(self, test_client, jwt_token_admin):
        response = test_client.get(url='/strava/athletes')
        
        assert response.status_code == 401

    def test_list_strava_athletes_unauthorized(self, test_client, jwt_token_not_admin):
        response = test_client.get(
            url='/strava/athletes',
            cookies={'jwt_token': jwt_token_not_admin})
        
        assert response.status_code == 403

    def test_get_strava_athlete(self, test_client, jwt_token_admin):
        response = test_client.get(
            url='/strava/athletes/1',
            cookies={'jwt_token': jwt_token_admin})
        
        assert response.status_code == 200
        athlete = response.json()

        assert athlete['id'] == 1
        assert athlete['access_token'] == 'some access token'
        assert athlete['refresh_token'] == 'some refresh token'
        assert 'token_expiration_datetime' in athlete

    def test_get_strava_athlete_unauthorized(self, test_client):
        response = test_client.get(url='/strava/athletes/1')
        
        assert response.status_code == 401

    def test_get_strava_athlete(self, test_client, jwt_token_not_admin):
        response = test_client.get(
            url='/strava/athletes/1',
            cookies={'jwt_token': jwt_token_not_admin})
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_strava_athlete(self, test_client, mocker, jwt_token_admin):
        mocked_deauthorize = mocker.patch('stravalib.Client.deauthorize')

        assert await StravaAthlete.objects.count() == 5

        response = test_client.delete(
            url='/strava/athletes/1',
            cookies={'jwt_token': jwt_token_admin})

        assert response.status_code == 200
        athlete = response.json()

        assert athlete['id'] == 1
        assert athlete['access_token'] == 'some access token'
        assert athlete['refresh_token'] == 'some refresh token'
        assert 'token_expiration_datetime' in athlete

        assert await StravaAthlete.objects.count() == 4

        mocked_deauthorize.assert_called_once()

    def test_delete_strava_athlete_unauthorized(self, test_client):
        response = test_client.delete(url='/strava/athletes/1')

        assert response.status_code == 401

    def test_delete_strava_athlete_unauthenticated(self, test_client, jwt_token_not_admin):
        response = test_client.delete(
            url='/strava/athletes/1',
            cookies={'jwt_token': jwt_token_not_admin})

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_process_activity(self, test_client, mocker, jwt_token_admin):
        m = mocker.patch('app.strava.tasks.generate_report')
        response = test_client.post(
            url='/strava/athletes/2/process_activity',
            cookies={'jwt_token': jwt_token_admin},
            json=dict(id=1337))

        assert response.status_code == 202
        athlete = await StravaAthlete.objects.get(id=2)
        m.assert_called_once_with(athlete, 1337)

    @pytest.mark.asyncio
    async def test_process_activity_unauthorized(self, test_client, jwt_token_not_admin):
        response = test_client.post(
            url='/strava/athletes/1/process_activity',
            cookies={'jwt_token': jwt_token_not_admin},
            json=dict(id=1337))

        assert response.status_code == 403
