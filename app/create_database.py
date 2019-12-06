import sqlalchemy

from .config import database, metadata
from .reports import models as report_models
from .strava import models as strava_models


engine = sqlalchemy.create_engine(str(database.url))
metadata.create_all(engine)
