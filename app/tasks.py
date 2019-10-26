import json
from pathlib import Path

import nbformat
import papermill as pm
from nbconvert import HTMLExporter

from strava.models import StravaAthlete
from config import (
    NOTEBOOK_TEMPLATE_NAME, NOTEBOOK_TEMPLATES_PATH, REPORT_OUTPUT_DIR
)


async def handle_new_event(event):
    athlete = await StravaAthlete.objects.get(id=event.owner_id)

    input_path = f'{NOTEBOOK_TEMPLATES_PATH}{NOTEBOOK_TEMPLATE_NAME}.ipynb'
    output_dir = Path(f'{REPORT_OUTPUT_DIR}{athlete.id}').mkdir(exist_ok=True)
    output_path = f'{REPORT_OUTPUT_DIR}{athlete.id}/{event.object_id}-{NOTEBOOK_TEMPLATE_NAME}.ipynb'

    # @TODO pass Strava activity detail, activity stream and athlete json as parameters
    pm.execute_notebook(
        input_path=input_path,
        output_path=output_path,
        parameters=dict(
            strava_athlete=dict(athlete),
            event=dict(event)
        )
    )

    with open(output_path, 'r') as f:
        notebook = nbformat.reads(f.read(), as_version=4)
    html_exporter = HTMLExporter()
    html_exporter.template_file = 'basic'
    body, _ = html_exporter.from_notebook_node(notebook)

    with open(f'{REPORT_OUTPUT_DIR}{athlete.id}/{event.object_id}-{NOTEBOOK_TEMPLATE_NAME}.html', 'w') as f:
        f.write(body)
