from pathlib import Path

from fastapi import Depends
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request

from .models import Report
from ..auth import jwt_cookie_authentication
from ..config import REPORT_OUTPUT_DIR, templates
from ..main import app
from ..strava.models import StravaAthlete


@app.get('/reports/{athlete_id}/{html_filename}')
def retrieve_report(athlete_id, html_filename):
    with Path(REPORT_OUTPUT_DIR, html_filename).open() as f:
        html = f.read()

    return HTMLResponse(content=html, status_code=200)


@app.get('/reports')
def reports_root(auth: dict = Depends(jwt_cookie_authentication)):
    # @TODO add admin login to see all available athletes
    if not auth['is_authenticated']:
        return RedirectResponse(f'/login')
    elif not auth.get('is_admin', False):
        strava_athlete_id = auth['sub']
        return RedirectResponse(f'/reports/{strava_athlete_id}')
    else:
        # @TODO return list of athletes
        strava_athlete_id = auth['sub']
        return RedirectResponse(f'/reports/{strava_athlete_id}')


@app.get('/reports/{athlete_id}')
async def list_reports(request: Request, athlete_id: int = None):
    reports = await Report.objects.filter(strava_athlete=athlete_id).all()
    reports.sort(key=lambda x: x.datetime, reverse=True)

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
