# 딥페이크 탐지 앱

딥페이크 비디오와 오디오를 탐지하는 통합 애플리케이션입니다.

## 🚀 빠른 시작

### 새 컴퓨터에서 설정하기

**다른 컴퓨터에서 처음 설정하는 경우:** [SETUP_NEW_COMPUTER.md](./SETUP_NEW_COMPUTER.md) 파일을 참고하세요.

### 기존 프로젝트 실행

#### 백엔드 서버 실행

**Windows:**
```bash
cd backend
.\run_server.bat
```

**수동 실행:**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

백엔드는 `http://localhost:8000`에서 실행됩니다.

#### 프론트엔드 실행

```bash
cd frontend
npm install  # 처음 한 번만
npm start
```

**Android Studio에서 실행:**
1. Android Studio 열기
2. `frontend/android` 폴더 열기
3. 기기/에뮬레이터 선택 후 Run

## 📁 프로젝트 구조

```
deepfake-detector-app-main/
├── backend/              # Python FastAPI 백엔드
│   ├── app/
│   │   ├── api/         # API 엔드포인트
│   │   ├── core/        # 설정 및 Firebase
│   │   ├── models/      # 데이터 모델
│   │   ├── services/    # 비즈니스 로직
│   │   └── utils/       # 유틸리티 함수
│   ├── venv/            # Python 가상환경 (Git 제외)
│   └── run_server.bat   # 서버 실행 스크립트
├── frontend/            # React Native Expo 프론트엔드
│   ├── android/         # Android 네이티브 코드
│   │   ├── app/         # Kotlin 소스 코드
│   │   └── local.properties  # SDK 경로 (자동 생성)
│   ├── src/
│   │   ├── api/         # API 클라이언트
│   │   ├── components/  # React 컴포넌트
│   │   ├── navigation/  # 네비게이션 설정
│   │   ├── screens/     # 화면 컴포넌트
│   │   └── types/       # TypeScript 타입
│   └── package.json
└── requirements.txt     # Python 의존성
```

## 🔧 사전 요구사항

- **Android Studio**: Android SDK 설치 필요
- **Node.js**: 18 이상
- **Python**: 3.8 이상
- **Git**: 프로젝트 클론용

## 📡 API 엔드포인트

- `POST /analyze-video` - 비디오 분석
- `GET /get-result/{video_id}` - 분석 결과 조회
- `POST /submit-report` - 리포트 제출
- `GET /download-report/{report_id}` - 리포트 다운로드

## 🛠 기술 스택

### 백엔드
- FastAPI
- PyTorch, Transformers
- Whisper (음성 인식)
- OpenCV (비디오 처리)

### 프론트엔드
- React Native + Expo
- TypeScript
- Firebase Storage
- React Navigation
- Android Native (Kotlin) - 플로팅 위젯

## 📝 주요 기능

- ✅ 비디오 딥페이크 탐지
- ✅ 오디오 딥페이크 탐지
- ✅ Android 플로팅 위젯
- ✅ 화면 녹화 및 캡처
- ✅ 리포트 생성 및 다운로드

## ⚠️ 주의사항

1. **local.properties**: Android SDK 경로는 각 컴퓨터마다 다르므로 Git에 포함되지 않습니다.
2. **firebase-key.json**: Firebase 키 파일은 보안상 Git에 포함되지 않습니다.
3. **venv**: Python 가상환경은 각 컴퓨터에서 새로 생성해야 합니다.

## 🔗 관련 문서

- [새 컴퓨터 설정 가이드](./SETUP_NEW_COMPUTER.md) - 다른 컴퓨터에서 처음 설정하는 방법
- [빌드 가이드](./BUILD_GUIDE.md) - 상세한 빌드 방법
- [Android Studio 빌드 가이드](./ANDROID_STUDIO_BUILD_GUIDE.md) - Android Studio 사용법

