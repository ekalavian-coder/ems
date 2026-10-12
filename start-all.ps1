# start-all.ps1
# Launches the EMS stack in three terminals: database (docker), backend, frontend.
# Idempotent: safe to re-run. Reuses existing venvs, container, and h2.jar.
#
# Usage (from workspace root):
#   .\start-all.ps1
#
# To stop:
#   .\stop-all.ps1    (or Ctrl-C each window, then: docker rm -f ems-database)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host ""
Write-Host "=== EMS stack launcher ===" -ForegroundColor Cyan
Write-Host "Workspace: $root"
Write-Host ""

# -------- 1. Database container --------
Write-Host "[1/3] Database (H2, docker container ems-database on port 9092)" -ForegroundColor Yellow

$existing = docker ps -a --filter "name=^ems-database$" --format "{{.Status}}"
if ($existing) {
    if ($existing -like "Up*") {
        Write-Host "    already running: $existing"
    } else {
        Write-Host "    container exists but stopped; starting..."
        docker start ems-database | Out-Null
    }
} else {
    Write-Host "    building image..."
    docker build -t ems-database "$root\database-service" | Out-Host
    Write-Host "    starting container..."
    docker run -d --name ems-database -p 127.0.0.1:9092:9092 -v h2_data:/data ems-database | Out-Null
}

# Wait for H2 TCP to accept connections
Write-Host "    waiting for TCP 9092..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect("127.0.0.1", 9092)
        $client.Close()
        $ready = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $ready) {
    Write-Host "    WARNING: port 9092 did not accept connections within 30s; backend may fail to start" -ForegroundColor Red
} else {
    Write-Host "    database ready." -ForegroundColor Green
}

# -------- 2. Backend terminal --------
Write-Host ""
Write-Host "[2/3] Backend (FastAPI on port 8000) - opening new window" -ForegroundColor Yellow

$pyLauncher = (Get-Command py.exe -ErrorAction SilentlyContinue)
$pyCmd = if ($pyLauncher) { 'py' } else { 'python' }

$backendInit = @'
Set-Location "__ROOT__\backend"
if (-not (Test-Path .\.venv\Scripts\Activate.ps1)) {
    Write-Host "Creating venv..."
    __PY__ -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
python -m pip install -q -r requirements.txt
if (-not (Test-Path .\lib\h2.jar)) {
    Write-Host "Downloading H2 JDBC driver..."
    New-Item -ItemType Directory -Force lib | Out-Null
    Invoke-WebRequest -Uri "https://repo.maven.apache.org/maven2/com/h2database/h2/2.3.232/h2-2.3.232.jar" -OutFile ".\lib\h2.jar"
}
$env:H2_JAR_PATH  = (Resolve-Path .\lib\h2.jar).Path
$env:H2_JDBC_URL  = "jdbc:h2:tcp://localhost:9092/./emsdb"
$env:H2_USER      = "sa"
$env:H2_PASSWORD  = ""
$env:CORS_ORIGINS = "http://localhost:4200"
Write-Host "Starting uvicorn..." -ForegroundColor Green
python -m uvicorn app.main:app --reload --port 8000
'@
$backendInit = $backendInit.Replace('__ROOT__', $root).Replace('__PY__', $pyCmd)

Start-Process powershell -ArgumentList '-NoExit', '-ExecutionPolicy', 'Bypass', '-Command', $backendInit

# -------- 3. Frontend terminal --------
Write-Host ""
Write-Host "[3/3] Frontend (Angular on port 4200) - opening new window" -ForegroundColor Yellow

$frontendInit = @'
Set-Location "__ROOT__\frontend"
if (-not (Test-Path .\node_modules)) {
    Write-Host "Installing npm dependencies (first run)..."
    npm install --no-audit --no-fund
}
Write-Host "Starting ng serve..." -ForegroundColor Green
npm start
'@
$frontendInit = $frontendInit.Replace('__ROOT__', $root)

Start-Process powershell -ArgumentList '-NoExit', '-ExecutionPolicy', 'Bypass', '-Command', $frontendInit

# -------- Summary --------
Write-Host ""
Write-Host "=== Launch complete ===" -ForegroundColor Cyan
Write-Host "  Database: docker container ems-database (port 9092, bound to 127.0.0.1)"
Write-Host "  Backend : http://localhost:8000  (new PowerShell window)"
Write-Host "  Frontend: http://localhost:4200  (new PowerShell window)"
Write-Host ""
Write-Host "Verify once both windows show 'ready':"
Write-Host "  curl http://localhost:8000/health"
Write-Host "  start http://localhost:4200"
Write-Host ""
Write-Host "To stop everything, run: .\stop-all.ps1"
Write-Host ""
