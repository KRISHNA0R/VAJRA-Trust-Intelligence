# Clean Test Data Script
# This script removes all test job data while preserving the directory structure

Write-Host "🧹 Cleaning test data..." -ForegroundColor Cyan

# Clean data/jobs directory (keep structure)
$jobsPath = "data\jobs"
if (Test-Path $jobsPath) {
    Write-Host "  Removing job data from $jobsPath..." -ForegroundColor Yellow
    Get-ChildItem -Path $jobsPath -Directory | ForEach-Object {
        Remove-Item -Path $_.FullName -Recurse -Force
        Write-Host "    Removed: $($_.Name)" -ForegroundColor Gray
    }
}

# Clean runs directory (keep structure)
$runsPath = "runs"
if (Test-Path $runsPath) {
    Write-Host "  Removing run data from $runsPath..." -ForegroundColor Yellow
    Get-ChildItem -Path $runsPath -Directory | ForEach-Object {
        Remove-Item -Path $_.FullName -Recurse -Force
        Write-Host "    Removed: $($_.Name)" -ForegroundColor Gray
    }
}

# Remove __pycache__ directories
Write-Host "  Removing Python cache..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory | ForEach-Object {
    Remove-Item -Path $_.FullName -Recurse -Force
    Write-Host "    Removed: $($_.FullName)" -ForegroundColor Gray
}

# Remove .pyc files
Write-Host "  Removing .pyc files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Filter "*.pyc" -File | ForEach-Object {
    Remove-Item -Path $_.FullName -Force
    Write-Host "    Removed: $($_.FullName)" -ForegroundColor Gray
}

Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Note: Model weight files (.pth, .pth.tar) are preserved." -ForegroundColor Cyan
Write-Host "To exclude them from git, they are listed in .gitignore" -ForegroundColor Cyan

