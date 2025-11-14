# 다른 컴퓨터에서 필요한 파일 가이드

GitHub에 올라가지 않은 필수 파일들을 다른 컴퓨터에서 설정하는 방법입니다.

## 🔴 필수 파일 목록

### 1. Android SDK 경로 설정 파일

**파일명:** `frontend/android/local.properties`

**위치:** `frontend/android/local.properties`

**내용:**
```properties
sdk.dir=C\:\\Users\\[사용자명]\\AppData\\Local\\Android\\Sdk
```

**설정 방법:**
- Android Studio에서 프로젝트를 열면 자동으로 생성됩니다
- 또는 수동으로 생성:
  ```bash
  cd frontend/android
  echo sdk.dir=C\:\\Users\\[사용자명]\\AppData\\Local\\Android\\Sdk > local.properties
  ```
- Windows에서 사용자명 확인: `echo %USERNAME%`

**주의:** 각 컴퓨터마다 SDK 경로가 다르므로 Git에 포함되지 않습니다.

---

### 2. Firebase 키 파일 (백엔드)

**파일명:** `firebase-key.json` 또는 `firebase-adminsdk-*.json`

**위치:** `backend/app/core/firebase-key.json`

**설정 방법:**
1. Firebase Console (https://console.firebase.google.com/) 접속
2. 프로젝트 선택
3. 프로젝트 설정 > 서비스 계정
4. "새 비공개 키 생성" 클릭
5. 다운로드한 JSON 파일을 `backend/app/core/firebase-key.json`으로 저장

**또는 환경 변수 사용:**
```bash
# Windows PowerShell
$env:FIREBASE_KEY_PATH="C:\path\to\firebase-key.json"
```

**주의:** 보안상 Git에 포함되지 않습니다. 다른 컴퓨터에서는 Firebase Console에서 새로 다운로드하거나 기존 파일을 안전하게 전달받아야 합니다.

---

### 3. Python 가상환경

**디렉토리:** `backend/venv/`

**설정 방법:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r ..\requirements.txt
```

**주의:** 각 컴퓨터에서 새로 생성해야 합니다.

---

### 4. Node.js 의존성

**디렉토리:** `frontend/node_modules/`

**설정 방법:**
```bash
cd frontend
npm install
```

**주의:** `package.json`이 있으면 자동으로 설치됩니다.

---

### 5. 모델 가중치 파일

**디렉토리:** `backend/weights/`

**필요한 파일:**
- `Meso4_DF.h5` - MesoNet 모델 가중치 (필수) ✅
- `effb0_dfdc.pth` - EfficientNet 모델 가중치 (현재 미사용) ❌

**현재 프로젝트 상태:**
- 프론트엔드에서 사용 중: `/analyze-video/` 엔드포인트
- **MesoNet 단독 모델만 사용** (Meso4_DF.h5 파일만 필요) ✅
- `/analyze-video-optimized/` 엔드포인트는 현재 사용하지 않음
- **`effb0_dfdc.pth` 파일은 현재 사용되지 않습니다** ❌

**설정 방법:**
1. **필수 파일**: `Meso4_DF.h5`를 기존 컴퓨터에서 복사
   ```bash
   # 기존 컴퓨터에서
   # backend/weights/Meso4_DF.h5 파일을 USB나 클라우드로 복사
   
   # 새 컴퓨터에서
   # backend/weights/ 폴더에 붙여넣기
   ```

2. **선택 파일**: `effb0_dfdc.pth` (최적화 기능 사용 시)
   - 다운로드 스크립트 실행:
     ```bash
     cd backend
     python download_models.py
     ```

**주의:** 파일 크기가 커서 Git에 포함되지 않습니다.

---

### 6. Android 빌드 파일들 (자동 생성)

**디렉토리:** `frontend/android/.gradle/`, `frontend/android/build/`, `frontend/android/app/build/`

**설정 방법:**
- Android Studio에서 프로젝트를 열면 자동으로 생성됩니다
- 또는 Gradle 빌드 실행:
  ```bash
  cd frontend/android
  ./gradlew build
  ```

**주의:** 빌드 시 자동 생성되므로 수동 설정 불필요

---

## 📋 다른 컴퓨터 설정 체크리스트

### 필수 설정 (반드시 필요)

- [ ] **Android SDK 경로 설정**
  - Android Studio 설치 확인
  - `frontend/android/local.properties` 파일 생성
  - SDK 경로 확인: `C:\Users\[사용자명]\AppData\Local\Android\Sdk`

- [ ] **Firebase 키 파일**
  - Firebase Console에서 키 파일 다운로드
  - `backend/app/core/firebase-key.json`에 저장
  - 또는 환경 변수 설정

- [ ] **Python 가상환경 생성**
  ```bash
  cd backend
  python -m venv venv
  venv\Scripts\activate
  pip install -r ..\requirements.txt
  ```

- [ ] **Node.js 의존성 설치**
  ```bash
  cd frontend
  npm install
  ```

### 선택 설정 (기능 사용 시 필요)

- [ ] **모델 가중치 파일**
  - `backend/weights/Meso4_DF.h5` 다운로드 또는 복사
  - 또는 `python download_models.py` 실행

---

## 🚀 빠른 설정 스크립트

다음 스크립트를 실행하면 대부분 자동으로 설정됩니다:

### Windows PowerShell

```powershell
# 1. Android SDK 경로 설정
$username = $env:USERNAME
$sdkPath = "C:\Users\$username\AppData\Local\Android\Sdk"
$localProps = "frontend\android\local.properties"
if (-not (Test-Path $localProps)) {
    "sdk.dir=$($sdkPath -replace '\\', '\\')" | Out-File -FilePath $localProps -Encoding ASCII
    Write-Host "✅ local.properties 생성 완료"
}

# 2. Python 가상환경 생성
if (-not (Test-Path "backend\venv")) {
    cd backend
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r ..\requirements.txt
    cd ..
    Write-Host "✅ Python 가상환경 생성 완료"
}

# 3. Node.js 의존성 설치
if (-not (Test-Path "frontend\node_modules")) {
    cd frontend
    npm install
    cd ..
    Write-Host "✅ Node.js 의존성 설치 완료"
}

Write-Host "⚠️  Firebase 키 파일은 수동으로 설정해야 합니다!"
Write-Host "   backend/app/core/firebase-key.json"
```

---

## 📝 파일 전달 방법

### 안전하게 전달해야 하는 파일

1. **Firebase 키 파일**
   - 암호화된 채널로 전달 (이메일 암호화, USB 등)
   - 또는 Firebase Console에서 새로 다운로드

2. **모델 가중치 파일** (선택)
   - USB 또는 클라우드 스토리지로 전달
   - 또는 다운로드 스크립트 사용

### 자동 생성되는 파일 (전달 불필요)

- `local.properties` - 각 컴퓨터에서 자동 생성
- `venv/` - 각 컴퓨터에서 새로 생성
- `node_modules/` - npm install로 자동 설치
- 빌드 파일들 - 빌드 시 자동 생성

---

## ⚠️ 주의사항

1. **Firebase 키 파일은 절대 Git에 올리지 마세요!**
   - 보안 위험
   - `.gitignore`에 포함되어 있음

2. **local.properties는 각 컴퓨터마다 다릅니다**
   - 사용자명과 SDK 설치 경로에 따라 다름

3. **모델 파일은 용량이 큽니다**
   - Git LFS를 사용하거나 별도로 관리

4. **가상환경은 각 컴퓨터에서 새로 생성**
   - Python 버전이 다를 수 있음

---

## 🔗 관련 문서

- [SETUP_NEW_COMPUTER.md](./SETUP_NEW_COMPUTER.md) - 전체 설정 가이드
- [FIREBASE_SETUP_GUIDE.md](./FIREBASE_SETUP_GUIDE.md) - Firebase 설정 상세 가이드

