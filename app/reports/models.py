import orm
import sqlalchemy

from ..config import database, metadata
from ..strava.models import StravaAthlete


class Report(orm.Model):
    __tablename__ = "reports"
    __database__ = database
    __metadata__ = metadata

    activity_id = orm.Integer(primary_key=True)
    strava_athlete = orm.ForeignKey(StravaAthlete)
    title = orm.String(max_length=500)
    datetime = orm.DateTime()
    notebook_filename = orm.String(max_length=200)
    html_filename = orm.String(max_length=200)
