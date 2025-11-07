# 딥페이크 탐지 앱 - 흐름도

## 📱 전체 앱 흐름

```
┌─────────────────┐
│   앱 시작        │
│  (HomeScreen)   │
└────────┬────────┘
         │
         ▼
    ┌─────────┐
    │ 메뉴 선택 │
    └────┬────┘
         │
    ┌────┴──────────────────────┐
    │                           │
    ▼                           ▼
┌──────────┐              ┌──────────────┐
│ 위젯 제어 │              │ 직접 녹화/업로드 │
│  (Widget)│              │  (RecordScreen)│
└────┬─────┘              └──────┬───────┘
     │                           │
     ▼                           │
┌─────────────────┐              │
│ Switch ON! 클릭 │              │
│ 권한 요청        │              │
└────┬────────────┘              │
     │                           │
     ▼                           │
┌─────────────────┐              │
│ 홈 화면으로 이동  │              │
│ 플로팅 버튼 표시  │              │
└────┬────────────┘              │
     │                           │
     ▼                           │
┌─────────────────┐              │
│ 녹화 버튼 클릭   │              │
│ MediaProjection │              │
│ 권한 요청        │              │
└────┬────────────┘              │
     │                           │
     ▼                           │
┌─────────────────┐              │
│ 화면 녹화 시작   │◄─────────────┘
│ (최대 15초)     │
└────┬────────────┘
     │
     ├─ 15초 경과 ──▶ 자동 종료 + Toast 알림
     │
     └─ 수동 종료 ──▶ 완료 알림
         │
         ▼
┌─────────────────┐
│ 녹화 완료 팝업   │
│ "분석하시겠습니까?"│
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ 분석 중 모달     │
│ "분석 중..."     │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ 백엔드 API 호출  │
│ /analyze-video/ │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ 딥페이크 확률 계산│
│ (영상만, 정수%)  │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ 분석 완료 모달   │
│ "딥페이크: 65%"  │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ 결과 화면 이동   │
│ (ResultScreen)  │
└─────────────────┘
```

## 🎯 주요 화면 흐름

```
HomeScreen
    │
    ├─▶ WidgetControl (위젯 제어)
    │       │
    │       └─▶ 플로팅 위젯 시작 → 녹화 → 분석
    │
    ├─▶ Record (직접 녹화/업로드)
    │       │
    │       ├─▶ 카메라 녹화
    │       ├─▶ 앨범에서 선택
    │       │
    │       └─▶ 분석 → Result
    │
    ├─▶ Upload (영상 업로드)
    │       │
    │       └─▶ 분석 → Result
    │
    └─▶ Metrics (지표)
```

## 🔄 플로팅 위젯 녹화 흐름 (상세)

```
WidgetControlScreen
    │
    ├─▶ "Switch ON!" 클릭
    │       │
    │       ├─▶ 권한 없음 → 설정 화면 이동
    │       │       │
    │       │       └─▶ 권한 허용 → 위젯 시작
    │       │
    │       └─▶ 권한 있음 → 바로 위젯 시작
    │
    ▼
홈 화면 (다른 앱 사용 중)
    │
    ▼
플로팅 버튼 표시
    │
    ├─▶ 버튼 클릭 → 메뉴 확장
    │       │
    │       ├─▶ "녹화" 클릭
    │       │       │
    │       │       ├─▶ MainActivity로 Intent 전송
    │       │       │
    │       │       ├─▶ MediaProjection 권한 요청
    │       │       │
    │       │       ├─▶ FloatingService로 녹화 시작
    │       │       │
    │       │       ├─▶ 15초 타이머 시작
    │       │       │
    │       │       ├─▶ 화면 녹화 진행
    │       │       │
    │       │       └─▶ 15초 경과 → 자동 종료
    │       │               │
    │       │               ├─▶ Toast: "녹화 완료 (15초 자동 종료)"
    │       │               │
    │       │               └─▶ Notification: "녹화 완료"
    │       │
    │       ├─▶ "캡처" 클릭 → 화면 캡처
    │       │
    │       └─▶ "종료" 클릭 → 위젯 종료
    │
    ▼
녹화 완료 이벤트 발생
    │
    ├─▶ React Native로 이벤트 전송
    │
    ├─▶ MainActivity 포그라운드로 이동
    │
    └─▶ WidgetControlScreen에서 팝업 표시
            │
            ├─▶ "취소" → 팝업 닫기
            │
            └─▶ "분석하기" → RecordScreen 이동
                    │
                    └─▶ 자동 분석 시작
```

