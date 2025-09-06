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

# Set Django settings for build
export DJANGO_SETTINGS_MODULE=config.settings.production
export BUILD_PHASE=true

# Debug: Print environment variables
echo "BUILD_PHASE: $BUILD_PHASE"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# SKIP database migrations during build (will run at startup)
echo "⏭️ Skipping database migrations during build phase..."

# Collect static files (this doesn't need database)
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.production

echo "✅ Build completed successfully!"