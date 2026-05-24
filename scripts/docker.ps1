# ============================================================================
# AI Marketing Hub — Docker Helper Script
# Usage: .\scripts\docker.ps1 <command>
#
# Commands:
#   build   — Build tất cả Docker images
#   up      — Chạy production (nginx + FastAPI)
#   dev     — Chạy development (hot-reload)
#   down    — Dừng tất cả containers
#   logs    — Xem logs realtime
#   clean   — Xóa images, volumes, cache
#   status  — Kiểm tra trạng thái containers
#   restart — Restart tất cả services
# ============================================================================

param(
    [Parameter(Position = 0)]
    [ValidateSet("build", "up", "dev", "down", "logs", "clean", "status", "restart")]
    [string]$Command = "status"
)

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path "$ProjectRoot\docker-compose.yml")) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
if (-not (Test-Path "$ProjectRoot\docker-compose.yml")) {
    Write-Host "❌ Không tìm thấy docker-compose.yml" -ForegroundColor Red
    exit 1
}

Set-Location $ProjectRoot

function Test-DockerRunning {
    try {
        docker info 2>$null | Out-Null
        return $true
    } catch {
        Write-Host "❌ Docker chưa chạy. Vui lòng khởi động Docker Desktop." -ForegroundColor Red
        exit 1
    }
}

function Ensure-EnvFile {
    if (-not (Test-Path "backend\.env")) {
        if (Test-Path ".env.example") {
            Write-Host "⚠️  Chưa có backend\.env — tạo từ .env.example..." -ForegroundColor Yellow
            Copy-Item ".env.example" "backend\.env"
            Write-Host "📝 Vui lòng cập nhật backend\.env với API keys thực tế." -ForegroundColor Cyan
        } else {
            Write-Host "❌ Không tìm thấy .env.example hoặc backend\.env" -ForegroundColor Red
            exit 1
        }
    }
}

function Ensure-DbFiles {
    # Ensure .db files exist (Docker bind mounts require existing files)
    $dbFiles = @("sites.db", "rank_tracker.db", "content_calendar.db", "ab_tests.db")
    foreach ($db in $dbFiles) {
        $path = "backend\$db"
        if (-not (Test-Path $path)) {
            New-Item -ItemType File -Path $path -Force | Out-Null
            Write-Host "📄 Tạo $path (trống)" -ForegroundColor Gray
        }
    }
}

# ── Commands ────────────────────────────────────────────────────────────────

switch ($Command) {
    "build" {
        Test-DockerRunning
        Write-Host "🔨 Building Docker images..." -ForegroundColor Cyan
        docker compose build --no-cache
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Build thành công!" -ForegroundColor Green
        } else {
            Write-Host "❌ Build thất bại!" -ForegroundColor Red
        }
    }

    "up" {
        Test-DockerRunning
        Ensure-EnvFile
        Ensure-DbFiles
        Write-Host "🚀 Starting AI Marketing Hub (Production)..." -ForegroundColor Cyan
        Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
        Write-Host "   Frontend: http://localhost:80" -ForegroundColor White
        Write-Host ""
        docker compose up -d
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Đang chạy! Mở http://localhost để truy cập." -ForegroundColor Green
        }
    }

    "dev" {
        Test-DockerRunning
        Ensure-EnvFile
        Ensure-DbFiles
        Write-Host "🔧 Starting AI Marketing Hub (Development)..." -ForegroundColor Cyan
        Write-Host "   Backend:  http://localhost:8000 (hot-reload)" -ForegroundColor White
        Write-Host "   Frontend: http://localhost:5173 (Vite HMR)" -ForegroundColor White
        Write-Host ""
        docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Dev mode đang chạy! Frontend: http://localhost:5173" -ForegroundColor Green
        }
    }

    "down" {
        Test-DockerRunning
        Write-Host "🛑 Stopping all containers..." -ForegroundColor Yellow
        docker compose -f docker-compose.yml -f docker-compose.dev.yml down
        Write-Host "✅ Đã dừng." -ForegroundColor Green
    }

    "logs" {
        Test-DockerRunning
        Write-Host "📋 Logs (Ctrl+C để thoát)..." -ForegroundColor Cyan
        docker compose logs -f --tail=100
    }

    "clean" {
        Test-DockerRunning
        Write-Host "🧹 Cleaning Docker resources..." -ForegroundColor Yellow
        $confirm = Read-Host "⚠️  Xóa tất cả images, containers, volumes? (y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v --rmi all --remove-orphans
            docker system prune -f
            Write-Host "✅ Đã dọn sạch." -ForegroundColor Green
        } else {
            Write-Host "⏹️  Đã hủy." -ForegroundColor Gray
        }
    }

    "status" {
        Test-DockerRunning
        Write-Host "📊 Container Status:" -ForegroundColor Cyan
        Write-Host ""
        docker compose ps -a
        Write-Host ""

        # Check health endpoints
        Write-Host "🏥 Health Checks:" -ForegroundColor Cyan
        try {
            $backend = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop
            Write-Host "   Backend:  ✅ OK (v$($backend.version), Phase $($backend.phase))" -ForegroundColor Green
        } catch {
            Write-Host "   Backend:  ❌ Không phản hồi" -ForegroundColor Red
        }

        try {
            $null = Invoke-WebRequest -Uri "http://localhost:80" -TimeoutSec 3 -ErrorAction Stop
            Write-Host "   Frontend: ✅ OK (port 80)" -ForegroundColor Green
        } catch {
            try {
                $null = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3 -ErrorAction Stop
                Write-Host "   Frontend: ✅ OK (dev, port 5173)" -ForegroundColor Green
            } catch {
                Write-Host "   Frontend: ❌ Không phản hồi" -ForegroundColor Red
            }
        }
    }

    "restart" {
        Test-DockerRunning
        Write-Host "🔄 Restarting..." -ForegroundColor Cyan
        docker compose restart
        Write-Host "✅ Đã restart." -ForegroundColor Green
    }
}
