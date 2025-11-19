# Cursor 개발 가이드

이 프로젝트는 딥페이크 탐지 앱입니다. Cursor에서 개발할 때 다음 사항을 참고하세요.

## 🎯 프로젝트 핵심 정보

### 기술 스택
- **프론트엔드**: React Native + Expo (TypeScript)
- **백엔드**: Python FastAPI
- **네이티브**: Android (Kotlin) - 플로팅 위젯

### 주요 파일 위치
- **플로팅 위젯**: `frontend/android/app/src/main/java/com/anonymous/deepfakeapp/FloatingService.kt`
- **React Native 앱**: `frontend/src/`
- **백엔드 API**: `backend/app/api/endpoints/`
- **아이콘 리소스**: `frontend/android/app/src/main/res/drawable/`

## 🔧 현재 플로팅 위젯 상태

### 버튼 구성
1. **메인 버튼** (중앙)
   - 크기: 60dp
   - 아이콘: `camera_icon.png` (눈 모양)
   - 기능: 메뉴 토글

2. **녹화 버튼** (상단 중앙)
   - 크기: 50dp
   - 아이콘: `icon_record.png`
   - 기능: 화면 녹화 시작/중지

3. **캡처 버튼** (왼쪽 중앙)
   - 크기: 50dp
   - 아이콘: `icon_capture.png`
   - 기능: 화면 캡처

4. **종료 버튼** (오른쪽 중앙)
   - 크기: 50dp
   - 아이콘: `icon_close.png`
   - 기능: 위젯 종료

### 레이아웃 설정
- 메인 버튼: `Gravity.CENTER`
- 녹화 버튼: `Gravity.CENTER_HORIZONTAL | Gravity.TOP`, `bottomMargin: 80dp`
- 캡처 버튼: `Gravity.CENTER_VERTICAL | Gravity.START`, `marginEnd: 80dp`
- 종료 버튼: `Gravity.CENTER_VERTICAL | Gravity.END`, `marginStart: 80dp`

## 📝 개발 시 주의사항

### 위젯 수정 시
- 버튼 크기 변경: `FloatingService.kt`에서 `val size = (XX * resources.displayMetrics.density).toInt()` 수정
- 아이콘 변경: `drawable` 폴더에 PNG 추가 후 `resources.getIdentifier("icon_name", "drawable", packageName)` 사용
- 버튼 위치 변경: `layoutParams`의 `gravity`와 `margin` 값 조정
- 메뉴 표시/숨김: `toggleMenu()` 함수의 `isExpanded` 상태 관리

### 코드 수정 후
1. Android Studio에서 `frontend/android` 프로젝트 열기
2. Gradle Sync 실행
3. 앱 재빌드 및 실행

### API 연동
- 백엔드 서버: `http://localhost:8000`
- API 클라이언트: `frontend/src/api/`
- 주요 엔드포인트:
  - `POST /analyze-video` - 비디오 분석
  - `GET /get-result/{video_id}` - 결과 조회

## 🚀 빠른 실행

### 백엔드
```bash
cd backend
.\run_server.bat
```

### 프론트엔드
```bash
cd frontend
npm start
```

### Android Studio
1. `frontend/android` 폴더 열기
2. Run 버튼 클릭

## 🐛 문제 해결

### 빌드 오류
```bash
cd frontend/android
./gradlew clean
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

## 📚 관련 문서
- `SETUP_NEW_COMPUTER.md` - 새 컴퓨터 설정 가이드
- `README.md` - 프로젝트 개요
- `BUILD_GUIDE.md` - 상세 빌드 가이드




