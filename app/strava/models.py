import orm
import sqlalchemy

from config import database, metadata


class StravaAthlete(orm.Model):
    __tablename__ = "strava_athletes"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    access_token = orm.String(max_length=100)
    refresh_token = orm.String(max_length=100)
    token_expiration_datetime = orm.DateTime()
    backfilled = orm.Boolean(default=False)

    # @TODO add 'get_access_token' method on model that automatically refreshes token if needed
