import secret
import datetime
from pytz import timezone

DATABASE_URL = secret.DATABASE_URL
SECRET_KEY = secret.SECRET_KEY
SQLALCHEMY_TRACK_MODIFICATIONS = secret.SQLALCHEMY_TRACK_MODIFICATIONS
APP_SETTINGS = secret.APP_SETTINGS
ADMIN_PASSWORD = secret.ADMIN_PASSWORD
GMAIL_USERNAME = secret.GMAIL_USERNAME
GMAIL_PASSWORD = secret.GMAIL_PASSWORD
EVENT_NAME = "HooHacks"

tz = timezone('US/Eastern')
APPLICATION_SUBMISSION_DEADLINE = tz.localize(datetime.datetime(2019, 4, 30, 23, 59, 59, 0))
APPLICATION_SUBMISSION_DEADLINE_FMT = APPLICATION_SUBMISSION_DEADLINE.strftime("%B %d, %Y %I:%M:%S %Z")

APPLICATION_CONFIRMATION_DEADLINE = tz.localize(datetime.datetime(2019, 5, 10, 23, 59, 59, 0))
APPLICATION_CONFIRMATION_DEADLINE_FMT = APPLICATION_CONFIRMATION_DEADLINE.strftime("%B %d, %Y %I:%M:%S %Z")

SCHOOLS = []
GRADUATION_YEARS = [2019, 2020, 2021, 2022, 2023, 2024]
RACES = ["African American", "American Indian", "Asian",
    "Hispanic", "Native Hawaiian", "White", "Other"]
GENDERS = ["Male", "Female", "Other", "Prefer not to say"]
TRAVEL_METHODS = ["Car", "Bus", "Train", "Airplane", "Other"]
TSHIRT_SIZES = ["XS", "S", "M", "L", "XL"]
DIETARY_RESTRICTIONS = ["None", "Vegetarian", "Vegan", "Nut Allergy", "Halal", "Other"]
CITIES = ["Pittsburgh", "Washington, DC", "Richmond", "NYC"] # Test Cities

f = open("schools.csv", "r")
for school in f:
    SCHOOLS.append(school.strip())
f.close()

f = open("emails/verify_email.html", "r")
VERIFY_EMAIL = f.read()
f.close()

f = open("emails/accepted.html", "r")
ACCEPTED_EMAIL = f.read()
f.close()

f = open("emails/waitlisted.html", "r")
WAITLISTED_EMAIL = f.read()
f.close()

f = open("emails/rejected.html", "r")
REJECTED_EMAIL = f.read()
f.close()

f = open("emails/confirmed.html", "r")
CONFIRMED_EMAIL = f.read()
f.close()
