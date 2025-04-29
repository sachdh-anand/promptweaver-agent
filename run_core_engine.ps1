#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $scriptDir

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "❌ 'uv' is not installed. Install it via 'pip install uv'"
    exit 1
}

if (-not (Test-Path '.venv')) {
    Write-Host "📦 Creating virtual environment with uv..."
    uv venv .venv --seed
    Write-Host "📚 Installing dependencies (first time)..."
    uv pip install -e .
} else {
    Write-Host "🔄 Syncing dependencies with uv..."
    uv sync
}

Write-Host ""
Write-Host "🚀 Running PromptWeaver..."
$env:PYTHONPATH = "src"
uv run python src/main.py

Pop-Location
