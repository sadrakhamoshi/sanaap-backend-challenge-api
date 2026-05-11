#!/bin/bash
set -e

echo "🚀 Starting setup..."

# Wait for PostgreSQL if DB_HOST is provided
if [ -n "$DB_HOST" ]; then
    echo "⏳ Waiting for PostgreSQL..."
    while ! nc -z "$DB_HOST" "${DB_PORT:-5432}"; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    echo "✅ PostgreSQL is ready!"
fi

# Run database migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# Collect static files (optional – safe to run even if not needed)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput


# Launch Django with Gunicorn
echo "🌟 Starting Django with Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120