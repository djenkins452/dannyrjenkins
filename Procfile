web: python manage.py migrate --noinput && python manage.py bootstrap_prod && gunicorn resume.wsgi --bind 0.0.0.0:$PORT --log-file -
