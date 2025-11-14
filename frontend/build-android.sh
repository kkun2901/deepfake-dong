#!/bin/bash
# Android 빌드 스크립트 (Linux/Mac)
# 사용법: ./build-android.sh [debug|release|bundle]

BUILD_TYPE=${1:-debug}

echo "=== 딥페이크 탐지 앱 Android 빌드 ==="
echo "빌드 타입: $BUILD_TYPE"

# frontend 디렉토리로 이동
cd "$(dirname "$0")"

# Node modules 확인
if [ ! -d "node_modules" ]; then
    echo "node_modules 없음. npm install 실행 중..."
    npm install
fi

# Android 디렉토리로 이동
cd android

case "$BUILD_TYPE" in
    debug)
        echo ""
        echo "[1/2] 디버그 APK 빌드 중..."
        ./gradlew assembleDebug
        
        if [ $? -eq 0 ]; then
            APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
            if [ -f "$APK_PATH" ]; then
                echo ""
                echo "✅ 빌드 성공!"
                echo "APK 위치: $(realpath $APK_PATH)"
            fi
        else
            echo ""
            echo "❌ 빌드 실패"
            exit 1
        fi
        ;;
    
    release)
        echo ""
        echo "[1/2] 릴리스 APK 빌드 중..."
        ./gradlew assembleRelease
        
        if [ $? -eq 0 ]; then
            APK_PATH="app/build/outputs/apk/release/app-release.apk"
            if [ -f "$APK_PATH" ]; then
                echo ""
                echo "✅ 빌드 성공!"
                echo "APK 위치: $(realpath $APK_PATH)"
                echo ""
                echo "⚠️  릴리스 APK는 서명이 필요합니다."
            fi
        else
            echo ""
            echo "❌ 빌드 실패"
            exit 1
        fi
        ;;
    
    bundle)
        echo ""
        echo "[1/2] AAB 번들 빌드 중..."
        ./gradlew bundleRelease
        
        if [ $? -eq 0 ]; then
            AAB_PATH="app/build/outputs/bundle/release/app-release.aab"
            if [ -f "$AAB_PATH" ]; then
                echo ""
                echo "✅ 빌드 성공!"
                echo "AAB 위치: $(realpath $AAB_PATH)"
                echo ""
                echo "⚠️  AAB는 서명이 필요합니다 (Google Play Store 업로드용)"
            fi
        else
            echo ""
            echo "❌ 빌드 실패"
            exit 1
        fi
        ;;
    
    *)
        echo ""
        echo "❌ 잘못된 빌드 타입: $BUILD_TYPE"
        echo "사용법: ./build-android.sh [debug|release|bundle]"
        exit 1
        ;;
esac

cd ..
echo ""
echo "빌드 완료!"




















