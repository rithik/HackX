release: python3 manage.py migrate
web: gunicorn -k uvicorn.workers.UvicornWorker hoohacks.asgi --preload
worker: python manage.py runworker channels -v2