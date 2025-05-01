# PowerShell script to run the A2A server and test client
# Usage: .\run_test.ps1

# Configuration
$apiModule = "src.api:app"
$testScript = "src\tests\a2a_test.py"
$port = 8000
$serverHost = "localhost"
$serverWaitTime = 10  # Increased wait time to allow for CrewAI initialization
$venvPath = ".venv"  # Path to virtual environment
$projectFile = "pyproject.toml"  # Project configuration file

# Set environment variables for CrewAI
$env:CREWAI_VERBOSE = "true"  # Enable verbose logging in CrewAI
$env:PYTHONUNBUFFERED = "1"   # Ensure Python output is not buffered

# Required packages (fallback if project file not found)
$requiredPackages = @(
    "fastapi",
    "uvicorn",
    "aiohttp",
    "pydantic",
    "crewai"  # Added CrewAI package
)

# Function to check if a port is in use
function Test-PortInUse {
    param(
        [int]$Port
    )
    
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $connections.Count -gt 0
}

# Function to check if virtual environment exists
function Test-VirtualEnv {
    param(
        [string]$Path
    )
    
    if (Test-Path -Path "$Path\Scripts\activate.ps1") {
        return $true
    }
    return $false
}

# Function to activate virtual environment
function Initialize-VirtualEnv {
    param(
        [string]$Path
    )
    
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & "$Path\Scripts\activate.ps1"
    
    # Check if activation was successful
    if (-not $?) {
        Write-Host "Failed to activate virtual environment." -ForegroundColor Red
        return $false
    }
    
    # Verify python path is within the venv
    $pythonPath = (Get-Command python).Source
    if ($pythonPath -like "*$Path*") {
        Write-Host "Virtual environment activated successfully." -ForegroundColor Green
        return $true
    } else {
        Write-Host "Virtual environment activation check failed." -ForegroundColor Yellow
        Write-Host "Current Python path: $pythonPath" -ForegroundColor Yellow
        return $false
    }
}

# Function to create virtual environment with uv
function New-VirtualEnv {
    param(
        [string]$Path
    )
    
    # Check if uv is installed
    $uvInstalled = $null
    try {
        $uvInstalled = Get-Command uv -ErrorAction SilentlyContinue
    } catch {
        $uvInstalled = $null
    }
    
    if ($uvInstalled) {
        Write-Host "Creating virtual environment with uv at $Path..." -ForegroundColor Cyan
        uv venv $Path
        
        if (-not $?) {
            Write-Host "Failed to create virtual environment with uv." -ForegroundColor Red
            return $false
        }
        
        Write-Host "Virtual environment created successfully with uv." -ForegroundColor Green
        return $true
    } else {
        Write-Host "uv not found. Falling back to standard venv..." -ForegroundColor Yellow
        python -m venv $Path
        
        if (-not $?) {
            Write-Host "Failed to create virtual environment." -ForegroundColor Red
            return $false
        }
        
        Write-Host "Virtual environment created successfully with venv." -ForegroundColor Green
        return $true
    }
}

# Function to check if package is installed
function Test-PackageInstalled {
    param(
        [string]$PackageName
    )
    
    $pipList = pip list 2>$null
    return ($pipList -match $PackageName).Count -gt 0
}

