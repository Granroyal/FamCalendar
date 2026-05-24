import os

from FamCalender import constants as shared_constants

API_BASE_URL = os.environ.get("FAMCALENDAR_API_URL", "http://localhost:8000")
CATEGORIES = shared_constants.CATEGORIES
MONTHS_DA = shared_constants.MONTHS_DA
WEEKDAYS_DA = shared_constants.WEEKDAYS_DA
YEAR = shared_constants.YEAR
