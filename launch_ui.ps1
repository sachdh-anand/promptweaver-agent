# Disable Streamlit's file watching (hot reload) but keep automatic browser opening
$env:STREAMLIT_WATCHER_IGNORE_MODULES="torch,torch._classes,torch.nn,torch.utils,torch._C"
$env:STREAMLIT_SERVER_FILE_WATCHER_TYPE="none"
$env:STREAMLIT_SERVER_ENABLE_STATIC_SERVING="false"
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"

# Install streamlit if needed
uv pip install streamlit

# Display helpful exit information
Write-Host ""
Write-Host "🚀 Starting PromptWeaver Studio..."
Write-Host "📋 To exit the application, press Ctrl+C multiple times, or Ctrl+Break, or close this terminal window"
Write-Host ""

# Run the app
streamlit run src/app.py