#!/usr/bin/bash
set -e

python manage.py makemigrations

python manage.py migrate 

python manage.py collectstatic

python manage.py import_csv ./data/ingredients.csv

cp -r /app/collected_static/. /backend_static/static/

exec "$@"