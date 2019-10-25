import json

import nbformat
import papermill as pm
from nbconvert import HTMLExporter
from strava.models import StravaAthlete


async def handle_new_event(event):
    athlete = await StravaAthlete.objects.get(id=event.owner_id)


    templates_path = '/data/templates/'
    template_name = 'parametrized_notebook'
    output_dir = '/data/output/'


    input_path = f'{templates_path}{template_name}.ipynb'
    output_path = f'{output_dir}{athlete.id}/{event.object_id}-{template_name}.ipynb'

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

    with open(f'{output_dir}{athlete.id}/{event.object_id}-{template_name}.html', 'w') as f:
        f.write(body)
