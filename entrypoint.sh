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


echo "✨ Done setting up djagno project..."
exec "$@"