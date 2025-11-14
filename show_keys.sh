#!/bin/bash

# 백엔드와 프론트엔드 키 확인 스크립트

echo "========================================"
echo "백엔드 설정 확인"
echo "========================================"
echo ""

# 백엔드 설정 파일 확인
BACKEND_CONFIG="deepfake-detector-app-main/backend/app/core/config.py"
if [ -f "$BACKEND_CONFIG" ]; then
    echo "[백엔드] 설정 파일: $BACKEND_CONFIG"
    echo ""
    grep -E "WEIGHTS|FRAME|IMAGE_SIZE|ENSEMBLE|THREADS" "$BACKEND_CONFIG" | sed 's/^/  /'
else
    echo "[백엔드] 설정 파일을 찾을 수 없습니다: $BACKEND_CONFIG"
fi

echo ""
echo "========================================"
echo "프론트엔드 API URL 확인"
echo "========================================"
echo ""

# 프론트엔드 API URL 확인
FRONTEND_FILES=(
    "deepfake-detector-app-main/frontend/src/api/index.ts"
    "deepfake-detector-app-main/frontend/src/utils/checkServer.ts"
    "deepfake-detector-app-main/frontend/src/api/community.ts"
    "deepfake-detector-app-main/frontend/android/app/src/main/java/com/anonymous/deepfakeapp/FloatingService.kt"
)

for file in "${FRONTEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "[프론트엔드] 파일: $file"
        grep -oE "https?://[^[:space:]'\"]+" "$file" | sed 's/^/  API URL: /' || echo "  API URL을 찾을 수 없습니다"
        echo ""
    fi
done

echo "========================================"
echo "백엔드 서버 포트 확인"
echo "========================================"
echo ""

BACKEND_SERVER="deepfake-detector-app-main/backend/run_server.bat"
if [ -f "$BACKEND_SERVER" ]; then
    echo "[백엔드] 서버 실행 파일: $BACKEND_SERVER"
    PORT=$(grep -oE "--port[[:space:]]+[0-9]+" "$BACKEND_SERVER" | grep -oE "[0-9]+" | head -1)
    if [ -n "$PORT" ]; then
        echo "  포트: $PORT"
    else
        echo "  포트: 8000 (기본값)"
    fi
fi

echo ""
echo "========================================"
echo "완료"
echo "========================================"




