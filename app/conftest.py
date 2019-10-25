import pytest
import sqlalchemy
from pathlib import Path

from config import database, metadata, DATABASE_PATH


@pytest.fixture(scope='function', autouse=True)
def db():
    engine = sqlalchemy.create_engine(str(database.url))
    metadata.create_all(engine)
    yield
    Path(DATABASE_PATH).unlink()
