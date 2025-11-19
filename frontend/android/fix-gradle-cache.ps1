# Gradle 캐시 완전 삭제 스크립트
Write-Host "Gradle 캐시 완전 삭제 중..." -ForegroundColor Yellow

# Gradle 데몬 중지
Write-Host "[1/3] Gradle 데몬 중지 중..." -ForegroundColor Cyan
& .\gradlew.bat --stop 2>$null
Start-Sleep -Seconds 2

# .gradle 폴더 완전 삭제 (dependencies-accessors 포함)
Write-Host "[2/3] .gradle 폴더 삭제 중..." -ForegroundColor Cyan
if (Test-Path ".gradle") {
    # 강제로 모든 프로세스 종료 후 삭제 시도
    Get-Process | Where-Object { $_.Path -like "*gradle*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    
    # cmd를 통해 삭제 (Windows 경로 길이 제한 우회)
    cmd /c "rmdir /s /q .gradle" 2>$null
    Write-Host "  .gradle 폴더 삭제 완료" -ForegroundColor Green
} else {
    Write-Host "  .gradle 폴더가 없습니다" -ForegroundColor Gray
}

# app/build 폴더 삭제
Write-Host "[3/3] app/build 폴더 삭제 중..." -ForegroundColor Cyan
if (Test-Path "app\build") {
    cmd /c "rmdir /s /q app\build" 2>$null
    Write-Host "  app/build 폴더 삭제 완료" -ForegroundColor Green
} else {
    Write-Host "  app/build 폴더가 없습니다" -ForegroundColor Gray
}

Write-Host "`n캐시 삭제 완료! 이제 빌드를 시도하세요." -ForegroundColor Green













