#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Building project with Modern Tools (uv & bun)..."

# Sync Python dependencies using uv
echo "Syncing Python dependencies..."
uv sync

# Install Node dependencies using bun
echo "Installing Node dependencies..."
bun install

# Build Frontend Assets
echo "Building Frontend..."
bun run build

# Collect Static Files
echo "Collecting Static Files..."
uv run manage.py collectstatic --noinput --clear

echo "Build process completed successfully."