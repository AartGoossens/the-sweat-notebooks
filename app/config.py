import databases
import sqlalchemy
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

config = Config(".env")

STRAVA_CLIENT_ID = config('STRAVA_CLIENT_ID', cast=int)
STRAVA_CLIENT_SECRET = config('STRAVA_CLIENT_SECRET', cast=Secret)
APP_URL = config('APP_URL')
DATABASE_PATH = config('DATABASE_PATH')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'


database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


NOTEBOOK_TEMPLATES_PATH = config('NOTEBOOK_TEMPLATES_PATH')
NOTEBOOK_TEMPLATE_NAME = config('NOTEBOOK_TEMPLATE_NAME')
REPORT_OUTPUT_DIR = config('REPORT_OUTPUT_DIR')
