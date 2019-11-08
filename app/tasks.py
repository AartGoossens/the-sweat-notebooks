from datetime import datetime, timedelta
from pathlib import Path

import nbformat
import papermill
from nbconvert import HTMLExporter

from strava.models import StravaAthlete
from strava.schemas import EventObjectType
from utils import refresh_access_token
from config import (
    NOTEBOOK_TEMPLATE_NAME, NOTEBOOK_TEMPLATES_PATH, REPORT_OUTPUT_DIR
)


async def handle_new_event(event):
    if event.object_type != EventObjectType.activity:
        return

    input_path = f'{NOTEBOOK_TEMPLATES_PATH}{NOTEBOOK_TEMPLATE_NAME}.ipynb'
    output_dir = Path(f'{REPORT_OUTPUT_DIR}{athlete.id}').mkdir(exist_ok=True)
    output_path = f'{REPORT_OUTPUT_DIR}{athlete.id}/{event.object_id}-{NOTEBOOK_TEMPLATE_NAME}.ipynb'

    athlete = await StravaAthlete.objects.get(id=event.owner_id)
    if athlete.token_expiration_datetime < datetime.now() + timedelta(minutes=5):
        athlete = await refresh_access_token(athlete)

    papermill.execute_notebook(
        input_path=input_path,
        output_path=output_path,
        parameters=dict(
            access_token=athlete.access_token,
            activity_id=event.object_id
        )
    )

    with open(output_path, 'r') as f:
        notebook = nbformat.reads(f.read(), as_version=4)
    html_exporter = HTMLExporter()
    html_exporter.template_file = 'full'
    body, _ = html_exporter.from_notebook_node(notebook)

    with open(f'{REPORT_OUTPUT_DIR}{athlete.id}/{event.object_id}-{NOTEBOOK_TEMPLATE_NAME}.html', 'w') as f:
        f.write(body)
