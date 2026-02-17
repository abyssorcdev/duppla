#!/bin/bash
# Script para arreglar código automáticamente con Ruff
# Uso: ./scripts/fix-code.sh

set -e

echo "🔧 Fixing code with Ruff..."
echo ""

cd "$(dirname "$0")/../backend" || exit 1

echo "📋 Step 1: Auto-fixing linting errors..."
ruff check --fix . --config ruff.toml
echo "✅ Linting fixes applied"
echo ""

echo "🎨 Step 2: Formatting code..."
ruff format . --config ruff.toml
echo "✅ Code formatted"
echo ""

echo "✅ Step 3: Verifying everything is clean..."
ruff check . --config ruff.toml && ruff format --check . --config ruff.toml
echo ""

echo "✨ Code is clean and ready for commit!"
