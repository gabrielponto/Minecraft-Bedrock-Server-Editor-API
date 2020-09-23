#!/bin/bash
# on every init create a superuser on database if not exists
script="
from django.contrib.auth.models import User;
import os

username = os.environ.get('DEFAULT_ADMIN_USERNAME', 'admin')
password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'bedrockeditor')
email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@localhost')

if User.objects.filter(email=email).count()==0:
    User.objects.create_superuser(username=username, email=email, password=password, first_name='Admin')
    print('Superuser created.')
else:
    print('Superuser creation skipped.')
"

# first wait for postgres to listening
set -e

until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT"; do
    >&2 echo "Postgres is unavailable. Sleeping..."
    sleep 1
done

>&2 echo "Postgres is up. Starting..."

cd /ofertas && \
    .venv/bin/python manage.py migrate && \
    .venv/bin/python manage.py collectstatic --noinput && \
    .venv/bin/python manage.py cities_light && \
    echo "$script" | .venv/bin/python manage.py shell
    
supervisord -c /etc/supervisor/supervisord.conf