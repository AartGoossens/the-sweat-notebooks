from datetime import datetime, timedelta
from pathlib import Path

import nbformat
import papermill
import scrapbook as sb
from nbconvert import HTMLExporter

from .models import Report
from ..config import (
    NOTEBOOK_TEMPLATE_NAME, NOTEBOOK_TEMPLATES_PATH, REPORT_OUTPUT_DIR
)
from ..strava.models import StravaAthlete
from ..strava.schemas import EventObjectType
from ..strava.utils import refresh_access_token


async def generate_report(athlete, activity_id):

    input_path = f'{NOTEBOOK_TEMPLATES_PATH}{NOTEBOOK_TEMPLATE_NAME}.ipynb'
    output_dir = Path(f'{REPORT_OUTPUT_DIR}')
    notebook_filename = f'{activity_id}.ipynb'
    html_filename = f'{activity_id}.html'
    notebook_path = f'{REPORT_OUTPUT_DIR}{notebook_filename}'

    papermill.execute_notebook(
        input_path=input_path,
        output_path=notebook_path,
        parameters=dict(
            access_token=athlete.access_token,
            activity_id=activity_id
        )
    )

    nb = sb.read_notebook(notebook_path)
    start_date_local = nb.scraps['activity_detail'].data['start_date_local']
    dt = datetime.fromisoformat(start_date_local)
    title = nb.scraps['activity_detail'].data['name']

    await Report.objects.create(
        activity_id=activity_id,
        strava_athlete=athlete,
        title=title,
        datetime=dt,
        notebook_filename=notebook_filename,
        html_filename=html_filename)


    with open(notebook_path, 'r') as f:
        notebook = nbformat.reads(f.read(), as_version=4)
    html_exporter = HTMLExporter()
    html_exporter.template_file = 'full'
    body, _ = html_exporter.from_notebook_node(notebook)

    with open(f'{REPORT_OUTPUT_DIR}{html_filename}', 'w') as f:
        f.write(body)
