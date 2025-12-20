#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Building project with Modern Tools (uv & bun)..."

# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# install bun
curl -fsSL https://bun.sh/install | bash
export PATH="$HOME/.bun/bin:$PATH"

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

# Run Migrations (Optional: typically done in release phase, but kept for simplicity)
echo "Running Migrations..."
uv run manage.py migrate --noinput