# Function to install dependencies with uv or pip
function Install-Dependencies {
    param(
        [array]$Packages,
        [string]$ProjectFile
    )
    
    $allPackagesInstalled = $true
    
    # Check if uv is installed
    $uvInstalled = $null
    try {
        $uvInstalled = Get-Command uv -ErrorAction SilentlyContinue
    } catch {
        $uvInstalled = $null
    }
    
    # Check if project file exists
    if (Test-Path -Path $ProjectFile) {
        Write-Host "Installing packages from $ProjectFile..." -ForegroundColor Cyan
        
        if ($uvInstalled) {
            # Using uv for dependency management
            uv pip install -e .
            
            if (-not $?) {
                Write-Host "Failed to install packages with uv." -ForegroundColor Red
                $allPackagesInstalled = $false
            } else {
                Write-Host "Packages installed successfully with uv." -ForegroundColor Green
            }
        } else {
            # Fallback to pip
            pip install -e .
            
            if (-not $?) {
                Write-Host "Failed to install packages with pip." -ForegroundColor Red
                $allPackagesInstalled = $false
            } else {
                Write-Host "Packages installed successfully with pip." -ForegroundColor Green
            }
        }
    } else {
        Write-Host "Project file $ProjectFile not found. Installing individual packages..." -ForegroundColor Yellow
        
        # Install individual packages
        foreach ($package in $Packages) {
            if (-not (Test-PackageInstalled -PackageName $package)) {
                Write-Host "Installing $package..." -ForegroundColor Cyan
                
                if ($uvInstalled) {
                    uv pip install $package
                } else {
                    pip install $package
                }
                
                if (-not $?) {
                    Write-Host "Failed to install $package." -ForegroundColor Red
                    $allPackagesInstalled = $false
                } else {
                    Write-Host "$package installed successfully." -ForegroundColor Green
                }
            } else {
                Write-Host "$package is already installed." -ForegroundColor Green
            }
        }
    }
    
    return $allPackagesInstalled
}

# Check for uv and pip
$uvInstalled = $null
try {
    $uvInstalled = Get-Command uv -ErrorAction SilentlyContinue
} catch {
    $uvInstalled = $null
}

if ($uvInstalled) {
    Write-Host "uv package manager detected." -ForegroundColor Green
} else {
    Write-Host "uv package manager not found. Will use pip if needed." -ForegroundColor Yellow
}

# Check and setup virtual environment
if (-not (Test-VirtualEnv -Path $venvPath)) {
    Write-Host "Virtual environment not found." -ForegroundColor Yellow
    $createVenv = Read-Host "Do you want to create a virtual environment? (Y/N)"
    
    if ($createVenv -eq "Y" -or $createVenv -eq "y") {
        if (-not (New-VirtualEnv -Path $venvPath)) {
            Write-Host "Exiting script due to virtual environment creation failure." -ForegroundColor Red
            exit
        }
    } else {
        Write-Host "Continuing without virtual environment..." -ForegroundColor Yellow
    }
}

# Activate virtual environment if it exists
if (Test-VirtualEnv -Path $venvPath) {
    if (-not (Initialize-VirtualEnv -Path $venvPath)) {
        Write-Host "Continuing without activating virtual environment..." -ForegroundColor Yellow
    }
}

# Check and install required packages
Write-Host "Checking dependencies..." -ForegroundColor Cyan
if (-not (Install-Dependencies -Packages $requiredPackages -ProjectFile $projectFile)) {
    Write-Host "Warning: Some packages might be missing. Proceeding anyway..." -ForegroundColor Yellow
    $continue = Read-Host "Do you want to continue? (Y/N)"
    
    if (-not ($continue -eq "Y" -or $continue -eq "y")) {
        Write-Host "Exiting script." -ForegroundColor Red
        exit
    }
}

# Ensure .well-known directory exists and contains agent.json
if (-not (Test-Path -Path ".well-known")) {
    Write-Host "Creating .well-known directory..." -ForegroundColor Cyan
    New-Item -Path ".well-known" -ItemType Directory | Out-Null
}

# Check for agent.json and create it if missing
if (-not (Test-Path -Path ".well-known/agent.json")) {
    Write-Host "Creating agent.json in .well-known directory..." -ForegroundColor Cyan
    
    # If the agent.json exists in the project root, copy it
    if (Test-Path -Path "agent.json") {
        Copy-Item -Path "agent.json" -Destination ".well-known/agent.json"
        Write-Host "Copied agent.json to .well-known directory." -ForegroundColor Green
    } else {
        Write-Host "Warning: agent.json not found. The test may fail without it." -ForegroundColor Yellow
    }
}