## 📊 분석 프로세스 흐름

```
RecordScreen
    │
    ├─▶ recordedVideoPath 받음
    │
    ├─▶ showAnalysisProgress = true
    │
    ▼
분석 중 모달 표시
    │
    ▼
handleAnalyze() 실행
    │
    ├─▶ setAnalyzing(true)
    │
    ├─▶ analyzeVideo() API 호출
    │       │
    │       ├─▶ FormData 생성
    │       │
    │       ├─▶ POST /analyze-video/
    │       │
    │       └─▶ timeline 데이터 받음
    │
    ▼
딥페이크 확률 계산
    │
    ├─▶ suspect 비율 계산
    │
    ├─▶ score 평균 계산
    │
    ├─▶ 두 값 평균
    │
    └─▶ Math.round()로 정수% 변환
    │
    ▼
분석 완료 모달
    │
    ├─▶ "딥페이크 확률: XX%" 표시
    │
    ├─▶ "취소" → 모달 닫기
    │
    └─▶ "결과 보기" → ResultScreen 이동
            │
            └─▶ timeline과 함께 전달
```

## 🔐 권한 흐름

```
앱 시작
    │
    ├─▶ 카메라 권한 요청 (RecordScreen)
    │
    ├─▶ 마이크 권한 요청 (RecordScreen)
    │
    └─▶ 다른 앱 위에 표시 권한 (WidgetControl)
            │
            ├─▶ 권한 없음 → 설정 화면 이동
            │
            └─▶ 권한 허용 → 위젯 사용 가능
                    │
                    └─▶ 녹화 시작 시 MediaProjection 권한 요청
                            │
                            └─▶ 시스템 다이얼로그 표시
                                    │
                                    └─▶ 허용 → 녹화 시작
```

## 📝 주요 데이터 흐름

```
녹화 파일
    │
    ├─▶ 경로: /storage/.../recordings/recording_*.mp4
    │
    ├─▶ FloatingService → onRecordingComplete 이벤트
    │
    ├─▶ React Native 이벤트 리스너
    │
    ├─▶ WidgetControlScreen 팝업
    │
    └─▶ RecordScreen → handleAnalyze()
            │
            └─▶ FormData → 백엔드 API
                    │
                    └─▶ timeline 반환
                            │
                            └─▶ 딥페이크 확률 계산
                                    │
                                    └─▶ ResultScreen 표시
```

## ⚡ 주요 상태 관리

```
WidgetControlScreen
    ├─ hasOverlay: boolean (권한 상태)
    ├─ serviceOn: boolean (위젯 실행 상태)
    └─ recording: boolean (녹화 중 상태)

RecordScreen
    ├─ analyzing: boolean (분석 중 상태)
    ├─ analysisResult: { percentage, timeline } | null
    └─ busy: boolean (처리 중 상태)

FloatingService (Android)
    ├─ isRecording: boolean
    ├─ mediaProjection: MediaProjection?
    └─ recordingHandler: Handler? (15초 타이머)
```

## 🎬 화면 전환 시나리오

### 시나리오 1: 플로팅 위젯을 통한 녹화
```
Home → WidgetControl → (홈 화면) → 플로팅 위젯 → 녹화 
→ Record → 분석 → Result
```

### 시나리오 2: 직접 카메라 녹화
```
Home → Record → 카메라 녹화 → 분석 → Result
```

### 시나리오 3: 앨범에서 영상 선택
```
Home → Record → 앨범 선택 → 분석 → Result
```

---
*마지막 업데이트: 2024-11-03*











