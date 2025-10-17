#!/bin/bash

# Build script for Vercel deployment
echo "Starting Vercel build process..."

# Install Node.js dependencies for Tailwind
echo "Installing Node.js dependencies..."
npm install

# Build Tailwind CSS
echo "Building Tailwind CSS..."
npm run build

# Collect static files using uv
echo "Collecting static files..."
uv run manage.py collectstatic --noinput

echo "Build process completed successfully!"