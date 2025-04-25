#!/usr/bin/env bash
# Script to run the PromptWeaver CrewAI project using uv
set -e

# Move to the script's directory
cd "$(dirname "$0")"

# Check for uv
if ! command -v uv &> /dev/null; then
  echo "❌ 'uv' is not installed. Install it via 'pip install uv'"
  exit 1
fi

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "📦 Creating virtual environment with uv..."
  uv venv .venv --seed
fi

# Install dependencies from pyproject.toml
echo "📚 Installing dependencies..."
uv pip install -e .

# Run the CrewAI main script
echo "🚀 Running PromptWeaver CrewAI..."
PYTHONPATH=src uv run python src/main.py
