#!/bin/bash
set -e

echo "در حال انتظار برای دیتابیس PostgreSQL..."
until python manage.py check --database default > /dev/null 2>&1; do
  sleep 1
done
echo "دیتابیس آماده است."

echo "اجرای Migration..."
python manage.py migrate --noinput

echo "جمع‌آوری فایل‌های استاتیک..."
python manage.py collectstatic --noinput

echo "شروع سرور Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
