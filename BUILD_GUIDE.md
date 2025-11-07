# Android 빌드 가이드

## 🛠️ 빌드 방법

### 방법 1: PowerShell 스크립트 사용 (Windows)

```powershell
# 디버그 APK 빌드 (기본값)
cd frontend
.\build-android.ps1

# 또는 빌드 타입 지정
.\build-android.ps1 debug     # 디버그 APK
.\build-android.ps1 release   # 릴리스 APK
.\build-android.ps1 bundle    # AAB 번들 (Play Store용)
```

### 방법 2: Expo CLI 사용 (권장 - 개발용)

```bash
cd frontend
npm run android
```

이 명령어는:
- Metro 번들러를 시작하고
- 에뮬레이터/연결된 기기에서 앱을 실행합니다

### 방법 3: Gradle 직접 사용

#### Windows
```powershell
cd frontend/android
.\gradlew.bat assembleDebug      # 디버그 APK
.\gradlew.bat assembleRelease    # 릴리스 APK
.\gradlew.bat bundleRelease      # AAB 번들
```

#### Linux/Mac
```bash
cd frontend/android
./gradlew assembleDebug      # 디버그 APK
./gradlew assembleRelease    # 릴리스 APK
./gradlew bundleRelease      # AAB 번들
```

### 방법 4: Bash 스크립트 사용 (Linux/Mac)

```bash
cd frontend
chmod +x build-android.sh
./build-android.sh [debug|release|bundle]
```

## 📱 빌드된 파일 위치

### 디버그 APK
```
frontend/android/app/build/outputs/apk/debug/app-debug.apk
```

### 릴리스 APK
```
frontend/android/app/build/outputs/apk/release/app-release.apk
```

### AAB 번들 (Play Store용)
```
frontend/android/app/build/outputs/bundle/release/app-release.aab
```

## ⚙️ 빌드 전 확인사항

1. **JDK 설치 확인**
   ```bash
   java -version  # Java 17 이상 필요
   ```

2. **Android SDK 설정**
   - Android Studio 설치
   - `ANDROID_HOME` 환경 변수 설정 확인
   - SDK 경로: `%LOCALAPPDATA%\Android\Sdk` (Windows)

3. **의존성 설치**
   ```bash
   cd frontend
   npm install
   ```

4. **네이티브 모듈 빌드**
   - Kotlin 파일 변경 시 반드시 네이티브 빌드 필요
   - `expo prebuild` 실행 필요할 수 있음

## 🔐 릴리스 빌드 서명

릴리스 APK/AAB는 서명이 필요합니다.

### 키스토어 생성 (처음 한 번만)
```bash
cd frontend/android/app
keytool -genkeypair -v -storetype PKCS12 -keystore deepfake-key.jks -alias deepfake -keyalg RSA -keysize 2048 -validity 10000
```

### 서명 설정
`frontend/android/app/build.gradle`에 서명 정보 추가:
```gradle
android {
    signingConfigs {
        release {
            storeFile file('deepfake-key.jks')
            storePassword 'your-password'
            keyAlias 'deepfake'
            keyPassword 'your-password'
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

## 🐛 빌드 문제 해결

### 1. Gradle 빌드 실패
```bash
cd frontend/android
./gradlew clean
./gradlew assembleDebug
```

### 2. 의존성 문제
```bash
cd frontend
rm -rf node_modules
rm package-lock.json
npm install
```

### 3. 네이티브 모듈 변경 후
```bash
cd frontend
npx expo prebuild --clean
```

### 4. Kotlin 컴파일 에러
- Android Studio에서 프로젝트 열기
- `File > Invalidate Caches / Restart`
- `Build > Clean Project`
- `Build > Rebuild Project`

## 📋 빌드 체크리스트

- [ ] 모든 의존성 설치 완료
- [ ] Android SDK 및 JDK 설치 확인
- [ ] 네이티브 코드 변경사항 반영
- [ ] 릴리스 빌드 시 서명 설정 완료
- [ ] `app.json`의 버전 정보 업데이트
- [ ] 필요한 권한이 `AndroidManifest.xml`에 추가됨

## 🚀 빠른 빌드 명령어

```powershell
# Windows - 디버그 빌드
cd frontend && .\build-android.ps1 debug

# Windows - 릴리스 빌드
cd frontend && .\build-android.ps1 release

# Expo 개발 서버 시작
cd frontend && npm start
```












