@echo off
echo Starting Deepfake Detection API Server...
echo.

REM Python 가상환경 확인
if not exist "venv\" (
    echo 가상환경이 없습니다. 생성 중...
    python -m venv venv
    echo.
)

REM 가상환경의 Python 경로 확인
set PYTHON_EXE=%~dp0venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    echo 오류: 가상환경 Python 실행 파일을 찾을 수 없습니다: %PYTHON_EXE%
    pause
    exit /b 1
)

echo 사용 중인 Python: %PYTHON_EXE%
echo.

REM 패키지 설치 확인
echo 패키지 설치 확인 중...
"%PYTHON_EXE%" -m pip install -r ..\requirements.txt

echo.
echo 백엔드 서버 시작...
echo 파일 업로드를 위해 max_request_size 증가 (500MB)
"%PYTHON_EXE%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --limit-max-requests 500000000

pause

