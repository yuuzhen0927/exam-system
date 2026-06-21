param(
    [switch]$NoTunnel,
    [switch]$NoBuild,
    [int]$Port = 8003
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "F:\CodexWorkspace\Project004_考试系统"
$FrontendDir = Join-Path $ProjectRoot "src\frontend"
$BackendDir = Join-Path $ProjectRoot "src\backend"
$DistDir = Join-Path $FrontendDir "dist"
$Python = "C:\Users\90997\AppData\Local\Programs\Python\Python312\python.exe"
$CfExe = "C:\Users\90997\cf2.exe"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Exam System - One-Click Deploy" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (-not $NoBuild) {
    Write-Host "[1/4] Building frontend..." -ForegroundColor Yellow
    Push-Location $FrontendDir
    try {
        & cmd /c "npm run build" 2>&1 | ForEach-Object { Write-Host "  $_" }
        if ($LASTEXITCODE -ne 0) { Write-Host "  Build had warnings (exit code $LASTEXITCODE), checking dist..." -ForegroundColor DarkYellow }
        Write-Host "  Build OK" -ForegroundColor Green
    } finally { Pop-Location }
} else {
    Write-Host "[1/4] Skipping build" -ForegroundColor DarkGray
}

if (-not (Test-Path $DistDir)) {
    Write-Host "  ERROR: dist/ not found" -ForegroundColor Red
    exit 1
}

Write-Host "[2/4] Stopping existing services..." -ForegroundColor Yellow
$existing = netstat -ano | Select-String ":$Port" | Select-String "LISTENING"
if ($existing) {
    $pids = $existing | ForEach-Object { ($_ -split '\s+')[-1] } | Sort-Object -Unique
    foreach ($p in $pids) {
        if ($p -and $p -ne $PID) {
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
            Write-Host "  Stopped PID $p"
        }
    }
    Start-Sleep -Seconds 2
}
Get-Process cf2 -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "[3/4] Starting backend on port $Port..." -ForegroundColor Yellow

$deployPy = Join-Path $BackendDir "_deploy_main.py"
Start-Process -FilePath $Python -ArgumentList "`"$deployPy`"" -WorkingDirectory $BackendDir -WindowStyle Hidden
Start-Sleep -Seconds 3

$backendUp = netstat -ano | Select-String ":$Port" | Select-String "LISTENING"
if ($backendUp) {
    Write-Host "  Backend OK: http://localhost:$Port" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Backend failed" -ForegroundColor Red
    exit 1
}

$tunnelUrl = ""
if (-not $NoTunnel -and (Test-Path $CfExe)) {
    Write-Host "[4/4] Starting Cloudflare tunnel..." -ForegroundColor Yellow
    $env:HTTPS_PROXY = "socks5://127.0.0.1:7890"
    Start-Process -FilePath $CfExe -ArgumentList "tunnel --url http://localhost:$Port" -RedirectStandardOutput "$env:TEMP\cf_out.txt" -RedirectStandardError "$env:TEMP\cf_err.txt" -WindowStyle Hidden
    Start-Sleep -Seconds 8

    for ($i = 0; $i -lt 6; $i++) {
        $all = ""
        if (Test-Path "$env:TEMP\cf_err.txt") { $all += Get-Content "$env:TEMP\cf_err.txt" -Raw }
        if (Test-Path "$env:TEMP\cf_out.txt") { $all += Get-Content "$env:TEMP\cf_out.txt" -Raw }
        if ($all -match "(https://[a-z0-9-]+\.trycloudflare\.com)") {
            $tunnelUrl = $Matches[1]
            break
        }
        Start-Sleep -Seconds 3
    }
    if ($tunnelUrl) {
        Write-Host "  Tunnel OK: $tunnelUrl" -ForegroundColor Green
    } else {
        Write-Host "  Tunnel started, URL pending..." -ForegroundColor DarkYellow
    }
} elseif ($NoTunnel) {
    Write-Host "[4/4] Skipping tunnel" -ForegroundColor DarkGray
} else {
    Write-Host "[4/4] cf2.exe not found" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Deploy Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Local:  http://localhost:$Port" -ForegroundColor White
if ($tunnelUrl) {
    Write-Host "  Public: $tunnelUrl" -ForegroundColor White
}
Write-Host ""
Write-Host "  Admin:  admin / admin123" -ForegroundColor DarkGray
Write-Host "  Stop:   Get-Process python* | Stop-Process" -ForegroundColor DarkGray
Write-Host ""
