# 최종 빌드 준비 스크립트

Write-Host "=== 최종 빌드 준비 ===" -ForegroundColor Green

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`n[1/3] Android 빌드 캐시 정리 중..." -ForegroundColor Cyan
if (Test-Path "android") {
    Remove-Item -Recurse -Force android\.gradle -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force android\app\build -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force android\build -ErrorAction SilentlyContinue
    Write-Host "✅ Android 빌드 캐시 정리 완료" -ForegroundColor Green
} else {
    Write-Host "⚠️  android 디렉토리가 없습니다. prebuild를 실행하면 생성됩니다." -ForegroundColor Yellow
}

Write-Host "`n[2/3] Expo prebuild 실행 (--clean 옵션)..." -ForegroundColor Cyan
Write-Host "⚠️  git 변경사항 확인 후 'y' 입력하세요" -ForegroundColor Yellow
npx expo prebuild --clean --platform android

Write-Host "`n[3/3] Android 빌드 시작..." -ForegroundColor Cyan
npm run android

Write-Host "`n✅ 완료!" -ForegroundColor Green




