# Android 빌드 스크립트
# 사용법: .\build-android.ps1 [debug|release|bundle]

param(
    [string]$BuildType = "debug"
)

Write-Host "=== 딥페이크 탐지 앱 Android 빌드 ===" -ForegroundColor Green
Write-Host "빌드 타입: $BuildType" -ForegroundColor Yellow

# frontend 디렉토리로 이동
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Node modules 확인
if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules 없음. npm install 실행 중..." -ForegroundColor Yellow
    npm install
}

# Android 디렉토리로 이동
Set-Location android

switch ($BuildType.ToLower()) {
    "debug" {
        Write-Host "`n[1/2] 디버그 APK 빌드 중..." -ForegroundColor Cyan
        & .\gradlew.bat assembleDebug
        
        if ($LASTEXITCODE -eq 0) {
            $apkPath = "app\build\outputs\apk\debug\app-debug.apk"
            if (Test-Path $apkPath) {
                Write-Host "`n✅ 빌드 성공!" -ForegroundColor Green
                Write-Host "APK 위치: $((Resolve-Path $apkPath).Path)" -ForegroundColor Cyan
            }
        } else {
            Write-Host "`n❌ 빌드 실패" -ForegroundColor Red
            exit 1
        }
    }
    
    "release" {
        Write-Host "`n[1/2] 릴리스 APK 빌드 중..." -ForegroundColor Cyan
        & .\gradlew.bat assembleRelease
        
        if ($LASTEXITCODE -eq 0) {
            $apkPath = "app\build\outputs\apk\release\app-release.apk"
            if (Test-Path $apkPath) {
                Write-Host "`n✅ 빌드 성공!" -ForegroundColor Green
                Write-Host "APK 위치: $((Resolve-Path $apkPath).Path)" -ForegroundColor Cyan
                Write-Host "`n⚠️  릴리스 APK는 서명이 필요합니다." -ForegroundColor Yellow
            }
        } else {
            Write-Host "`n❌ 빌드 실패" -ForegroundColor Red
            exit 1
        }
    }
    
    "bundle" {
        Write-Host "`n[1/2] AAB 번들 빌드 중..." -ForegroundColor Cyan
        & .\gradlew.bat bundleRelease
        
        if ($LASTEXITCODE -eq 0) {
            $aabPath = "app\build\outputs\bundle\release\app-release.aab"
            if (Test-Path $aabPath) {
                Write-Host "`n✅ 빌드 성공!" -ForegroundColor Green
                Write-Host "AAB 위치: $((Resolve-Path $aabPath).Path)" -ForegroundColor Cyan
                Write-Host "`n⚠️  AAB는 서명이 필요합니다 (Google Play Store 업로드용)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "`n❌ 빌드 실패" -ForegroundColor Red
            exit 1
        }
    }
    
    default {
        Write-Host "`n❌ 잘못된 빌드 타입: $BuildType" -ForegroundColor Red
        Write-Host "사용법: .\build-android.ps1 [debug|release|bundle]" -ForegroundColor Yellow
        exit 1
    }
}

Set-Location ..
Write-Host "`n빌드 완료!" -ForegroundColor Green












