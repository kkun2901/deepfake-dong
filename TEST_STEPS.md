# 🧪 딥페이크 탐지 앱 테스트 절차 (에뮬레이터)

## 📋 사전 준비사항

### ✅ 확인 사항
- [x] 백엔드 서버 실행 중 (`uvicorn app.main:app --reload`)
- [x] Android Studio 에뮬레이터 실행 중
- [x] APK 빌드 완료
- [x] APK 설치 완료

---

## 🚀 테스트 순서

### STEP 1: 에뮬레이터 연결 확인

```powershell
# 터미널에서 실행
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices
```

**예상 결과:**
```
List of devices attached
emulator-5554   device
```

**문제 해결:** 아무것도 표시되지 않으면 에뮬레이터를 재시작하세요.

---

### STEP 2: 앱 실행 확인

1. **에뮬레이터 화면에서:**
   - 앱 목록에서 "deepfake-app" 또는 "딥페이크 탐지 앱" 찾기
   - 앱 아이콘 탭하여 실행

2. **예상 화면:**
   - 검은색 배경 (`#000000`)
   - 상단: 프로필 아이콘 (👤) + 메뉴 버튼 (☰)
   - 메인 메시지: "당신은 이제 허위 정보에 휘둘리지 않을거에요!"
   - 로고 이미지
   - "SWITCH ON!" 버튼 (배경 이미지)
   - "무료 가입" 버튼 (노란색)
   - 하단: 얼굴 이미지

**문제 해결:** 앱이 보이지 않으면 재설치하세요:
```powershell
cd C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\frontend\android
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r app\build\outputs\apk\debug\app-debug.apk
```

---

### STEP 3: HomeScreen 기능 테스트

1. **프로필 아이콘 확인**
   - 상단 왼쪽 프로필 아이콘 (👤) 표시 확인

2. **메뉴 버튼 확인**
   - 상단 오른쪽 메뉴 버튼 (☰) 표시 확인

3. **SWITCH ON! 버튼 테스트**
   - "SWITCH ON!" 버튼 탭
   - **예상 동작:** WidgetControlScreen으로 이동
   - 상단 제목: "위젯 제어"

---

### STEP 4: WidgetControlScreen 테스트

**화면 확인:**
- 제목: "플로팅 위젯 제어"
- 부제목: "다른 앱 위에 떠 있는 버블을 제어합니다."
- 버튼들: "Switch on!", "위젯 종료", "녹화 시작/종료"

**테스트 단계:**

1. **Switch on! 버튼 탭**
   - **예상 동작:** 
     - 권한 요청 팝업 나타남
     - "다른 앱 위에 표시" 권한 요청
   
2. **권한 허용**
   - 팝업에서 "허용" 선택
   - 에뮬레이터 설정 화면으로 이동할 수 있음
   - 설정에서 권한 허용 후 앱으로 돌아옴

3. **위젯 활성화 확인**
   - 권한 허용 후 자동으로 플로팅 위젯 서비스 시작
   - "위젯 시작" 알림 표시

4. **홈 화면으로 이동**
   - 에뮬레이터 홈 버튼 탭 (또는 제스처)
   - **예상 결과:** 파란색 플로팅 버튼이 화면에 표시됨

---

### STEP 5: 플로팅 위젯 테스트

1. **플로팅 버튼 확인**
   - 홈 화면에 파란색 원형 버튼 표시 확인
   - 화면 어디든 드래그 가능

2. **버튼 탭**
   - 플로팅 버튼 탭
   - **예상 동작:** 메뉴가 펼쳐짐
   - 녹화, 캡처, 종료 버튼 표시

3. **메뉴 버튼 테스트**
   - **녹화 버튼**: 탭 시 MediaProjection 권한 요청 → 녹화 시작
   - **캡처 버튼**: 탭 시 화면 캡처
   - **종료 버튼**: 탭 시 위젯 서비스 종료

4. **위젯 종료 확인**
   - "종료" 버튼 탭
   - 플로팅 버튼이 사라짐

---

### STEP 6: RecordScreen 테스트 (앨범 선택)

1. **RecordScreen 이동**
   - 앱으로 돌아가기
   - 뒤로 가기로 HomeScreen으로 이동
   - 네비게이션 또는 앱 내 링크로 RecordScreen 이동
   - 또는 직접 실행:
   ```powershell
   # 앱을 다시 시작하면 Record 탭으로 이동할 수 있는 방법 확인
   ```

2. **앨범 선택 모드**
   - 화면에 "📷 카메라로 녹화" / "🎬 앨범에서 선택" 버튼 표시
   - "🎬 앨범에서 선택" 버튼 탭

