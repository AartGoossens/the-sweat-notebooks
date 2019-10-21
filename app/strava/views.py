from starlette.responses import RedirectResponse
from starlette.requests import Request
from stravalib import Client

from config import APP_URL, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
from main import app
from strava.schemas import Event


@app.get('/strava/login')
def strava_login():
    client = Client()
    authorize_url = client.authorization_url(
        client_id=STRAVA_CLIENT_ID,
        redirect_uri=f'{APP_URL}/strava/callback')

    return RedirectResponse(authorize_url)


@app.get('/strava/callback')
def strava_callback(code: str, scope: str, state: str = None):
    client = Client()
    response = client.exchange_code_for_token(
        client_id=STRAVA_CLIENT_ID,
        client_secret=STRAVA_CLIENT_SECRET,
        code=code)
    
    return response


@app.post('/strava/subscription')
def strava_create_subscription():
    client = Client()
    
    response = client.create_subscription(
        client_id=STRAVA_CLIENT_ID,
        client_secret=STRAVA_CLIENT_SECRET,
        callback_url=f'{APP_URL}/strava/webhook',
        verify_token='some verify token')

    return response


@app.delete('/strava/subscription')
def strava_delete_subscription():
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

    hub_challenge = request.query_params['hub.challenge']
    hub_verify_token = request.query_params.get('hub.verify_token', None)

    return {'hub.challenge': hub_challenge}


@app.post('/strava/webhook')
def strava_webhook(event: Event):
    return {'message': 'ok'}
