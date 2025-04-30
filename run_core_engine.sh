#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for uv
if ! command -v uv &> /dev/null; then
  echo "❌ 'uv' is not installed. Run: pip install uv"
  exit 1
fi

# Create venv if not present
if [ ! -d ".venv" ]; then
  echo "📦 Creating virtual environment with uv..."
  uv venv .venv --seed
  echo "📚 Installing dependencies (first time)..."
  uv pip install -e .
else
  echo "🔄 Syncing dependencies with uv..."
  uv sync
fi

# Run the CrewAI project
echo ""
echo "🚀 Running PromptWeaver..."
# Set PYTHONPATH to include both the current directory and src
export PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/src"
uv run python src/main.py
