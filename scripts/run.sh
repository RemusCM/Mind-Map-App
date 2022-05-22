#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput # may fail as we don't have static
python manage.py migrate


uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi

