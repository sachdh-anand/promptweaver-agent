# setup.ps1 - Full project bootstrapper with uv and CrewAI

$base = "$PSScriptRoot"
cd $base

if (-Not (Test-Path ".venv")) {
    Write-Output "🛠 Creating virtual environment..."
    uv venv
}

Write-Output "📦 Installing dependencies via uv..."
& .\.venv\Scripts\Activate.ps1
uv pip install -r (uv pip compile --generate-hashes pyproject.toml | Out-String)

Write-Output "🚀 Running the agent..."
python main.py
