@echo off
echo ========================================
echo 프론트엔드 개발 서버 시작
echo ========================================
cd frontend

echo.
echo npm 패키지 설치 중...
call npm install

echo.
echo Expo 개발 서버 시작...
call npm start

pause


