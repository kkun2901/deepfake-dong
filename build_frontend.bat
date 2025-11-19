@echo off
echo ========================================
echo 프론트엔드 앱 빌드 (Android)
echo ========================================
cd frontend

echo.
echo npm 패키지 설치 중...
call npm install

echo.
echo Android 앱 빌드 중...
call npm run android

pause


