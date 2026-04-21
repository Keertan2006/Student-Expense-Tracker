#!/bin/sh
set -e

pip install -r requirements.txt
python manage.py collectstatic --noinput
# Ensure the static directory exists for Vercel to serve
mkdir -p staticfiles_build/static
python manage.py migrate --noinput
