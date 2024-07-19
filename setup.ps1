$currentDirectory = Split-Path -Parent $MyInvocation.MyCommand.Definition

# function to install Python on Windows
function Install-Python {
    Write-Host "Installing Python..."
    $pythonInstallerUrl = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    $installerPath = Join-Path -Path $currentDirectory -ChildPath "python-installer.exe"
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $installerPath
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1"
    Remove-Item -Path $installerPath
}

# function to install Ollama on Windows
function Install-Ollama {
    Write-Host "Installing Ollama..."
    $ollamaInstallerUrl = "https://ollama.com/download/OllamaSetup.exe"
    $installerPath = Join-Path -Path $currentDirectory -ChildPath "ollama-installer.exe"
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $ollamaInstallerUrl -OutFile $installerPath
    Start-Process -FilePath $installerPath -NoNewWindow  # Run without waiting for completion
    Remove-Item -Path $installerPath

    # Check if Ollama is available, retrying up to 30 times every 20 seconds
    $attempts = 30
    for ($i = 1; $i -le $attempts; $i++) {
        Start-Sleep -Seconds 20
        if (Get-Command ollama -ErrorAction SilentlyContinue) {
            Write-Host "Ollama is now installed."
            # Proceed with pulling models
            ollama pull phi3:mini
            ollama pull nomic-embed-text
            return
        } else {
            Write-Host "Ollama not found, retrying... ($i/$attempts)"
        }
    }

    Write-Host "Ollama installation timed out. Please check the installation."
    exit 1
}

# check if Python is installed
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed. Attempting to install Python."
    Install-Python
} else {
    Write-Host "Python is already installed."
}

# check if Ollama is installed
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    $response = Read-Host "Would you like to install Ollama? [Y] Yes [N] No"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Ollama is not installed. Attempting to install Ollama."
        Install-Ollama
    } else {
        Write-Host "Skipping Ollama installation."
    }
} else {
    Write-Host "Ollama is already installed."
}

# check if virtualenv is installed, if not, install it
if (-not (py -m pip show virtualenv)) {
    Write-Host "virtualenv not found, installing..."
    py -m pip install virtualenv
}

# check if venv folder already exists
if (-not (Test-Path -Path ".\venv")) {
    # create a virtual environment
    py -m virtualenv venv
} else {
    Write-Host "Virtual environment 'venv' already exists."
}

# activate the virtual environment
& .\venv\Scripts\Activate.ps1

# install dependencies from requirements.txt
if (Test-Path -Path ".\requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found, please make sure it is in the same directory as this script."
    exit
}


Write-Host "Setup complete. Virtual environment is ready and dependencies are installed."
Write-Host "To activate the virtual environment, run: .\venv\Scripts\Activate.ps1"
Write-Host "To start the application in the future, activate the virtual environment and run: flask run"

flask run
