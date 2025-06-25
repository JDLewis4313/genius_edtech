#!/bin/bash
echo "📦 Running Django migrations inside Railway..."
python manage.py migrate --noinput

echo "🧼 Collecting static files..."
python manage.py collectstatic --noinput

