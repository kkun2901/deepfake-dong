# 빠른 로그 확인 (간단 버전)

$adbPath = "C:\Users\a\AppData\Local\Android\Sdk\platform-tools\adb.exe"

if (-not (Test-Path $adbPath)) {
    Write-Host "❌ adb를 찾을 수 없습니다: $adbPath" -ForegroundColor Red
    exit 1
}

Write-Host "=== 위젯 녹화 로그 ===" -ForegroundColor Green
Write-Host "중지: Ctrl+C" -ForegroundColor Yellow
Write-Host ""

& $adbPath logcat -c
& $adbPath logcat FloatingService:* FloatingWidgetModule:* MainActivity:* *:S



