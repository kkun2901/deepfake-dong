# 새 컴퓨터에서 프로젝트 설정 가이드

이 가이드는 다른 컴퓨터에서 이 프로젝트를 바로 사용할 수 있도록 설정하는 방법을 설명합니다.

## 사전 요구사항

### 1. 필수 소프트웨어 설치

#### Android Studio
- Android Studio를 설치합니다 (이미 설치되어 있다고 가정)
- Android SDK가 설치되어 있어야 합니다
- SDK 경로는 보통 `C:\Users\[사용자명]\AppData\Local\Android\Sdk` 입니다

#### Node.js
- Node.js 18 이상 설치 필요
- [Node.js 다운로드](https://nodejs.org/)

#### Python
- Python 3.8 이상 설치 필요
- [Python 다운로드](https://www.python.org/downloads/)

#### Git
- Git 설치 필요 (이미 설치되어 있다고 가정)

## 프로젝트 클론 및 설정

### 1. 프로젝트 클론

```bash
git clone [저장소 URL]
cd deepfake-detector-app-main
```

### 2. Android SDK 경로 설정

프로젝트를 클론한 후, Android SDK 경로를 설정해야 합니다:

**Windows:**
```bash
cd frontend/android
# local.properties 파일 생성 (자동 생성됨)
# 또는 수동으로 생성:
echo sdk.dir=C\:\\Users\\[사용자명]\\AppData\\Local\\Android\\Sdk > local.properties
```

**참고:** `local.properties` 파일은 자동으로 생성되거나 Android Studio에서 자동으로 설정됩니다.

### 3. 프론트엔드 설정

```bash
cd frontend

# 의존성 설치
npm install

# Android 빌드 (처음 한 번만)
cd android
./gradlew clean
cd ..
```

### 4. 백엔드 설정

```bash
cd backend

# 가상환경 생성 (Windows)
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r ..\requirements.txt
```

### 5. Firebase 설정 (필요한 경우)

Firebase 키 파일이 필요한 경우:
1. `backend/app/core/firebase-key.json` 파일을 프로젝트에 추가
2. 또는 환경 변수로 설정

**주의:** `firebase-key.json` 파일은 `.gitignore`에 포함되어 있으므로 Git에 올라가지 않습니다. 
다른 컴퓨터에서 사용하려면 별도로 전달받아야 합니다.

## 프로젝트 실행

### 백엔드 서버 실행

```bash
cd backend
.\run_server.bat
```

또는 수동 실행:
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 프론트엔드 실행

```bash
cd frontend
npm start
```

Android Studio에서 실행:
1. Android Studio 열기
2. `frontend/android` 폴더 열기
3. 기기/에뮬레이터 선택
4. Run 버튼 클릭

## 문제 해결

### Android SDK 경로 오류

`local.properties` 파일이 없거나 잘못된 경우:
1. Android Studio에서 프로젝트 열기
2. File > Project Structure > SDK Location 확인
3. `frontend/android/local.properties` 파일에 SDK 경로 추가:
   ```
   sdk.dir=C\:\\Users\\[사용자명]\\AppData\\Local\\Android\\Sdk
   ```

### Gradle 빌드 오류

```bash
cd frontend/android
./gradlew clean
./gradlew build
```

### Node 모듈 오류

```bash
cd frontend
rm -rf node_modules
npm install
```

### Python 가상환경 오류

```bash
cd backend
rm -rf venv
python -m venv venv
venv\Scripts\activate
pip install -r ..\requirements.txt
```

## 프로젝트 구조

```
deepfake-detector-app-main/
├── backend/              # Python FastAPI 백엔드
│   ├── app/
│   ├── venv/            # 가상환경 (Git에 포함 안됨)
│   └── run_server.bat   # 서버 실행 스크립트
├── frontend/            # React Native Expo 프론트엔드
│   ├── android/         # Android 네이티브 코드
│   │   ├── local.properties  # SDK 경로 (자동 생성)
│   │   └── app/
│   ├── src/             # React Native 소스 코드
│   └── package.json
└── requirements.txt     # Python 의존성
```

## 주의사항

1. **local.properties**: 이 파일은 각 컴퓨터마다 다르므로 Git에 포함되지 않습니다.
2. **firebase-key.json**: Firebase 키 파일은 보안상 Git에 포함되지 않습니다.
3. **node_modules**: npm install로 자동 설치됩니다.
4. **venv**: Python 가상환경은 각 컴퓨터에서 새로 생성해야 합니다.

## 빠른 시작 체크리스트

- [ ] Git 클론 완료
- [ ] Android Studio 설치 및 SDK 경로 확인
- [ ] Node.js 설치 확인 (`node --version`)
- [ ] Python 설치 확인 (`python --version`)
- [ ] `frontend/android/local.properties` 파일 확인/생성
- [ ] `cd frontend && npm install` 실행
- [ ] `cd backend && python -m venv venv` 실행
- [ ] `cd backend && venv\Scripts\activate && pip install -r ..\requirements.txt` 실행
- [ ] 백엔드 서버 실행 테스트
- [ ] 프론트엔드 실행 테스트

## 추가 도움말

문제가 발생하면 다음을 확인하세요:
- Android Studio의 SDK Manager에서 필요한 SDK 설치 여부
- 환경 변수 설정 (JAVA_HOME, ANDROID_HOME 등)
- 방화벽 설정 (백엔드 서버 포트 8000)

