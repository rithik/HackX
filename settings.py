import secret
import datetime
from pytz import timezone

DATABASE_URL = secret.DATABASE_URL
SECRET_KEY = secret.SECRET_KEY
SQLALCHEMY_TRACK_MODIFICATIONS = secret.SQLALCHEMY_TRACK_MODIFICATIONS
APP_SETTINGS = secret.APP_SETTINGS
ADMIN_USERNAME = secret.ADMIN_USERNAME
ADMIN_PASSWORD = secret.ADMIN_PASSWORD
EVENT_NAME = "HooHacks"

tz = timezone('US/Eastern')
APPLICATION_SUBMISSION_DEADLINE = tz.localize(datetime.datetime(2019, 4, 30, 23, 59, 59, 0))

SCHOOLS = []
GRADUATION_YEARS = [2019, 2020, 2021, 2022, 2023, 2024]
RACES = ["African American", "American Indian", "Asian",
    "Hispanic", "Native Hawaiian", "White", "Other"]
GENDERS = ["Male", "Female", "Other", "Prefer not to say"]
TRAVEL_METHODS = ["Car", "Bus", "Train", "Airplane", "Other"]


f = open("schools.csv", "r")
for school in f:
    SCHOOLS.append(school)
f.close()
