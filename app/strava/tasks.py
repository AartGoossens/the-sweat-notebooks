import asyncio
from datetime import datetime, timedelta
from pathlib import Path

import nbformat
import papermill
from nbconvert import HTMLExporter
from stravalib import Client

from ..config import STRAVA_BACKFILL_COUNT
from ..reports.utils import generate_report
from .models import StravaAthlete
from .schemas import EventObjectType
from .utils import refresh_access_token


async def handle_event(event):
    if event.object_type != EventObjectType.activity:
        return

    athlete = await StravaAthlete.objects.get(id=event.owner_id)

    await process_activity(athlete, event.object_id)


async def process_activity(athlete, activity_id):
    if athlete.token_expiration_datetime < datetime.now() + timedelta(minutes=5):
        athlete = await refresh_access_token(athlete)

    generate_report(athlete, activity_id)


async def new_athlete(athlete):
    # This is a hack to have the callback response return before the reports are generated
    await asyncio.sleep(1)

    client = Client(athlete.access_token)

    for activity in client.get_activities(limit=STRAVA_BACKFILL_COUNT):
        # This is a hack to have this job not block all other requests
        await asyncio.sleep(1)
        if athlete.token_expiration_datetime < datetime.now() + timedelta(minutes=5):
            athlete = await refresh_access_token(athlete)

        generate_report(athlete, activity.id)

    await athlete.update(backfilled=True)
