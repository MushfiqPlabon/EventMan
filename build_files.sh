#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Building project with Modern Tools (uv & bun)..."

# Ensure uv is available
if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Add uv to PATH for this session
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

# Sync Python dependencies using uv
echo "Syncing Python dependencies..."
uv sync

# Ensure bun is available
if ! command -v bun >/dev/null 2>&1; then
  echo "bun not found. Installing bun..."
  curl -fsSL https://bun.sh/install | bash
  export BUN_INSTALL="$HOME/.bun"
  export PATH="$BUN_INSTALL/bin:$PATH"
fi

# Install Node dependencies using bun
echo "Installing Node dependencies..."
bun install --frozen-lockfile || bun install

# Build Frontend Assets
echo "Building Frontend..."
bun run build

# Collect Static Files
echo "Collecting Static Files..."
uv run manage.py collectstatic --noinput

echo "Build process completed successfully."