FROM python:3.7-buster

RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/pip_cache
RUN mkdir -p /opt/app/hackx
COPY requirements.txt /opt/app/
RUN pip3 install -r /opt/app/requirements.txt --cache-dir /opt/app/pip_cache
COPY . /opt/app/hackx/
WORKDIR /opt/app/hackx/
RUN python3 manage.py collectstatic --no-input
# RUN chown -R www-data:www-data /opt/app

EXPOSE 5000
ENTRYPOINT ["/opt/app/hackx/prodrunserver.sh"]