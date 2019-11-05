import pytest
import sqlalchemy
from datetime import datetime, timedelta
from pathlib import Path

import nest_asyncio

import config
from strava.models import StravaAthlete


# https://github.com/spyder-ide/spyder/issues/7096#issuecomment-449655308
nest_asyncio.apply()


@pytest.mark.asyncio
@pytest.fixture(scope='function', autouse=True)
async def db():
    engine = sqlalchemy.create_engine(str(config.database.url))
    config.metadata.create_all(engine)

    
    for i in range(1, 6):
        await StravaAthlete.objects.create(
            id=i,
            access_token='some access token',
            refresh_token='some refresh token',
            token_expiration_datetime=datetime.now() + timedelta(days=10))


    yield
    Path(config.DATABASE_PATH).unlink()


@pytest.fixture(scope='function')
def tmp_output_dir(tmpdir):
    old_report_output_dir = config.REPORT_OUTPUT_DIR
    config.REPORT_OUTPUT_DIR = tmpdir

    yield Path(tmpdir.dirpath())

    config.REPORT_OUTPUT_DIR = old_report_output_dir
