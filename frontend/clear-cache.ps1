# Metro 번들러 캐시 완전 정리

Write-Host "=== Metro 캐시 완전 정리 ===" -ForegroundColor Green

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "`n[1/5] .expo 디렉토리 삭제..." -ForegroundColor Cyan
Remove-Item -Recurse -Force .expo -ErrorAction SilentlyContinue

Write-Host "`n[2/5] node_modules/.cache 삭제..." -ForegroundColor Cyan
Remove-Item -Recurse -Force node_modules\.cache -ErrorAction SilentlyContinue

Write-Host "`n[3/5] Metro 번들러 캐시 삭제..." -ForegroundColor Cyan
Remove-Item -Recurse -Force $env:TEMP\metro-* -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $env:TEMP\haste-* -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $env:TEMP\react-* -ErrorAction SilentlyContinue

Write-Host "`n[4/5] watchman 캐시 삭제 (설치된 경우)..." -ForegroundColor Cyan
watchman watch-del-all 2>&1 | Out-Null

Write-Host "`n[5/5] Metro 서버 재시작 (--clear 옵션)..." -ForegroundColor Cyan
Write-Host "이제 'npx expo start --clear' 명령어를 실행하세요." -ForegroundColor Yellow

Write-Host "`n✅ 캐시 정리 완료!" -ForegroundColor Green




