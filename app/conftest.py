import pytest
import sqlalchemy
from pathlib import Path

import nest_asyncio

from config import database, metadata, DATABASE_PATH


# https://github.com/spyder-ide/spyder/issues/7096#issuecomment-449655308
nest_asyncio.apply()


@pytest.fixture(scope='function', autouse=True)
def db():
    engine = sqlalchemy.create_engine(str(database.url))
    metadata.create_all(engine)
    yield
    Path(DATABASE_PATH).unlink()
