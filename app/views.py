from fastapi import Cookie
from starlette.responses import RedirectResponse
from starlette.requests import Request
from stravalib import Client, exc as stravalib_exceptions

from config import APP_URL, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
from main import app
from strava.models import StravaAthlete
from strava.schemas import Event
from strava.tasks import handle_event
from strava.utils import refresh_access_token


@app.get('/')
def root(strava_athlete_id: str = Cookie(None)):
    if strava_athlete_id is None:
        return RedirectResponse(f'/login')
    else:
        return RedirectResponse(f'/reports')

@app.get('/login')
def login():
    return RedirectResponse(f'/strava/login')


@app.get('/logout')
def logout(strava_athlete_id: str = Cookie(None)):
    response = RedirectResponse('/login')
    response.delete_cookie('strava_athlete_id')
    return response
