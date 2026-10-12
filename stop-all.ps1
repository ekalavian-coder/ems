# stop-all.ps1
# Stops the EMS database container. Backend and frontend run in their own
# PowerShell windows -- close them (or Ctrl-C) to stop those.

$ErrorActionPreference = 'Continue'

Write-Host ""
Write-Host "=== Stopping EMS stack ===" -ForegroundColor Cyan

# Database container
$exists = docker ps -a --filter "name=^ems-database$" --format "{{.Names}}"
if ($exists) {
    Write-Host "Stopping ems-database container..."
    docker stop ems-database | Out-Null
    docker rm   ems-database | Out-Null
    Write-Host "Database container removed." -ForegroundColor Green
    Write-Host "(Data volume 'h2_data' preserved. 'docker volume rm h2_data' to wipe data.)"
} else {
    Write-Host "No ems-database container found."
}

Write-Host ""
Write-Host "Backend and frontend are not managed from here --" -ForegroundColor Yellow
Write-Host "close their PowerShell windows or Ctrl-C in each."
Write-Host ""
