import databases
import sqlalchemy
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret
from starlette.templating import Jinja2Templates

config = Config(".env")

STRAVA_CLIENT_ID = config('STRAVA_CLIENT_ID', cast=int)
STRAVA_CLIENT_SECRET = config('STRAVA_CLIENT_SECRET', cast=Secret)
APP_URL = config('APP_URL')
DATABASE_PATH = config('DATABASE_PATH', default='/data/db.sqlite')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'


database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


NOTEBOOK_TEMPLATES_PATH = config('NOTEBOOK_TEMPLATES_PATH', default='/app/notebook_templates/')
NOTEBOOK_TEMPLATE_NAME = config('NOTEBOOK_TEMPLATE_NAME', default='parametrized_notebook')
REPORT_OUTPUT_DIR = config('REPORT_OUTPUT_DIR', default='/data/reports/')


templates = Jinja2Templates(directory="/app/html_templates")


STRAVA_BACKFILL_COUNT = config('STRAVA_BACKFILL_COUNT', cast=int, default=10)


JWT_SECRET = config('JWT_SECRET', cast=Secret)


ADMIN_IDS = config('ADMIN_IDS', cast=CommaSeparatedStrings)
