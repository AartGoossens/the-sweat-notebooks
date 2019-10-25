from stravalib import Client

from config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET


async def refresh_access_token(athlete):
    client = Client()
    response = client.refresh_access_token(
        client_id=STRAVA_CLIENT_ID,
        client_secret=STRAVA_CLIENT_SECRET,
        refresh_token=athlete.refresh_token)

    await athlete.update(
        access_token=response['access_token'],
        refresh_token=response['refresh_token'],
        token_expiration_datetime=datetime.utcfromtimestamp(response['expires_at']).isoformat())

    return athlete
