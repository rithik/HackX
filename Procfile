release: python3 manage.py migrate
web: bin/start-pgbouncer-stunnel daphne hoohacks.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker channels -v2