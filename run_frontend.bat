@echo off
chcp 65001 >nul
echo ========================================
echo 프론트엔드 실행 스크립트
echo ========================================
echo.

cd /d "%~dp0deepfake-detector-app-main\frontend"

if not exist "node_modules" (
    echo [1/2] node_modules가 없습니다. 의존성 설치 중...
    call npm install
    if errorlevel 1 (
        echo [오류] npm install 실패!
        pause
        exit /b 1
    )
    echo [완료] 의존성 설치 완료!
    echo.
) else (
    echo [1/2] 의존성 확인 완료
    echo.
)

echo [2/2] Expo 개발 서버 시작 중...
echo.
echo 사용 가능한 옵션:
echo   - 스마트폰에서 Expo Go 앱으로 QR 코드 스캔
echo   - 'a' 키: Android 에뮬레이터에서 실행
echo   - 'i' 키: iOS 시뮬레이터에서 실행 (Mac만)
echo   - 'w' 키: 웹 브라우저에서 실행
echo.

call npm start

pause



