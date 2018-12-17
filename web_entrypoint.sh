#!/bin/sh
sleep 5
python manage.py migrate --noinput
exec "$@"
