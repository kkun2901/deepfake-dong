# Android Studio 에뮬레이터 테스트 가이드

## 🎯 에뮬레이터 테스트 팁

### 1. 에뮬레이터 상태 확인

```powershell
# 연결된 기기/에뮬레이터 확인
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices

# 에뮬레이터가 실행 중이면 출력 예시:
# List of devices attached
# emulator-5554   device
```

### 2. 빠른 재설치 (코드 수정 후)

```powershell
cd C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\frontend\android

# 빌드
.\gradlew.bat assembleDebug

# 기존 앱 제거 후 재설치
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" uninstall com.anonymous.deepfakeapp
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install app\build\outputs\apk\debug\app-debug.apk
```

### 3. 로그 확인 (에뮬레이터 디버깅)

```powershell
# 실시간 로그 확인
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" logcat | Select-String "deepfake"

# 또는 앱 태그만 필터링
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" logcat -s ReactNativeJS:* ReactNative:* AndroidRuntime:*
```

### 4. 파일 전송 (테스트용 비디오 등)

```powershell
# 에뮬레이터로 파일 복사
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" push "test_video.mp4" /sdcard/Download/

# 에뮬레이터에서 파일 가져오기
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" pull /sdcard/Download/test_video.mp4 ./
```

### 5. 에뮬레이터 설정 확인

#### 권한 테스트
- **카메라**: 에뮬레이터에서 카메라가 작동하지 않을 수 있음 → 앨범 선택 기능 사용
- **마이크**: 에뮬레이터에서 마이크가 작동하지 않을 수 있음
- **미디어 라이브러리**: `adb push`로 테스트 비디오 추가 가능

#### 에뮬레이터 확장 컨트롤
- 에뮬레이터 창의 `...` 버튼 클릭
- **Extended Controls** → **Camera** 탭에서 가상 카메라 설정 가능
- **Extended Controls** → **Microphone** 탭에서 오디오 입력 설정 가능

### 6. 백엔드 API 연결 확인

에뮬레이터에서 로컬 백엔드 접속:
- **에뮬레이터**: `http://10.0.2.2:8000` (localhost 대체 주소)
- **실제 기기**: PC의 실제 IP 주소 필요

백엔드 서버가 실행 중인지 확인:
```powershell
# 백엔드 서버 상태 확인
curl http://localhost:8000/docs
```

### 7. 개발 모드 (Hot Reload)

Expo 개발 서버 사용 (권장):
```powershell
cd C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\frontend
npm run android
```

이 방식은:
- 코드 변경 시 자동 리로드
- 빠른 개발 속도
- 네이티브 코드 변경 시에는 다시 빌드 필요

### 8. 네이티브 코드 변경 후

Kotlin 파일 수정 후:
```powershell
cd C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\frontend\android
.\gradlew.bat assembleDebug
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r app\build\outputs\apk\debug\app-debug.apk
```

### 9. 에뮬레이터 문제 해결

#### 앱이 설치되지 않을 때
```powershell
# 앱 완전 제거
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" uninstall com.anonymous.deepfakeapp

# 캐시 정리
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell pm clear com.anonymous.deepfakeapp

# 다시 설치
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install app\build\outputs\apk\debug\app-debug.apk
```

#### 에뮬레이터 재시작
- Android Studio → AVD Manager → 에뮬레이터 우클릭 → Cold Boot Now

#### 로그캣 정리
```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" logcat -c
```

### 10. 유용한 ADB 명령어 단축키

PowerShell 별칭 설정 (선택사항):
```powershell
# 프로필에 추가
notepad $PROFILE

# 다음 내용 추가:
Set-Alias adb "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
function adb-install { adb install -r $args[0] }
function adb-logcat { adb logcat | Select-String $args[0] }

# 사용 예:
# adb devices
# adb-install app\build\outputs\apk\debug\app-debug.apk
# adb-logcat "deepfake"
```

## 🧪 테스트 시나리오

### 1. 기본 기능 테스트
- [ ] HomeScreen 렌더링 확인
- [ ] "SWITCH ON!" 버튼 클릭 → WidgetControlScreen 이동
- [ ] RecordScreen에서 앨범 선택 기능

### 2. 위젯 기능 테스트
- [ ] 위젯 권한 요청
- [ ] 플로팅 버튼 표시
- [ ] 메뉴 토글 (녹화/캡처/종료 버튼)

### 3. 백엔드 연동 테스트
- [ ] 비디오 업로드 및 분석 요청
- [ ] 결과 화면 표시

## ⚠️ 에뮬레이터 제한사항

1. **카메라**: 실제 카메라 없음 → 앨범 선택으로 테스트
2. **화면 녹화**: MediaProjection 권한은 작동하지만 실제 화면 녹화는 제한적
3. **성능**: 실제 기기보다 느릴 수 있음

## 📝 추천 테스트 순서

1. **개발 모드로 실행** (`npm run android`) - 빠른 반복 테스트
2. **APK 빌드 후 설치** - 최종 확인
3. **실제 기기 테스트** - 실제 카메라/마이크 기능 확인























