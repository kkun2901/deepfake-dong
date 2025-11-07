@echo off
echo ========================================
echo Metro 번들러 및 모든 캐시 완전 삭제
echo ========================================
echo.

REM Metro 번들러 캐시 삭제
echo [1/5] Metro 번들러 캐시 삭제 중...
if exist ".expo" (
    rmdir /s /q ".expo" 2>nul
    echo   .expo 폴더 삭제 완료
)

REM node_modules 캐시 삭제
echo [2/5] node_modules 캐시 삭제 중...
if exist "node_modules\.cache" (
    rmdir /s /q "node_modules\.cache" 2>nul
    echo   node_modules\.cache 삭제 완료
)

REM watchman 캐시 (있는 경우)
echo [3/5] watchman 캐시 확인 중...
if exist "%TEMP%\metro-*" (
    del /q /f "%TEMP%\metro-*" 2>nul
    echo   Metro 임시 파일 삭제 완료
)

REM Android 빌드 캐시
echo [4/5] Android 빌드 캐시 삭제 중...
cd android
if exist ".gradle" (
    call gradlew.bat --stop >nul 2>&1
    timeout /t 2 >nul
    rmdir /s /q ".gradle" 2>nul
    echo   .gradle 폴더 삭제 완료
)
if exist "app\build" (
    rmdir /s /q "app\build" 2>nul
    echo   app\build 폴더 삭제 완료
)
cd ..

REM TypeScript 빌드 정보 삭제
echo [5/5] TypeScript 빌드 정보 삭제 중...
if exist "*.tsbuildinfo" (
    del /q /f "*.tsbuildinfo" 2>nul
    echo   TypeScript 빌드 정보 삭제 완료
)

echo.
echo ========================================
echo 모든 캐시 삭제 완료!
echo ========================================
echo.
echo 다음 명령어로 앱을 다시 빌드하세요:
echo   npm run android
echo.


