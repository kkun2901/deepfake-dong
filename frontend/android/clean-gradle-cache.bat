@echo off
REM Gradle 캐시 정리 스크립트

echo Gradle 캐시 정리 중...

REM Gradle 데몬 중지
call gradlew.bat --stop >nul 2>&1

REM 손상된 dependencies-accessors 폴더 삭제
if exist ".gradle\8.8\dependencies-accessors" (
    echo dependencies-accessors 폴더 삭제 중...
    rmdir /s /q ".gradle\8.8\dependencies-accessors" 2>nul
)

REM .gradle 폴더 전체 삭제 (선택사항)
REM rmdir /s /q ".gradle" 2>nul

echo 캐시 정리 완료!


