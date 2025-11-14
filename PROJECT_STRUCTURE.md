# 📁 REALGUARD 프로젝트 - 파일 구조 및 패키지 가이드

## 📋 목차
1. [전체 프로젝트 구조](#1-전체-프로젝트-구조)
2. [프론트엔드 구조](#2-프론트엔드-구조)
3. [백엔드 구조](#3-백엔드-구조)
4. [필요한 패키지 목록](#4-필요한-패키지-목록)
5. [향후 추가될 파일](#5-향후-추가될-파일)

---

## 1. 전체 프로젝트 구조

```
deepfake-detector-app-main/
├── frontend/                          # React Native + Expo 프론트엔드
│   ├── android/                       # Android 네이티브 코드
│   │   ├── app/
│   │   │   ├── src/main/
│   │   │   │   ├── java/com/anonymous/deepfakeapp/
│   │   │   │   │   ├── MainActivity.kt
│   │   │   │   │   ├── MainApplication.kt
│   │   │   │   │   ├── FloatingWidgetModule.kt
│   │   │   │   │   ├── FloatingWidgetPackage.kt
│   │   │   │   │   └── FloatingService.kt
│   │   │   │   ├── res/               # 리소스 파일
│   │   │   │   └── AndroidManifest.xml
│   │   │   └── build.gradle
│   │   ├── gradle/
│   │   ├── gradlew
│   │   ├── gradlew.bat
│   │   ├── gradle.properties
│   │   └── settings.gradle
│   ├── src/                           # 소스 코드
│   │   ├── api/                       # API 통신
│   │   ├── assets/                    # 이미지, 폰트 등
│   │   ├── components/                # 재사용 컴포넌트
│   │   ├── hooks/                     # Custom Hooks
│   │   ├── navigation/                # 네비게이션 설정
│   │   ├── screens/                   # 화면 컴포넌트
│   │   ├── services/                  # 비즈니스 로직 서비스
│   │   ├── types/                     # TypeScript 타입 정의
│   │   └── utils/                     # 유틸리티 함수
│   ├── app.json                       # Expo 설정
│   ├── package.json                   # NPM 패키지
│   ├── tsconfig.json                  # TypeScript 설정
│   ├── babel.config.js                # Babel 설정
│   └── index.js                       # 진입점
│
├── backend/                           # Python FastAPI 백엔드
│   ├── app/
│   │   ├── api/                       # API 엔드포인트
│   │   │   └── endpoints/
│   │   ├── core/                      # 핵심 설정
│   │   ├── models/                    # 데이터 모델
│   │   ├── services/                  # 비즈니스 로직
│   │   ├── utils/                     # 유틸리티 함수
│   │   └── main.py                    # FastAPI 앱 진입점
│   ├── temp/                          # 임시 파일 저장
│   ├── weights/                       # AI 모델 가중치
│   ├── venv/                          # Python 가상환경
│   ├── requirements.txt               # Python 패키지
│   └── run_server.bat                 # 서버 실행 스크립트
│
├── docs/                              # 문서 (선택사항)
│   ├── REALGUARD_PRD_REVISED.md
│   ├── FIREBASE_REQUIREMENTS.md
│   ├── REQUIRED_PACKAGES.md
│   └── PROJECT_STRUCTURE.md
│
└── README.md                          # 프로젝트 설명
```

---

## 2. 프론트엔드 구조

### 2.1 현재 구조 (구현 완료)

```
frontend/src/
├── api/                               # API 통신 로직
│   ├── index.ts                       # API 기본 함수
│   ├── firebase.ts                    # Firebase 설정
│   └── uploadToFirebase.ts            # Firebase Storage 업로드
│
├── assets/                            # 정적 리소스
│   ├── images/
│   │   ├── home-background.png
│   │   └── login.bar.background.png
│   └── fonts/                         # 폰트 파일 (선택사항)
│
├── components/                        # 재사용 컴포넌트
│   ├── CameraView.tsx                 # 카메라 뷰 컴포넌트
│   ├── VideoPlayer.tsx                # 비디오 플레이어
│   ├── Timeline.tsx                   # 타임라인 컴포넌트
│   ├── VoiceResult.tsx                # 음성 분석 결과
│   └── CommunityList.tsx              # 커뮤니티 리스트
│
├── hooks/                             # Custom Hooks
│   └── useAuth.ts                     # 인증 관련 Hook (향후 구현)
│
├── navigation/                        # 네비게이션 설정
│   └── AppNavigator.tsx               # 메인 네비게이터
│
├── screens/                           # 화면 컴포넌트
│   ├── HomeScreen.tsx                 # 홈 화면
│   ├── RecordScreen.tsx               # 녹화 화면
│   ├── UploadScreen.tsx               # 업로드 화면
│   ├── ResultScreen.tsx               # 결과 화면
│   ├── ReportScreen.tsx               # 신고 화면
│   ├── MetricsScreen.tsx              # 지표 화면
│   ├── WidgetControlScreen.tsx        # 위젯 제어 화면
│   ├── CommunityScreen.tsx            # 커뮤니티 목록
│   ├── CommunityWriteScreen.tsx       # 커뮤니티 작성
│   ├── CommunityDetailScreen.tsx      # 커뮤니티 상세
│   ├── CameraSmokeTest.tsx            # 카메라 테스트
│   └── CameraDiag.tsx                 # 카메라 진단
│
├── services/                          # 비즈니스 로직 서비스 (향후 구현)
│   ├── authService.ts                 # 인증 서비스
│   ├── userService.ts                 # 사용자 서비스
│   ├── rewardService.ts               # 리워드 서비스
│   └── metadataService.ts             # 메타데이터 서비스
│
├── types/                             # TypeScript 타입 정의
│   ├── index.ts                       # 공통 타입
│   ├── user.ts                        # 사용자 타입
│   └── analysis.ts                    # 분석 결과 타입
│
└── utils/                             # 유틸리티 함수
    ├── index.ts                       # 공통 유틸리티
    └── anonymization.ts               # 익명화 유틸리티 (향후 구현)
```

### 2.2 향후 추가될 파일 (PRD 요구사항)

```
frontend/src/
├── services/
│   ├── authService.ts                 # ✅ 새로 생성 필요
│   │   - signInAnonymously()
│   │   - signOut()
│   │   - onAuthStateChange()
│   │
│   ├── userService.ts                 # ✅ 새로 생성 필요
│   │   - createUserProfile()
│   │   - getUserProfile()
│   │   - updateUserProfile()
│   │
│   ├── rewardService.ts               # ✅ 새로 생성 필요
│   │   - getRewardPoints()
│   │   - getBadges()
│   │   - getRewardHistory()
│   │
│   └── metadataService.ts             # ✅ 새로 생성 필요
│       - extractMetadata()
│       - labelVideoMetadata()
│
├── screens/
│   ├── AuthScreen.tsx                 # ✅ 새로 생성 필요 (로그인/회원가입)
│   ├── ProfileScreen.tsx              # ✅ 새로 생성 필요 (프로필/리워드)
│   ├── RewardScreen.tsx               # ✅ 새로 생성 필요 (리워드 상세)
│   └── DashboardScreen.tsx            # ✅ 새로 생성 필요 (대시보드)
│
├── components/
│   ├── RewardBadge.tsx                # ✅ 새로 생성 필요 (뱃지 컴포넌트)
│   ├── PointsDisplay.tsx              # ✅ 새로 생성 필요 (포인트 표시)
│   ├── ChartView.tsx                  # ✅ 새로 생성 필요 (차트 컴포넌트)
│   └── ConsentModal.tsx               # ✅ 새로 생성 필요 (동의 모달)
│
└── utils/
    └── anonymization.ts               # ✅ 새로 생성 필요
        - generateAnonymousId()
        - decryptAnonymousId()
```

---

## 3. 백엔드 구조

### 3.1 현재 구조 (구현 완료)

```
backend/app/
├── api/
│   └── endpoints/
│       ├── __init__.py
│       ├── analyze_video.py           # 비디오 분석 엔드포인트
│       ├── analyze_video_optimized.py # 최적화된 분석
│       ├── analysis_server.py         # 분석 서버
│       ├── submit_report.py           # 리포트 제출
│       ├── report_download.py         # 리포트 다운로드
│       ├── model_guide.py             # 모델 가이드
│       ├── model_metrics.py           # 모델 지표
│       ├── dataset_export.py          # 데이터셋 내보내기
│       ├── get_result.py              # 결과 조회
│       └── community.py               # 커뮤니티 API
│
├── core/
│   ├── __init__.py
│   ├── config.py                      # 설정 파일
│   ├── firebase.py                    # Firebase 설정
│   └── firebase-key.json              # Firebase 키 (보안)
│
├── models/
│   ├── __init__.py
│   └── schemas.py                     # Pydantic 스키마
│
├── services/
│   ├── __init__.py
│   ├── deepfake_detector.py           # 딥페이크 탐지 서비스
│   ├── deepfake_detector_optimized.py # 최적화된 탐지
│   ├── mesonet_backend.py             # MesoNet 백엔드
│   ├── model_efficientnet.py          # EfficientNet 모델
│   ├── model_mesonet.py               # MesoNet 모델
│   ├── model_ensemble.py              # 앙상블 모델
│   ├── video_processing.py            # 비디오 처리
│   ├── video_processing_optimized.py  # 최적화된 비디오 처리
│   ├── audio_processing.py            # 오디오 처리
│   ├── parallel_processing_optimized.py # 병렬 처리
│   ├── metrics.py                     # 지표 계산
│   └── report_generator.py            # 리포트 생성
│
├── utils/
│   ├── __init__.py
│   └── helpers.py                     # 헬퍼 함수
│
└── main.py                            # FastAPI 앱 진입점
```

### 3.2 향후 추가될 파일 (PRD 요구사항)

```
backend/app/
├── api/endpoints/
│   ├── auth.py                        # ✅ 새로 생성 필요
│   │   - POST /auth/signin-anonymous
│   │   - POST /auth/signout
│   │   - GET /auth/me
│   │
│   ├── user.py                        # ✅ 새로 생성 필요
│   │   - GET /user/profile
│   │   - PUT /user/profile
│   │   - GET /user/contributions
│   │
│   ├── reward.py                      # ✅ 새로 생성 필요
│   │   - GET /reward/points
│   │   - GET /reward/badges
│   │   - GET /reward/history
│   │   - POST /reward/calculate
│   │
│   └── metadata.py                    # ✅ 새로 생성 필요
│       - POST /metadata/extract
│       - POST /metadata/label
│
├── services/
│   ├── user_service.py                # ✅ 새로 생성 필요
│   │   - create_user_profile()
│   │   - get_user_profile()
│   │   - update_user_profile()
│   │   - anonymize_user_id()
│   │
│   ├── reward_service.py              # ✅ 새로 생성 필요
│   │   - calculate_reward_points()
│   │   - award_badges()
│   │   - get_reward_history()
│   │   - check_badge_eligibility()
│   │
│   ├── metadata_service.py            # ✅ 새로 생성 필요
│   │   - extract_video_metadata()
│   │   - extract_audio_metadata()
│   │   - label_lighting()
│   │   - label_angle()
│   │   - label_expression()
│   │
│   ├── anonymization_service.py       # ✅ 새로 생성 필요
│   │   - generate_anonymous_id()
│   │   - decrypt_anonymous_id()
│   │   - encrypt_user_data()
│   │   - decrypt_user_data()
│   │
│   └── analytics_service.py           # ✅ 새로 생성 필요
│       - calculate_model_improvement()
│       - generate_user_statistics()
│       - create_visualization_data()
│
├── models/
│   ├── user_models.py                 # ✅ 새로 생성 필요
│   │   - UserProfile
│   │   - UserContribution
│   │   - RewardHistory
│   │
│   └── metadata_models.py             # ✅ 새로 생성 필요
│       - VideoMetadata
│       - AudioMetadata
│       - LabeledMetadata
│
└── utils/
    ├── encryption.py                  # ✅ 새로 생성 필요
    │   - encrypt_aes256()
    │   - decrypt_aes256()
    │
    └── mediapipe_utils.py             # ✅ 새로 생성 필요
        - detect_face_landmarks()
        - detect_expression()
        - detect_lighting()
```

---

## 4. 필요한 패키지 목록

### 4.1 Frontend 패키지 (`package.json`)

#### 현재 설치된 패키지
```json
{
  "dependencies": {
    "@react-navigation/drawer": "^6.7.2",
    "@react-navigation/native": "^6.1.8",
    "@react-navigation/stack": "^6.3.20",
    "axios": "^1.6.0",
    "expo": "~51.0.0",
    "expo-av": "~14.0.7",
    "expo-camera": "~15.0.16",
    "expo-document-picker": "~12.0.0",
    "expo-file-system": "~17.0.1",
    "expo-image-picker": "~15.1.0",
    "firebase": "^10.7.1",
    "react": "18.2.0",
    "react-native": "0.74.5",
    "react-native-gesture-handler": "~2.16.1",
    "react-native-reanimated": "~3.10.1",
    "react-native-safe-area-context": "4.10.5",
    "react-native-screens": "3.31.1"
  },
  "devDependencies": {
    "@types/react": "~18.2.0",
    "typescript": "~5.3.3"
  }
}
```

#### 향후 추가 필요 패키지

##### Phase 1: 인증 및 사용자 관리
```bash
npm install @react-native-async-storage/async-storage
```

##### Phase 2: 암호화 및 익명화
```bash
npm install crypto-js uuid
npm install --save-dev @types/crypto-js @types/uuid
```

##### Phase 3: 시각화 및 차트
```bash
# 옵션 1: React Native 전용 차트
npm install react-native-chart-kit react-native-svg

# 옵션 2: WebView 기반 Plotly
npm install react-native-webview
```

##### Phase 4: 추가 유틸리티
```bash
# 날짜/시간 처리
npm install date-fns

# 폼 관리 (선택사항)
npm install react-hook-form

# 상태 관리 (선택사항)
npm install zustand
# 또는
npm install @reduxjs/toolkit react-redux
```

#### 완전한 `package.json` (향후)
```json
{
  "name": "realguard-app",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "expo start --dev-client",
    "start:expo": "expo start",
    "android": "expo run:android",
    "ios": "expo run:ios",
    "web": "expo start --web"
  },
  "dependencies": {
    "@react-navigation/drawer": "^6.7.2",
    "@react-navigation/native": "^6.1.8",
    "@react-navigation/stack": "^6.3.20",
    "@react-native-async-storage/async-storage": "^1.21.0",
    "axios": "^1.6.0",
    "crypto-js": "^4.2.0",
    "date-fns": "^3.0.0",
    "expo": "~51.0.0",
    "expo-av": "~14.0.7",
    "expo-camera": "~15.0.16",
    "expo-document-picker": "~12.0.0",
    "expo-file-system": "~17.0.1",
    "expo-image-picker": "~15.1.0",
    "firebase": "^10.7.1",
    "react": "18.2.0",
    "react-native": "0.74.5",
    "react-native-chart-kit": "^6.12.0",
    "react-native-gesture-handler": "~2.16.1",
    "react-native-reanimated": "~3.10.1",
    "react-native-safe-area-context": "4.10.5",
    "react-native-screens": "3.31.1",
    "react-native-svg": "^13.14.0",
    "react-native-webview": "^13.6.0",
    "uuid": "^9.0.1"
  },
  "devDependencies": {
    "@types/crypto-js": "^4.2.1",
    "@types/react": "~18.2.0",
    "@types/uuid": "^9.0.7",
    "typescript": "~5.3.3"
  }
}
```

### 4.2 Backend 패키지 (`requirements.txt`)

#### 현재 설치된 패키지
```txt
# FastAPI and web server
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# AI/ML models and processing
torch>=2.0.0
transformers>=4.35.0
sentence-transformers>=2.2.2
whisper>=1.1.10
speechrecognition>=3.10.0
librosa>=0.10.1
soundfile>=0.12.1
scikit-learn>=1.3.0
tensorflow-cpu>=2.15.0,<3.0.0
mediapipe>=0.10.0

# Image and video processing
opencv-python>=4.8.0
Pillow>=10.0.0

# Firebase integration
firebase-admin>=6.4.0

# Report generation
reportlab>=4.0.0
openpyxl>=3.1.0

# System monitoring and optimization
psutil>=5.9.0

# Utilities
pydantic>=2.4.0
aiofiles>=23.2.0
```

#### 향후 추가 필요 패키지

##### Phase 1: 암호화 및 보안
```txt
# AES256 암호화
cryptography>=41.0.0
pycryptodome>=3.19.0
```

##### Phase 2: 데이터 시각화
```txt
# Plotly를 통한 시각화
plotly>=5.18.0
kaleido>=0.2.1  # Plotly 이미지 내보내기용 (선택사항)
```

##### Phase 3: 데이터 분석
```txt
# 데이터 분석 (이미 pandas는 설치되어 있을 수 있음)
pandas>=2.0.0
numpy>=1.24.0
```

##### Phase 4: 추가 유틸리티
```txt
# 환경 변수 관리
python-dotenv>=1.0.0

# 로깅
loguru>=0.7.0

# 날짜/시간 처리
python-dateutil>=2.8.2
```

#### 완전한 `requirements.txt` (향후)
```txt
# FastAPI and web server
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# AI/ML models and processing
torch>=2.0.0
transformers>=4.35.0
sentence-transformers>=2.2.2
whisper>=1.1.10
speechrecognition>=3.10.0
librosa>=0.10.1
soundfile>=0.12.1
scikit-learn>=1.3.0
tensorflow-cpu>=2.15.0,<3.0.0
mediapipe>=0.10.0

# Image and video processing
opencv-python>=4.8.0
Pillow>=10.0.0

# Firebase integration
firebase-admin>=6.4.0

# Report generation
reportlab>=4.0.0
openpyxl>=3.1.0

# System monitoring and optimization
psutil>=5.9.0

# Utilities
pydantic>=2.4.0
aiofiles>=23.2.0

# ===== 향후 추가 패키지 =====

# 암호화 및 보안
cryptography>=41.0.0
pycryptodome>=3.19.0

# 데이터 시각화
plotly>=5.18.0
kaleido>=0.2.1

# 데이터 분석
pandas>=2.0.0
numpy>=1.24.0

# 환경 변수 관리
python-dotenv>=1.0.0

# 로깅
loguru>=0.7.0

# 날짜/시간 처리
python-dateutil>=2.8.2
```

---

## 5. 향후 추가될 파일

### 5.1 Frontend 파일 생성 체크리스트

#### Phase 1: 인증 시스템
- [ ] `src/services/authService.ts`
- [ ] `src/services/userService.ts`
- [ ] `src/screens/AuthScreen.tsx`
- [ ] `src/components/ConsentModal.tsx`
- [ ] `src/hooks/useAuth.ts`

#### Phase 2: 리워드 시스템
- [ ] `src/services/rewardService.ts`
- [ ] `src/screens/ProfileScreen.tsx`
- [ ] `src/screens/RewardScreen.tsx`
- [ ] `src/components/RewardBadge.tsx`
- [ ] `src/components/PointsDisplay.tsx`

#### Phase 3: 메타데이터 및 시각화
- [ ] `src/services/metadataService.ts`
- [ ] `src/screens/DashboardScreen.tsx`
- [ ] `src/components/ChartView.tsx`
- [ ] `src/utils/anonymization.ts`

#### Phase 4: 타입 정의
- [ ] `src/types/user.ts`
- [ ] `src/types/reward.ts`
- [ ] `src/types/metadata.ts`

### 5.2 Backend 파일 생성 체크리스트

#### Phase 1: 인증 및 사용자 관리
- [ ] `app/api/endpoints/auth.py`
- [ ] `app/api/endpoints/user.py`
- [ ] `app/services/user_service.py`
- [ ] `app/services/anonymization_service.py`
- [ ] `app/models/user_models.py`
- [ ] `app/utils/encryption.py`

#### Phase 2: 리워드 시스템
- [ ] `app/api/endpoints/reward.py`
- [ ] `app/services/reward_service.py`

#### Phase 3: 메타데이터 처리
- [ ] `app/api/endpoints/metadata.py`
- [ ] `app/services/metadata_service.py`
- [ ] `app/models/metadata_models.py`
- [ ] `app/utils/mediapipe_utils.py`

#### Phase 4: 분석 및 시각화
- [ ] `app/services/analytics_service.py`

---

## 6. 설치 명령어

### Frontend 패키지 설치
```bash
cd frontend

# 기본 패키지 (이미 설치됨)
npm install

# Phase 1: 인증
npm install @react-native-async-storage/async-storage

# Phase 2: 암호화
npm install crypto-js uuid
npm install --save-dev @types/crypto-js @types/uuid

# Phase 3: 시각화
npm install react-native-chart-kit react-native-svg react-native-webview

# Phase 4: 유틸리티
npm install date-fns
```

### Backend 패키지 설치
```bash
cd backend

# 가상환경 활성화
.\venv\Scripts\activate  # Windows
# 또는
source venv/bin/activate  # Linux/Mac

# 기본 패키지 (이미 설치됨)
pip install -r requirements.txt

# Phase 1: 암호화
pip install cryptography>=41.0.0 pycryptodome>=3.19.0

# Phase 2: 시각화
pip install plotly>=5.18.0 kaleido>=0.2.1

# Phase 3: 데이터 분석
pip install pandas>=2.0.0 numpy>=1.24.0

# Phase 4: 유틸리티
pip install python-dotenv>=1.0.0 loguru>=0.7.0 python-dateutil>=2.8.2
```

---

## 7. 환경 변수 설정

### Frontend (`.env`)
```env
# API
API_BASE_URL=http://localhost:8000

# Firebase (이미 firebase.ts에 설정되어 있음)
# FIREBASE_API_KEY=...
# FIREBASE_AUTH_DOMAIN=...
# FIREBASE_PROJECT_ID=...
# FIREBASE_STORAGE_BUCKET=...

# 암호화
ANONYMIZATION_SECRET_KEY=your-secret-key-here-change-in-production
```

### Backend (`.env`)
```env
# 서버 설정
HOST=0.0.0.0
PORT=8000

# Firebase
FIREBASE_PROJECT_ID=deepfake-fc59d
FIREBASE_STORAGE_BUCKET=deepfake-fc59d.firebasestorage.app

# 암호화
ANONYMIZATION_SECRET_KEY=your-secret-key-here-change-in-production

# AI 모델 경로
MODEL_WEIGHTS_PATH=./weights
```

---

## 8. 참고 사항

### 파일 명명 규칙
- **TypeScript/React**: PascalCase (컴포넌트), camelCase (함수/변수)
- **Python**: snake_case (함수/변수), PascalCase (클래스)
- **파일명**: 
  - Frontend: PascalCase (컴포넌트), camelCase (유틸리티)
  - Backend: snake_case

### 디렉토리 구조 원칙
- **관심사 분리**: 기능별로 디렉토리 분리
- **재사용성**: 공통 컴포넌트/유틸리티는 별도 디렉토리
- **확장성**: 향후 기능 추가를 고려한 구조

### 보안 주의사항
- `firebase-key.json`은 절대 Git에 커밋하지 않기
- `.env` 파일은 `.gitignore`에 추가
- 암호화 키는 환경 변수로 관리

---

## 📝 업데이트 이력

- **2025-11-07**: 초기 파일 구조 및 패키지 목록 작성
  - 현재 구조 파악
  - PRD 요구사항 반영
  - 향후 추가될 파일 명시





