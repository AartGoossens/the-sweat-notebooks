from dataclasses import dataclass
from pathlib import Path

import pytest

import config
from strava import tasks
from strava.models import StravaAthlete
from strava.schemas import Event


@pytest.mark.asyncio
async def test_handle_event(mocker):

    mocked_generate_report = mocker.patch('strava.tasks.generate_report')

    event = Event(
        aspect_type='update',
        event_time=1516126040,
        object_id=1360128428,
        object_type='activity',
        owner_id=2,
        subscription_id=120475,
        updates=dict(title='Messy')
    )

    await tasks.handle_event(event)

    athlete = await StravaAthlete.objects.get(id=event.owner_id)

    mocked_generate_report.assert_called_once_with(athlete, event.object_id)


@pytest.mark.asyncio
async def test_handle_event_athlete(mocker):

    mocked_generate_report = mocker.patch('strava.tasks.generate_report')

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
