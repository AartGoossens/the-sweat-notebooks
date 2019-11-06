import json
from pathlib import Path

import nbformat
import papermill
from nbconvert import HTMLExporter
from stravalib import Client, exc as stravalib_exceptions

from strava.models import StravaAthlete
from utils import refresh_access_token
from config import (
    NOTEBOOK_TEMPLATE_NAME, NOTEBOOK_TEMPLATES_PATH, REPORT_OUTPUT_DIR
)


STRAVA_STREAM_TYPES = [
    'time', 'latlng', 'distance', 'altitude', 'velocity_smooth', 'heartrate',
    'cadence', 'watts', 'temp', 'moving', 'grade_smooth'
]


async def handle_new_event(event):
    athlete = await StravaAthlete.objects.get(id=event.owner_id)

    input_path = f'{NOTEBOOK_TEMPLATES_PATH}{NOTEBOOK_TEMPLATE_NAME}.ipynb'
    output_dir = Path(f'{REPORT_OUTPUT_DIR}{athlete.id}').mkdir(exist_ok=True)
    output_path = f'{REPORT_OUTPUT_DIR}{athlete.id}/{event.object_id}-{NOTEBOOK_TEMPLATE_NAME}.ipynb'

    client = Client(athlete.access_token)
    while True:
        try:
            strava_athlete_response = client.get_athlete()
            activity_detail_response = client.get_activity(event.object_id)
            activity_streams_response = client.get_activity_streams(
                activity_id=event.object_id,
                types=STRAVA_STREAM_TYPES,
                series_type='time'
            )
        except stravalib_exceptions.AccessUnauthorized:
            athlete = await refresh_access_token(athlete)
            client = Client(athlete.access_token)
        else:
            break

    strava_athlete = strava_athlete_response.to_dict()
    strava_activity_detail = activity_detail_response.to_dict()
    strava_activity_streams = {key: val.data for key, val in activity_streams_response.items()}

    papermill.execute_notebook(
        input_path=input_path,
        output_path=output_path,
        parameters=dict(
            athlete=strava_athlete,
            activity_detail=strava_activity_detail,
            activity_streams=strava_activity_streams
        )
    )

    with open(output_path, 'r') as f:
        notebook = nbformat.reads(f.read(), as_version=4)
    html_exporter = HTMLExporter()
    html_exporter.template_file = 'full'
    body, _ = html_exporter.from_notebook_node(notebook)

    with open(f'{REPORT_OUTPUT_DIR}{athlete.id}/{event.object_id}-{NOTEBOOK_TEMPLATE_NAME}.html', 'w') as f:
        f.write(body)
