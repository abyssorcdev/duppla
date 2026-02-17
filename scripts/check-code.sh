#!/bin/bash
# Script para verificar código con Ruff antes de commit
# Uso: ./scripts/check-code.sh

set -e  # Exit on error

echo "🔍 Checking code with Ruff..."
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/../backend" || exit 1

echo "📋 Step 1: Running linter..."
ruff check . --config ruff.toml || {
    echo ""
    echo "❌ Linting errors found. Try to fix with:"
    echo "   ruff check --fix . --config ruff.toml"
    exit 1
}

echo "✅ Linting passed"
echo ""

echo "🎨 Step 2: Checking code formatting..."
ruff format --check . --config ruff.toml || {
    echo ""
    echo "❌ Formatting issues found. Fix with:"
    echo "   ruff format . --config ruff.toml"
    exit 1
}

echo "✅ Formatting is correct"
echo ""

echo "✨ All checks passed! Ready to commit."
exit 0
