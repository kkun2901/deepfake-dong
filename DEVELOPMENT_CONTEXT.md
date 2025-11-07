# 딥페이크 탐지 앱 개발 컨텍스트

## 📋 프로젝트 개요
- **프로젝트명**: 딥페이크 탐지 앱 (Deepfake Detector App)
- **프론트엔드**: React Native + Expo (TypeScript)
- **백엔드**: Python FastAPI
- **주요 기능**: 비디오 딥페이크 탐지 및 분석

## 🗂️ 프로젝트 구조
```
deepfake-detector-app-main/
├── frontend/              # React Native Expo 앱
│   ├── src/
│   │   ├── screens/      # 화면 컴포넌트
│   │   ├── components/   # 재사용 컴포넌트
│   │   ├── api/          # API 통신 로직
│   │   ├── navigation/   # 네비게이션 설정
│   │   └── assets/       # 이미지/리소스
│   └── package.json
├── backend/              # FastAPI 백엔드
│   ├── app/
│   │   ├── api/endpoints/
│   │   ├── core/         # Firebase 설정 등
│   │   ├── services/     # 비즈니스 로직
│   │   └── main.py
│   └── requirements.txt
└── README.md
```

## 🎯 주요 화면 (Navigation)
1. **HomeScreen** (`Home`) - 메인 랜딩 화면 (헤더 숨김)
2. **RecordScreen** (`Record`) - 비디오 녹화/앨범 선택
3. **UploadScreen** (`Upload`) - 비디오 업로드
4. **ResultScreen** (`Result`) - 분석 결과 표시
5. **ReportScreen** (`Report`) - 신고하기
6. **MetricsScreen** (`Metrics`) - 지표 보기
7. **WidgetControlScreen** (`WidgetControl`) - 위젯 제어

## 📱 현재 개발 상태

### ✅ 완료된 작업
1. **권한 설정 완료**
   - `app.json`에 Android 13+ 미디어 권한 추가 (`READ_MEDIA_VIDEO`, `READ_MEDIA_IMAGES`)
   - RecordScreen에서 동적 권한 요청 구현

2. **API 통신 설정**
   - 프론트엔드에서 Firebase 업로드 제거
   - 로컬 파일을 직접 백엔드로 전송 (`FormData` 사용)
   - API Base URL: `http://10.0.2.2:8000` (Android 에뮬레이터용)
   - 엔드포인트: `POST /analyze-video/`

3. **HomeScreen 디자인 적용**
   - 검은색 배경 (`#000000`)
   - 상단: 프로필 아이콘 + 메뉴 버튼
   - 메인 메시지: "당신은 이제 허위 정보에 휘둘리지 않을거에요!"
   - 로고 이미지: `normal.logo.home.png`
   - 스포트라이트 효과: 올리브 그린 색상 (`rgba(85, 107, 47, 0.3)`)
   - SWITCH ON! 버튼: `login.bar.background.png` 배경 이미지 사용 → `WidgetControl` 화면으로 이동
   - 무료 가입 버튼: 노란색 배경 (`#FFD700`), 검은 글씨
   - 하단 얼굴 이미지: `people.home.png`

4. **RecordScreen 기능**
   - 카메라 녹화 / 앨범에서 선택 모드 전환
   - 미디어 라이브러리 권한 동적 요청
   - 분석 결과를 `ResultScreen`으로 전달

### 📦 현재 사용 중인 이미지 리소스
- `frontend/src/assets/normal.logo.home.png` - 로고
- `frontend/src/assets/login.bar.background.png` - SWITCH ON 버튼 배경
- `frontend/src/assets/people.home.png` - 하단 얼굴 이미지

### ⚠️ 중요 사항
- **SVG 파일은 사용하지 않음** - React Native에서는 PNG/JPG만 지원
- **ImageStyle 타입 사용**: 이미지 스타일에 `as ImageStyle` 캐스팅 필요
- **TypeScript 타입 정의**: `src/types/images.d.ts`에 이미지 모듈 타입 정의

## 🔧 개발 환경 설정

### 백엔드 실행
```bash
cd backend
# 가상환경 활성화 (Windows)
venv\Scripts\activate
uvicorn app.main:app --reload
```
- 백엔드 서버: `http://localhost:8000`
- Firebase 설정: `backend/app/core/firebase-key.json` 필요

### 프론트엔드 실행
```bash
cd frontend
npm install
npx expo start
```

### Android 에뮬레이터 접속
- API Base URL: `http://10.0.2.2:8000` (호스트 PC 접근용)

## 📝 주요 코드 위치

### API 통신
- **파일**: `frontend/src/api/index.ts`
- **함수**: `analyzeVideo(videoUri, userId)` - FormData로 비디오 업로드

### 화면 컴포넌트
- **HomeScreen**: `frontend/src/screens/HomeScreen.tsx`
- **RecordScreen**: `frontend/src/screens/RecordScreen.tsx`
- **네비게이션**: `frontend/src/navigation/AppNavigator.tsx`

### 스타일 가이드
- 배경색: `#000000` (검은색)
- 텍스트 색상: `#FFFFFF` (흰색)
- 강조 색상: `#FFD700` (노란색), `rgba(85, 107, 47, 0.3)` (올리브 그린)

## 🐛 알려진 이슈 및 해결책

1. **에뮬레이터에서 갤러리 비어있음**
   - 해결: ADB로 파일 푸시 또는 실제 기기 사용

2. **네트워크 에러 (Android 에뮬레이터)**
   - 해결: `API_BASE_URL`을 `http://10.0.2.2:8000`으로 설정

3. **이미지 타입 에러**
   - 해결: SVG 대신 PNG 사용, `ImageStyle` 타입 캐스팅

## 🚀 다음 개발 작업 제안
1. HomeScreen 디자인 완성 (디자인 이미지와 정확히 일치시키기)
2. RecordScreen → ResultScreen 데이터 전달 검증
3. 백엔드 API 연결 테스트
4. 에러 핸들링 강화

## 📌 개발 시 주의사항
- 모든 이미지는 PNG 형식 사용 (SVG 사용 불가)
- Android 권한은 `app.json`과 런타임 모두에서 설정 필요
- TypeScript 타입 정의 필수 (특히 이미지 import)
- 한국어 UI 텍스트 사용

