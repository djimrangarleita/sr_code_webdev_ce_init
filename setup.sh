#!/usr/bin/env bash
# This script will install dependencies in eval and client app

cd /app

# Install frontend dependencies (clean install)
echo "Installing frontend dependencies..."
npm ci

# Move to eval directory
cd /app/eval

# Install eval dependencies (clean install)
echo "Installing eval dependencies..."
npm ci
