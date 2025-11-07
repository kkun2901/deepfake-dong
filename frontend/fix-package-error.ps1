# 패키징 오류 해결 스크립트

Write-Host "=== 패키징 오류 해결 ===" -ForegroundColor Green

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`n[1/4] Gradle 빌드 캐시 정리..." -ForegroundColor Cyan
if (Test-Path "android") {
    Set-Location android
    .\gradlew.bat clean --no-daemon 2>&1 | Out-Null
    Set-Location ..
}

Write-Host "`n[2/4] Android 빌드 디렉토리 삭제..." -ForegroundColor Cyan
Remove-Item -Recurse -Force android\.gradle -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force android\app\build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force android\build -ErrorAction SilentlyContinue

Write-Host "`n[3/4] Gradle 데몬 종료..." -ForegroundColor Cyan
if (Test-Path "android") {
    Set-Location android
    .\gradlew.bat --stop 2>&1 | Out-Null
    Set-Location ..
}

Write-Host "`n[4/4] Android 빌드 재시도..." -ForegroundColor Cyan
npm run android

Write-Host "`n✅ 완료!" -ForegroundColor Green




