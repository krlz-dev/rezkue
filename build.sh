#!/usr/bin/env bash
# Build script for Render deployment
# This installs Python dependencies and Playwright browsers

set -o errexit  # Exit on error

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright browsers..."
playwright install --with-deps chromium

echo "Build completed successfully!"
