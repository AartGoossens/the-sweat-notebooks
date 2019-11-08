from datetime import datetime, timedelta
from pathlib import Path

import nbformat
import papermill
from nbconvert import HTMLExporter

from reports.utils import generate_report
from strava.models import StravaAthlete
from strava.schemas import EventObjectType
from strava.utils import refresh_access_token
from config import (
    NOTEBOOK_TEMPLATE_NAME, NOTEBOOK_TEMPLATES_PATH, REPORT_OUTPUT_DIR
)


async def handle_event(event):
    if event.object_type != EventObjectType.activity:
        return

    athlete = await StravaAthlete.objects.get(id=event.owner_id)
    if athlete.token_expiration_datetime < datetime.now() + timedelta(minutes=5):
        athlete = await refresh_access_token(athlete)

    generate_report(athlete, event.object_id)
