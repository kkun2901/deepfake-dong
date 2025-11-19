# 백엔드와 프론트엔드 키 확인 스크립트

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "백엔드 설정 확인" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 백엔드 설정 파일 확인
$backendConfig = "deepfake-detector-app-main\backend\app\core\config.py"
if (Test-Path $backendConfig) {
    Write-Host "[백엔드] 설정 파일: $backendConfig" -ForegroundColor Green
    Write-Host ""
    Get-Content $backendConfig | Select-String -Pattern "WEIGHTS|FRAME|IMAGE_SIZE|ENSEMBLE|THREADS" | ForEach-Object {
        Write-Host "  $_" -ForegroundColor White
    }
} else {
    Write-Host "[백엔드] 설정 파일을 찾을 수 없습니다: $backendConfig" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "프론트엔드 API URL 확인" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 프론트엔드 API URL 확인
$frontendFiles = @(
    "deepfake-detector-app-main\frontend\src\api\index.ts",
    "deepfake-detector-app-main\frontend\src\utils\checkServer.ts",
    "deepfake-detector-app-main\frontend\src\api\community.ts",
    "deepfake-detector-app-main\frontend\android\app\src\main\java\com\anonymous\deepfakeapp\FloatingService.kt"
)

foreach ($file in $frontendFiles) {
    if (Test-Path $file) {
        Write-Host "[프론트엔드] 파일: $file" -ForegroundColor Green
        $content = Get-Content $file -Raw
        $matches = [regex]::Matches($content, "http[s]?://[^\s'`"]+")
        if ($matches.Count -gt 0) {
            $matches | ForEach-Object {
                Write-Host "  API URL: $($_.Value)" -ForegroundColor White
            }
        } else {
            Write-Host "  API URL을 찾을 수 없습니다" -ForegroundColor Yellow
        }
        Write-Host ""
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "백엔드 서버 포트 확인" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendServer = "deepfake-detector-app-main\backend\run_server.bat"
if (Test-Path $backendServer) {
    Write-Host "[백엔드] 서버 실행 파일: $backendServer" -ForegroundColor Green
    $port = Get-Content $backendServer | Select-String -Pattern "--port\s+(\d+)" | ForEach-Object {
        if ($_.Line -match "--port\s+(\d+)") {
            $matches[1]
        }
    }
    if ($port) {
        Write-Host "  포트: $port" -ForegroundColor White
    } else {
        Write-Host "  포트: 8000 (기본값)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "완료" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan







