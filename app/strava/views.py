from config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
from main import app


@app.get("/strava/login")
def strava_login():
    return {'response': 'strava login endpoint'}


@app.get("/strava/callback")
def strava_callback():
    return {'response': 'strava callback endpoint'}


@app.get("/strava/webhook")
def strava_webhook():
    return {'response': 'strava webhook endpoint'}

