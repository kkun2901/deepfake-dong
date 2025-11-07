# 빠른 빌드 수정 스크립트

Write-Host "=== 빠른 빌드 수정 ===" -ForegroundColor Green

# frontend 디렉토리로 이동
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`n[1/3] Android 빌드 캐시 정리 중..." -ForegroundColor Cyan
if (Test-Path "android") {
    Set-Location android
    .\gradlew.bat clean
    Set-Location ..
}

Write-Host "`n[2/3] Android 빌드 디렉토리 정리 중..." -ForegroundColor Cyan
Remove-Item -Recurse -Force android\.gradle -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force android\app\build -ErrorAction SilentlyContinue

Write-Host "`n[3/3] Android 빌드 재시도..." -ForegroundColor Cyan
npm run android

Write-Host "`n✅ 완료!" -ForegroundColor Green