# Check if the port is already in use
if (Test-PortInUse -Port $port) {
    Write-Host "Port $port is already in use. Another instance of the server might be running." -ForegroundColor Yellow
    
    $response = Read-Host "Do you want to clear the port and restart the server? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host "Attempting to clear port $port..." -ForegroundColor Cyan
        
        # Find and kill the process using the port
        $processInfo = netstat -ano | findstr :$port
        if ($processInfo) {
            # Extract PID from the netstat output (last column)
            $pid = ($processInfo -split '\s+')[-1]
            Write-Host "Found process using port $port with PID: $pid" -ForegroundColor Cyan
            
            try {
                Stop-Process -Id $pid -Force -ErrorAction Stop
                Write-Host "Successfully terminated process with PID: $pid" -ForegroundColor Green
                Start-Sleep -Seconds 2  # Give system time to release the port
            } catch {
                Write-Host "Failed to terminate process. Error: $_" -ForegroundColor Red
                Write-Host "You may need to manually end the process or use a different port." -ForegroundColor Yellow
                
                $continueAnyway = Read-Host "Do you want to proceed with testing only? (Y/N)"
                if ($continueAnyway -eq "Y" -or $continueAnyway -eq "y") {
                    Write-Host "Proceeding with test only..." -ForegroundColor Cyan
                    
                    if ($uvInstalled) {
                        uv run $testScript
                    } else {
                        python $testScript
                    }
                    exit
                } else {
                    Write-Host "Exiting script." -ForegroundColor Red
                    exit
                }
            }
        } else {
            Write-Host "Could not identify the process using port $port." -ForegroundColor Yellow
        }
    } else {
        $testOnly = Read-Host "Do you want to proceed with testing only? (Y/N)"
        if ($testOnly -eq "Y" -or $testOnly -eq "y") {
            Write-Host "Proceeding with test only..." -ForegroundColor Cyan
            
            if ($uvInstalled) {
                uv run $testScript
            } else {
                python $testScript
            }
            exit
        } else {
            Write-Host "Exiting script." -ForegroundColor Red
            exit
        }
    }
}

# Update the script to use the existing logger and ensure CrewAI logs are displayed
# Redirect logs to the logs/ directory
$logFilePath = "logs/server.log"

# Ensure the logs directory exists
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Start the server and redirect logs to the centralized logger
Write-Host "Starting the A2A API server on localhost:8000..."
Start-Process -FilePath "python" -ArgumentList "-u src/api.py > $logFilePath 2>&1" -NoNewWindow -PassThru | Out-Null

# Wait for the server to initialize
Write-Host "Waiting 10 seconds for the server to initialize..."
Start-Sleep -Seconds 10

# Check if the server is running
$serverRunning = $false
for ($i = 0; $i -lt 3; $i++) {
    try {
        Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing | Out-Null
        $serverRunning = $true
        break
    } catch {
        Write-Host "Server port not responding yet. Retrying in 3 seconds... (Attempt $($i + 1) of 3)"
        Start-Sleep -Seconds 3
    }
}

if (-not $serverRunning) {
    Write-Host "Server port is open but docs endpoint not responding. Proceeding anyway..."
}

Write-Host "Try manually accessing: http://localhost:8000/docs"
Write-Host "Or the OpenAPI JSON: http://localhost:8000/openapi.json"

# Monitor the log file in real-time
Write-Host "Started log monitoring in background. Server logs will be displayed during test."
Get-Content -Path $logFilePath -Wait -Tail 10 | ForEach-Object { Write-Host $_ }

# Run the A2A test client
Write-Host "Running A2A test client..."
Start-Process -FilePath "python" -ArgumentList "src/tests/a2a_test.py" -NoNewWindow -Wait

# Stop the server
Write-Host "Stopping server..."
Stop-Process -Name "python" -Force
Write-Host "Server stopped successfully."

# Display final log entries
Write-Host "Final server log entries:"
Get-Content -Path $logFilePath -Tail 20 | ForEach-Object { Write-Host $_ }

Write-Host "`nScript execution completed!" -ForegroundColor Green