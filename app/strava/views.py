import shutil
from datetime import datetime
from pathlib import Path

from fastapi import BackgroundTasks
from orm import exceptions as orm_exceptions
from starlette.responses import RedirectResponse
from starlette.requests import Request
from stravalib import Client, exc as stravalib_exceptions

from config import APP_URL, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
from main import app
from reports.utils import get_or_create_athlete_dir
from strava.models import StravaAthlete
from strava.schemas import Event
from strava.tasks import handle_event, new_athlete
from strava.utils import refresh_access_token


@app.get('/strava/login')
def strava_login():
    client = Client()
    authorize_url = client.authorization_url(
        client_id=STRAVA_CLIENT_ID,
        redirect_uri=f'{APP_URL}/strava/callback')

    return RedirectResponse(authorize_url)


@app.get('/strava/callback')
async def strava_callback(background_task: BackgroundTasks, code: str, scope: str, state: str = None):
    client = Client()
    token_response = client.exchange_code_for_token(
        client_id=STRAVA_CLIENT_ID, client_secret=STRAVA_CLIENT_SECRET,
        code=code)

    client = Client(access_token=token_response['access_token'])
    athlete = client.get_athlete()
    
    try:
        strava_athlete = await StravaAthlete.objects.get(id=athlete.id)
    except orm_exceptions.NoMatch:
        strava_athlete = await StravaAthlete.objects.create(
            id=athlete.id,
            access_token=token_response['access_token'],
            refresh_token=token_response['refresh_token'],
            token_expiration_datetime=datetime.utcfromtimestamp(token_response['expires_at']).isoformat())

        background_task.add_task(new_athlete, strava_athlete)
        get_or_create_athlete_dir(strava_athlete)
    
    response = RedirectResponse('/reports')
    response.set_cookie(
        key="strava_athlete_id",
        value=str(strava_athlete.id),
        httponly=True)
    return response


@app.post('/strava/subscription')
def strava_create_subscription():
    # @TODO add secret to the callback url to prevent abuse
    client = Client()
    
    response = client.create_subscription(
        client_id=STRAVA_CLIENT_ID,
        client_secret=STRAVA_CLIENT_SECRET,
        callback_url=f'{APP_URL}/strava/webhook',
        verify_token='some verify token')

    return response


@app.delete('/strava/subscription')
def strava_delete_subscription():
    # @TODO add authorization
    client = Client()

    subscriptions = client.list_subscriptions(
        client_id=STRAVA_CLIENT_ID,
        client_secret=STRAVA_CLIENT_SECRET)

    i = 0
    for subscription in subscriptions:
        client.delete_subscription(
            subscription_id=subscription.id,
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET)
        i += 1
    
    return {'message': f'deleted {i} subscriptions'}


@app.get('/strava/webhook')
def strava_webhook_validation(request: Request):
    '''
    So Strava is fucking around with query param standards in a way that FastAPI cannot handle them natively.
    There is no other way then to go back in time and parse the query params ourselves.
    Shoot me.
    '''
    # @TODO add authorization

    hub_challenge = request.query_params['hub.challenge']
    hub_verify_token = request.query_params.get('hub.verify_token', None)

    return {'hub.challenge': hub_challenge}


@app.post('/strava/webhook')
def strava_webhook(event: Event, background_task: BackgroundTasks):
    # @TODO add a secret to this path to prevent abuse
    background_task.add_task(handle_event, event)
    return {'message': 'ok'}


@app.get('/strava/athletes')
async def list_strava_athletes():
    # @TODO add authorization
    strava_athletes = await StravaAthlete.objects.all()

    return strava_athletes


@app.get('/strava/athletes/{strava_athlete_id}')
async def get_strava_athletes(strava_athlete_id: int):
    # @TODO add authorization
    strava_athlete = await StravaAthlete.objects.get(id=strava_athlete_id)

    return strava_athlete


@app.delete('/strava/athletes/{strava_athlete_id}')
async def delete_strava_athletes(strava_athlete_id: int):
    # @TODO add authorization
    strava_athlete = await StravaAthlete.objects.get(id=strava_athlete_id)

    client = Client(strava_athlete.access_token)
    try:
        client.deauthorize()
    except stravalib_exceptions.AccessUnauthorized:
        strava_athlete = await refresh_access_token(strava_athlete)
        client = Client(strava_athlete.access_token)
        client.deauthorize()

    athlete_dir = get_or_create_athlete_dir(strava_athlete)
    shutil.rmtree(athlete_dir)

    await strava_athlete.delete()

    return strava_athlete
