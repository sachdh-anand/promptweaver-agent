#!/usr/bin/env pwsh
# Script to run the PromptWeaver CrewAI project using uv
$ErrorActionPreference = 'Stop'

# Move to script's directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $scriptDir

# Check if uv is installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "❌ 'uv' is not installed. Install it via 'pip install uv'"
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path '.venv')) {
    Write-Host "📦 Creating virtual environment with uv..."
    uv venv .venv --seed
}

# Install dependencies from pyproject.toml
Write-Host "📚 Installing dependencies..."
uv pip install -e .

# Run the project
Write-Host "🚀 Running PromptWeaver CrewAI..."
$env:PYTHONPATH = "src"
uv run python src/main.py

# Restore previous location
Pop-Location
