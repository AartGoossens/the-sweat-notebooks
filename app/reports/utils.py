from datetime import datetime, timedelta
from pathlib import Path

import nbformat
import papermill
from nbconvert import HTMLExporter

from ..config import (
    NOTEBOOK_TEMPLATE_NAME, NOTEBOOK_TEMPLATES_PATH, REPORT_OUTPUT_DIR
)
from ..strava.models import StravaAthlete
from ..strava.schemas import EventObjectType
from ..strava.utils import refresh_access_token


def get_or_create_athlete_dir(athlete):
    athlete_dir = Path(f'{REPORT_OUTPUT_DIR}{athlete.id}')
    if not athlete_dir.exists():
        athlete_dir.mkdir()
    return athlete_dir


def generate_report(athlete, activity_id):

    input_path = f'{NOTEBOOK_TEMPLATES_PATH}{NOTEBOOK_TEMPLATE_NAME}.ipynb'
    output_dir = get_or_create_athlete_dir(athlete)
    output_path = f'{REPORT_OUTPUT_DIR}{athlete.id}/{activity_id}-{NOTEBOOK_TEMPLATE_NAME}.ipynb'

    papermill.execute_notebook(
        input_path=input_path,
        output_path=output_path,
        parameters=dict(
            access_token=athlete.access_token,
            activity_id=activity_id
        )
    )

    with open(output_path, 'r') as f:
        notebook = nbformat.reads(f.read(), as_version=4)
    html_exporter = HTMLExporter()
    html_exporter.template_file = 'full'
    body, _ = html_exporter.from_notebook_node(notebook)

    with open(f'{REPORT_OUTPUT_DIR}{athlete.id}/{activity_id}-{NOTEBOOK_TEMPLATE_NAME}.html', 'w') as f:
        f.write(body)
