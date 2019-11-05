from dataclasses import dataclass
from pathlib import Path

import pytest

import config
import tasks
from strava.schemas import Event


@pytest.mark.asyncio
async def test_handle_new_event(mocker):
    @dataclass
    class StravaAPIResponse:
        data: dict

        def to_dict(self):
            return self.data

    mocked_get_athlete = mocker.patch('stravalib.Client.get_athlete')
    mocked_get_athlete.return_value = StravaAPIResponse({})
    mocked_get_activity = mocker.patch('stravalib.Client.get_activity')
    mocked_get_activity.return_value = StravaAPIResponse({})
    mocked_get_activity_streams = mocker.patch('stravalib.Client.get_activity_streams')
    mocked_get_activity_streams.return_value = StravaAPIResponse({})

    event = Event(
        aspect_type='update',
        event_time=1516126040,
        object_id=1360128428,
        object_type='activity',
        owner_id=2,
        subscription_id=120475,
        updates=dict(title='Messy')
    )

    await tasks.handle_new_event(event)

    mocked_get_athlete.assert_called_once()
    mocked_get_activity.assert_called_once_with(1360128428)
    mocked_get_activity_streams.assert_called_once_with(
        activity_id=1360128428,
        types=tasks.STRAVA_STREAM_TYPES,
        series_type='time'
    )

    assert Path(config.REPORT_OUTPUT_DIR, '2', '1360128428-parametrized_notebook.html').exists()
