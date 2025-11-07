# 위젯 녹화 디버깅용 로그 (FloatingService, FloatingWidgetModule, MainActivity만)

Write-Host "=== 위젯 녹화 디버깅 로그 ===" -ForegroundColor Green
Write-Host "중지하려면 Ctrl+C를 누르세요" -ForegroundColor Yellow
Write-Host ""

# adb 경로 찾기
$adbPath = $null

# ANDROID_HOME 환경 변수 확인
if ($env:ANDROID_HOME) {
    $adbPath = Join-Path $env:ANDROID_HOME "platform-tools\adb.exe"
    if (Test-Path $adbPath) {
        Write-Host "adb 경로: $adbPath" -ForegroundColor Cyan
    } else {
        $adbPath = $null
    }
}

# LOCALAPPDATA에서 찾기
if (-not $adbPath) {
    $sdkPath = Join-Path $env:LOCALAPPDATA "Android\Sdk"
    $adbPath = Join-Path $sdkPath "platform-tools\adb.exe"
    if (Test-Path $adbPath) {
        Write-Host "adb 경로: $adbPath" -ForegroundColor Cyan
    } else {
        $adbPath = $null
    }
}

# 직접 경로 시도
if (-not $adbPath) {
    $possiblePaths = @(
        "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk\platform-tools\adb.exe",
        "C:\Android\Sdk\platform-tools\adb.exe",
        "C:\Program Files\Android\android-sdk\platform-tools\adb.exe"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $adbPath = $path
            Write-Host "adb 경로: $adbPath" -ForegroundColor Cyan
            break
        }
    }
}

if (-not $adbPath) {
    Write-Host "❌ adb를 찾을 수 없습니다!" -ForegroundColor Red
    Write-Host ""
    Write-Host "해결 방법:" -ForegroundColor Yellow
    Write-Host "1. Android SDK Platform Tools가 설치되어 있는지 확인"
    Write-Host "2. Android Studio > SDK Manager > SDK Tools > Android SDK Platform-Tools 설치"
    Write-Host "3. 또는 수동으로 adb.exe 경로를 입력하세요"
    Write-Host ""
    $manualPath = Read-Host "adb.exe 전체 경로를 입력하세요 (또는 Enter로 종료)"
    if ($manualPath -and (Test-Path $manualPath)) {
        $adbPath = $manualPath
    } else {
        exit 1
    }
}

# 로그 버퍼 초기화
& $adbPath logcat -c

# 위젯 관련 로그만 필터링
& $adbPath logcat FloatingService:* FloatingWidgetModule:* MainActivity:* *:S
