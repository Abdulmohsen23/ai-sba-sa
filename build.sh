#!/bin/bash

echo "🚀 Starting build process..."

# Exit on error
set -e

# Update pip
echo "📦 Updating pip..."
pip install --upgrade pip

# Install requirements with increased timeout
echo "📋 Installing Python packages..."
pip install --timeout=1000 --no-cache-dir -r requirements.txt

# Run database migrations (if needed)
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!"