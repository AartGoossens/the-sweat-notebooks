from pathlib import Path

from fastapi import Cookie
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request

from config import REPORT_OUTPUT_DIR, templates
from main import app
from strava.models import StravaAthlete


@app.get('/reports/{athlete_id}/{report_name}')
def retrieve_report(athlete_id, report_name):
    with Path(REPORT_OUTPUT_DIR, athlete_id, report_name).open() as f:
        html = f.read()

    return HTMLResponse(content=html, status_code=200)


@app.get('/reports')
def list_reports(strava_athlete_id: str = Cookie(None)):
    # @TODO add admin login to see all available athletes
    if strava_athlete_id is None:
        return RedirectResponse(f'/login')
    else:
        return RedirectResponse(f'/reports/{strava_athlete_id}')


@app.get('/reports/{athlete_id}')
async def list_reports(request: Request, athlete_id: int = None):
    athlete_dir = Path(REPORT_OUTPUT_DIR, str(athlete_id))
    reports = []
    for f in athlete_dir.iterdir():
        if not f.is_file():
            continue
        if f.name.endswith('.ipynb'):
            continue
        reports.append(f.name)

    athlete = await StravaAthlete.objects.get(id=athlete_id)
    athlete_backfilled = athlete.backfilled

    return templates.TemplateResponse(
        "list_reports.html",
        context=dict(
            request=request,
            athlete_id=athlete_id,
            athlete_backfilled=athlete_backfilled,
            reports=reports
        )
    )
