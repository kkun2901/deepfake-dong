# Android 빌드 문제 해결 스크립트

Write-Host "=== Android 빌드 문제 해결 ===" -ForegroundColor Green

# frontend 디렉토리로 이동
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`n[1/5] node_modules 재설치 중..." -ForegroundColor Cyan
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
npm install

Write-Host "`n[2/5] Android 빌드 캐시 정리 중..." -ForegroundColor Cyan
if (Test-Path "android") {
    Set-Location android
    .\gradlew.bat clean
    Set-Location ..
}

Write-Host "`n[3/5] Android .gradle 캐시 정리 중..." -ForegroundColor Cyan
Remove-Item -Recurse -Force android\.gradle -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force android\app\build -ErrorAction SilentlyContinue

Write-Host "`n[4/5] Expo prebuild 실행 중..." -ForegroundColor Cyan
npx expo prebuild --clean

Write-Host "`n[5/5] Android 빌드 재시도..." -ForegroundColor Cyan
npm run android

Write-Host "`n✅ 빌드 문제 해결 완료!" -ForegroundColor Green




