#!/bin/bash

# Build script for Render deployment
echo "Starting Render build process..."

# Install Node.js dependencies for Tailwind
echo "Installing Node.js dependencies..."
npm install

# Build Tailwind CSS
echo "Building Tailwind CSS..."
npm run build

echo "Build process completed successfully!"
