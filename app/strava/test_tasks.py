from dataclasses import dataclass
from pathlib import Path

import asynctest
import pytest

from .. import config
from . import tasks
from .models import StravaAthlete
from .schemas import Event


@pytest.mark.asyncio
async def test_handle_event(mocker):
    event = Event(
        aspect_type='update',
        event_time=1516126040,
        object_id=1360128428,
        object_type='activity',
        owner_id=2,
        subscription_id=120475,
        updates=dict(title='Messy')
    )

    with asynctest.patch('app.strava.tasks.generate_report') as mocked_generate_report:
        await tasks.handle_event(event)

    athlete = await StravaAthlete.objects.get(id=event.owner_id)

    mocked_generate_report.assert_called_once_with(athlete, event.object_id)


@pytest.mark.asyncio
async def test_handle_event_athlete(mocker):

    mocked_generate_report = mocker.patch('app.strava.tasks.generate_report')

    event = Event(
        aspect_type='update',
        event_time=1516126040,
        object_id=1360128428,
        object_type='athlete',
        owner_id=2,
        subscription_id=120475,
        updates=dict(title='Messy')
    )

    await tasks.handle_event(event)

    mocked_generate_report.assert_not_called()


@pytest.mark.asyncio
async def test_new_athlete(mocker):
    mocked_get_activities = mocker.patch('stravalib.Client.get_activities')

    @dataclass
    class StravaActivity:
        id: int

    mocked_get_activities.return_value = [StravaActivity(1337)]

    strava_athlete = await StravaAthlete.objects.get(id=1)
    assert strava_athlete.backfilled == False

    with asynctest.patch('app.strava.tasks.generate_report') as mocked_generate_report:
        await tasks.new_athlete(strava_athlete)

    mocked_get_activities.assert_called_once_with(limit=config.STRAVA_BACKFILL_COUNT)
    mocked_generate_report.assert_called_once_with(strava_athlete, 1337)

    strava_athlete = await StravaAthlete.objects.get(id=1)
    assert strava_athlete.backfilled == True
