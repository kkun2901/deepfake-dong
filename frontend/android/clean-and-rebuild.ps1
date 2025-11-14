# 완전한 클린 빌드 스크립트
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "완전한 클린 빌드 시작" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Gradle 데몬 중지
Write-Host "[1/5] Gradle 데몬 중지 중..." -ForegroundColor Yellow
& .\gradlew.bat --stop 2>$null
Start-Sleep -Seconds 2

# 2. 모든 빌드 출력 삭제
Write-Host "[2/5] 빌드 출력 폴더 삭제 중..." -ForegroundColor Yellow
if (Test-Path "app\build") {
    cmd /c "rmdir /s /q app\build" 2>$null
    Write-Host "  app\build 삭제 완료" -ForegroundColor Green
}
if (Test-Path "build") {
    cmd /c "rmdir /s /q build" 2>$null
    Write-Host "  build 삭제 완료" -ForegroundColor Green
}

# 3. .gradle 캐시 삭제
Write-Host "[3/5] Gradle 캐시 삭제 중..." -ForegroundColor Yellow
if (Test-Path ".gradle") {
    Get-Process | Where-Object { $_.Path -like "*gradle*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    cmd /c "rmdir /s /q .gradle" 2>$null
    Write-Host "  .gradle 삭제 완료" -ForegroundColor Green
}

# 4. .idea 폴더의 빌드 캐시 삭제 (있는 경우)
Write-Host "[4/5] IDE 캐시 확인 중..." -ForegroundColor Yellow
if (Test-Path "..\.idea\workspace.xml") {
    Write-Host "  IDE 캐시 발견 (무시 가능)" -ForegroundColor Gray
}

# 5. 클린 빌드 실행
Write-Host "[5/5] 클린 빌드 실행 중..." -ForegroundColor Yellow
Write-Host ""
& .\gradlew.bat clean --no-build-cache --no-daemon

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "클린 빌드 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "이제 상위 디렉토리에서 'npm run android'를 실행하세요." -ForegroundColor Cyan










