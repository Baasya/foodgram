#!/usr/bin/bash

python manage.py migrate 

python manage.py collectstatic

python manage.py import_csv ./data/ingredients.csv

cp -r /app/collected_static/. /backend_static/static/
