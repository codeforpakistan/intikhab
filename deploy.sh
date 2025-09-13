#!/bin/bash

# Deployment script for Intikhab on DigitalOcean App Platform
# This script runs automatically during deployment

set -e  # Exit on any error

echo "🚀 Starting Intikhab deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
echo "🗃️ Running database migrations..."
python manage.py migrate --noinput

# Create superuser if environment variables are set
if [ ! -z "$DJANGO_SUPERUSER_USERNAME" ] && [ ! -z "$DJANGO_SUPERUSER_EMAIL" ] && [ ! -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" || echo "Superuser already exists or creation failed"
fi

# Seed database with initial data
echo "🌱 Seeding database with initial data..."
python manage.py seed || echo "Seeding completed or already done"

# Create Citizens group
echo "👥 Creating Citizens group..."
python manage.py create_citizens_group || echo "Citizens group already exists"

echo "✅ Deployment completed successfully!"
echo "🗳️ Intikhab is ready for secure electronic voting!"