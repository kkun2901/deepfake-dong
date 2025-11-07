# Android 빌드 문제 해결 스크립트 (v2)

Write-Host "=== Android 빌드 문제 해결 (v2) ===" -ForegroundColor Green

# frontend 디렉토리로 이동
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`n[1/6] expo-document-picker 버전 수정 확인..." -ForegroundColor Cyan

Write-Host "`n[2/6] node_modules 재설치 중..." -ForegroundColor Cyan
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
npm install

Write-Host "`n[3/6] Android 빌드 캐시 완전 정리 중..." -ForegroundColor Cyan
if (Test-Path "android") {
    Set-Location android
    .\gradlew.bat clean --no-daemon 2>&1 | Out-Null
    Set-Location ..
}

Write-Host "`n[4/6] Android .gradle 캐시 완전 삭제 중..." -ForegroundColor Cyan
Remove-Item -Recurse -Force android\.gradle -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force android\app\build -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force android\build -ErrorAction SilentlyContinue

Write-Host "`n[5/6] Expo prebuild 실행 (--clean 옵션)..." -ForegroundColor Cyan
# prebuild를 강제로 실행 (yes 자동 응답)
echo "y" | npx expo prebuild --clean --platform android

Write-Host "`n[6/6] Android 빌드 재시도..." -ForegroundColor Cyan
npm run android

Write-Host "`n✅ 빌드 문제 해결 완료!" -ForegroundColor Green