3. **미디어 권한 요청**
   - 권한 요청 팝업 나타남
   - "허용" 선택

4. **갤러리 열기**
   - 갤러리/앨범 화면이 열림
   - **참고:** 에뮬레이터 갤러리가 비어있을 수 있음

5. **테스트 비디오 추가 (선택사항)**
   ```powershell
   # PC에서 테스트 비디오를 에뮬레이터로 복사
   & "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" push "test_video.mp4" /sdcard/DCIM/Camera/
   ```
   - 에뮬레이터에서 갤러리 새로고침
   - 비디오 선택

6. **비디오 선택 후**
   - 영상 선택 시 분석 시작
   - 로딩 화면 표시
   - **예상 결과:** ResultScreen으로 이동 (분석 결과 표시)

---

### STEP 7: 백엔드 API 연동 테스트

1. **백엔드 서버 확인**
   ```powershell
   # 새 터미널에서 실행
   curl http://localhost:8000/docs
   ```
   - 브라우저가 열리며 Swagger UI 표시
   - 서버가 정상 작동 중임을 확인

2. **앱에서 API 호출 확인**
   - RecordScreen에서 영상 선택
   - 네트워크 요청 전송 확인
   - **예상:** `POST http://10.0.2.2:8000/analyze-video/`

3. **로그 확인**
   ```powershell
   # 새 PowerShell 창에서 실행
   & "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" logcat | Select-String "analyze|API|network"
   ```

4. **결과 확인**
   - 분석 완료 후 ResultScreen 표시
   - 타임라인 데이터 표시 확인
   - 최대 의심 점수 표시 확인

---

### STEP 8: ResultScreen 테스트

**예상 화면:**
- 제목: "🔎 탐지 결과"
- 최대 의심 점수: XX.X%
- 위험도: 높음/중간/주의/낮음
- 영상 플레이어 (있는 경우)
- 타임라인 차트

**테스트 항목:**
- [ ] 결과 데이터 표시 확인
- [ ] 타임라인 시각화 확인
- [ ] 영상 재생 확인 (있는 경우)

---

### STEP 9: 전체 플로우 테스트

**완전한 사용자 시나리오:**

1. 앱 실행 → HomeScreen 표시
2. "SWITCH ON!" 버튼 탭
3. WidgetControlScreen으로 이동
4. "Switch on!" 버튼 탭 → 권한 허용
5. 홈 화면으로 이동 → 플로팅 버튼 확인
6. 플로팅 버튼 탭 → 녹화 또는 캡처 테스트
7. 앱으로 돌아가기
8. RecordScreen에서 앨범 선택
9. 비디오 선택 → 분석 시작
10. ResultScreen에서 결과 확인

---

## 🐛 문제 해결

### 문제 1: 앱이 설치되지 않음
```powershell
# 완전 제거 후 재설치
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" uninstall com.anonymous.deepfakeapp
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\frontend\android\app\build\outputs\apk\debug\app-debug.apk
```

### 문제 2: 백엔드 연결 실패
- 백엔드 서버가 실행 중인지 확인
- `http://10.0.2.2:8000`이 올바른 주소인지 확인
- 방화벽 설정 확인

### 문제 3: 권한 요청이 나타나지 않음
- 앱 설정에서 수동으로 권한 허용:
  - 설정 → 앱 → deepfake-app → 권한
  - 카메라, 마이크, 저장소, 다른 앱 위에 표시 권한 확인

### 문제 4: 위젯이 표시되지 않음
- 권한이 정확히 허용되었는지 확인
- 에뮬레이터 재시작 후 다시 시도

### 문제 5: 갤러리가 비어있음
```powershell
# 테스트 비디오 추가
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" push "test_video.mp4" /sdcard/DCIM/Camera/
```

---

## 📊 테스트 체크리스트

### 기본 기능
- [ ] 앱 설치 및 실행
- [ ] HomeScreen UI 표시
- [ ] 네비게이션 동작

### 위젯 기능
- [ ] 위젯 권한 요청
- [ ] 플로팅 버튼 표시
- [ ] 메뉴 토글
- [ ] 녹화/캡처 기능 (MediaProjection 권한)

### 영상 분석
- [ ] 앨범에서 영상 선택
- [ ] 백엔드 API 호출
- [ ] 분석 결과 표시
- [ ] 타임라인 시각화

### 백엔드 연동
- [ ] API 통신 성공
- [ ] 에러 핸들링
- [ ] 로딩 상태 표시

---

## 🎯 다음 단계

테스트 완료 후:
1. 발견한 버그 기록
2. 개선 사항 문서화
3. 실제 기기에서 테스트 (카메라/마이크 기능)











