# Cursor 개발 시작 프롬프트

이 프로젝트를 Cursor에서 열었을 때, AI에게 다음 프롬프트를 제공하세요:

---

## 프로젝트 컨텍스트

이 프로젝트는 **딥페이크 탐지 앱**입니다.

### 기술 스택
- **프론트엔드**: React Native + Expo (TypeScript)
- **백엔드**: Python FastAPI
- **네이티브**: Android (Kotlin) - 플로팅 위젯

### 프로젝트 구조
```
deepfake-detector-app-main/
├── backend/              # Python FastAPI 백엔드
│   ├── app/api/         # API 엔드포인트
│   ├── app/services/    # 딥페이크 탐지 로직
│   └── run_server.bat   # 서버 실행
├── frontend/            # React Native Expo
│   ├── android/         # Android 네이티브
│   │   └── app/src/main/java/com/anonymous/deepfakeapp/
│   │       └── FloatingService.kt  # 플로팅 위젯
│   └── src/             # React Native 소스
└── requirements.txt
```

### 현재 플로팅 위젯 상태

**위젯 구성:**
- 메인 버튼: 60dp, `camera_icon.png` (눈 모양 아이콘), 중앙 배치
- 녹화 버튼: 50dp, `icon_record.png`, 상단 중앙 (bottomMargin: 80dp)
- 캡처 버튼: 50dp, `icon_capture.png`, 왼쪽 중앙 (marginEnd: 80dp)
- 종료 버튼: 50dp, `icon_close.png`, 오른쪽 중앙 (marginStart: 80dp)

**아이콘 위치:** `frontend/android/app/src/main/res/drawable/`

**주요 파일:** `frontend/android/app/src/main/java/com/anonymous/deepfakeapp/FloatingService.kt`

### 주요 기능
1. 비디오 딥페이크 탐지 (MesoNet)
2. 오디오 딥페이크 탐지 (Whisper)
3. Android 플로팅 위젯 (화면 녹화/캡처)
4. 리포트 생성

### 실행 방법
- 백엔드: `cd backend && .\run_server.bat`
- 프론트엔드: `cd frontend && npm start`
- Android: Android Studio에서 `frontend/android` 열기

### 최근 변경사항
- 플로팅 위젯 아이콘 변경 (camera_icon.png)
- 버튼 아이콘 변경 (icon_capture.png, icon_close.png)
- 버튼 크기: 메인 60dp, 서브 50dp
- 텍스트 레이블 제거

### 개발 시 참고
- 위젯 크기 변경: `FloatingService.kt`의 `size` 변수
- 아이콘 변경: `drawable` 폴더에 PNG 추가 후 `getIdentifier()` 사용
- 버튼 위치: `layoutParams`의 `gravity`와 `margin` 조정
- 메뉴 토글: `toggleMenu()` 함수의 `isExpanded` 상태

---

**이제 이 프로젝트에 대한 모든 정보를 이해했습니다. 어떤 작업을 도와드릴까요?**




