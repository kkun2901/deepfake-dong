# 전체 정리 및 재빌드 스크립트 (경로 길이 문제 회피)

Write-Host "=== 전체 정리 및 재빌드 ===" -ForegroundColor Green

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`n[1/6] npm cache 정리..." -ForegroundColor Cyan
npm cache clean --force

Write-Host "`n[2/6] Rimraf로 node_modules 삭제 시도..." -ForegroundColor Cyan
npx rimraf node_modules 2>&1 | Out-Null

Write-Host "`n[3/6] package-lock.json 삭제..." -ForegroundColor Cyan
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue

Write-Host "`n[4/6] 패키지 재설치..." -ForegroundColor Cyan
npm install

Write-Host "`n[5/6] Android 빌드 캐시 정리..." -ForegroundColor Cyan
if (Test-Path "android") {
    Remove-Item -Recurse -Force android\.gradle -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force android\app\build -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force android\build -ErrorAction SilentlyContinue
}

Write-Host "`n[6/6] Expo prebuild 실행..." -ForegroundColor Cyan
Write-Host "⚠️  git 변경사항 확인 후 'y' 입력하세요" -ForegroundColor Yellow
npx expo prebuild --clean --platform android

Write-Host "`n✅ 완료! 이제 npm run android를 실행하세요." -ForegroundColor Green




