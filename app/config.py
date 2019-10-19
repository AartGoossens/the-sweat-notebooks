from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

config = Config(".env")

STRAVA_CLIENT_ID = config('STRAVA_CLIENT_ID', cast=int)
STRAVA_CLIENT_SECRET = config('STRAVA_CLIENT_SECRET', cast=Secret)
