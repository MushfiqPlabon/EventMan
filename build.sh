#!/bin/bash

# Build script for Vercel deployment
echo "Starting Vercel build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies for Tailwind
echo "Installing Node.js dependencies..."
npm install

# Build Tailwind CSS
echo "Building Tailwind CSS..."
npm run build

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run Django migrations
echo "Running database migrations..."
python manage.py migrate --noinput

echo "Build process completed successfully!"