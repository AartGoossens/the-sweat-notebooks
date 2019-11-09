import sqlalchemy

from .config import database, metadata
from .strava import models


engine = sqlalchemy.create_engine(str(database.url))
metadata.create_all(engine)
