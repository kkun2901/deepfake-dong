# 다른 컴퓨터에서 필요한 파일 체크리스트

## 🔴 필수 파일 (반드시 설정 필요)

### 1. Android SDK 경로 설정
**파일:** `frontend/android/local.properties`

**설정 방법:**
```bash
# Windows에서 사용자명 확인
echo %USERNAME%

# local.properties 파일 생성
cd frontend/android
echo sdk.dir=C\:\\Users\\[사용자명]\\AppData\\Local\\Android\\Sdk > local.properties
```

**또는:** Android Studio에서 프로젝트를 열면 자동 생성됩니다.

---

### 2. Firebase 키 파일 ⚠️ 보안 중요
**파일:** `backend/app/core/firebase-key.json`

**설정 방법:**
1. Firebase Console 접속: https://console.firebase.google.com/
2. 프로젝트 선택
3. 프로젝트 설정 > 서비스 계정
4. "새 비공개 키 생성" 클릭
5. 다운로드한 JSON 파일을 `backend/app/core/firebase-key.json`으로 저장

**주의:** 이 파일은 보안상 Git에 포함되지 않습니다. 안전하게 전달받거나 새로 다운로드해야 합니다.

---

## 🟡 자동 생성 파일 (명령어로 생성)

### 3. Python 가상환경
**디렉토리:** `backend/venv/`

**생성 방법:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements.txt
```

---

### 4. Node.js 의존성
**디렉토리:** `frontend/node_modules/`

**설정 방법:**
```bash
cd frontend
npm install
```

---

## 🟢 선택 파일 (기능 사용 시 필요)

### 5. 모델 가중치 파일
**디렉토리:** `backend/weights/`

**필요한 파일:**
- `Meso4_DF.h5` - MesoNet 모델 (필수) ✅
- `effb0_dfdc.pth` - EfficientNet 모델 (현재 미사용) ❌

**중요:** 
- **`Meso4_DF.h5` 파일만 있으면 기본 기능 정상 동작** ✅
- 현재 프론트엔드는 `/analyze-video/` 엔드포인트 사용 (MesoNet 단독)
- **`effb0_dfdc.pth` 파일은 현재 사용되지 않습니다** ❌
- EfficientNet은 `/analyze-video-optimized/` 엔드포인트에서만 사용 (현재 미사용)

**설정 방법:**
1. 기존 컴퓨터에서 `backend/weights/Meso4_DF.h5` 파일 복사
2. 새 컴퓨터의 `backend/weights/` 폴더에 붙여넣기

**주의:** 파일 크기가 커서 Git에 포함되지 않습니다.

---

## 📋 빠른 설정 스크립트

다음 PowerShell 스크립트를 실행하면 자동으로 설정됩니다:

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

Write-Host ""
Write-Host "⚠️  다음 파일은 수동으로 설정해야 합니다:"
Write-Host "   1. backend/app/core/firebase-key.json (Firebase Console에서 다운로드)"
Write-Host "   2. backend/weights/Meso4_DF.h5 (모델 파일, 선택사항)"
```

---

## ✅ 최종 체크리스트

다른 컴퓨터에서 프로젝트를 클론한 후:

- [ ] **Android SDK 경로 설정** (`frontend/android/local.properties`)
- [ ] **Firebase 키 파일** (`backend/app/core/firebase-key.json`)
- [ ] **Python 가상환경 생성** (`backend/venv/`)
- [ ] **Node.js 의존성 설치** (`frontend/node_modules/`)
- [ ] **모델 파일** (`backend/weights/Meso4_DF.h5`) - 선택사항

---

## 📝 파일 전달 방법

### 안전하게 전달해야 하는 파일:
1. **firebase-key.json** - 암호화된 채널로 전달 또는 Firebase Console에서 새로 다운로드
2. **모델 파일** (*.h5, *.pth) - USB 또는 클라우드 스토리지

### 자동 생성되는 파일 (전달 불필요):
- `local.properties` - 각 컴퓨터에서 자동 생성
- `venv/` - 각 컴퓨터에서 새로 생성
- `node_modules/` - npm install로 자동 설치

---

## 🔗 관련 문서

- [MISSING_FILES_GUIDE.md](./MISSING_FILES_GUIDE.md) - 상세 가이드
- [SETUP_NEW_COMPUTER.md](./SETUP_NEW_COMPUTER.md) - 전체 설정 가이드

