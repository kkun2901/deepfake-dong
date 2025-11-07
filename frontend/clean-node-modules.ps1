# node_modules 강제 삭제 스크립트 (Windows 경로 길이 문제 해결)

Write-Host "=== node_modules 강제 삭제 ===" -ForegroundColor Green

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`n방법 1: npm cache clean 후 재설치 시도..." -ForegroundColor Cyan
npm cache clean --force

Write-Host "`n방법 2: Rimraf를 사용한 삭제 (설치 필요시)..." -ForegroundColor Cyan
npx rimraf node_modules

Write-Host "`n방법 3: npm install --force로 재설치..." -ForegroundColor Cyan
npm install --force

Write-Host "`n✅ 완료!" -ForegroundColor Green




