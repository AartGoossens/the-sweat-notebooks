import pytest
import sqlalchemy
from datetime import datetime, timedelta
from pathlib import Path

import nest_asyncio

from config import database, metadata, DATABASE_PATH
from strava.models import StravaAthlete


# https://github.com/spyder-ide/spyder/issues/7096#issuecomment-449655308
nest_asyncio.apply()


@pytest.mark.asyncio
@pytest.fixture(scope='function', autouse=True)
async def db():
    engine = sqlalchemy.create_engine(str(database.url))
    metadata.create_all(engine)

    
    for i in range(1, 6):
        await StravaAthlete.objects.create(
            id=i,
            access_token='some access token',
            refresh_token='some refresh token',
            token_expiration_datetime=datetime.now() + timedelta(days=10))


    yield
    Path(DATABASE_PATH).unlink()
