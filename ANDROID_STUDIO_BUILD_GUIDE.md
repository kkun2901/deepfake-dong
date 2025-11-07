# Android Studio에서 빌드 진행 상황 확인하기

## 🔍 Build 출력 창 찾기

### 방법 1: 하단 패널에서 확인
1. **Android Studio 하단**을 보면 여러 탭이 있습니다
2. 탭 목록에서 **"Build"** 탭을 클릭
3. 빌드 진행 상황과 로그가 표시됩니다

### 방법 2: View 메뉴에서 열기
1. 상단 메뉴: **View** → **Tool Windows** → **Build**
2. 또는 단축키: `Alt + 0` (0은 숫자)

### 방법 3: 하단 상태 바에서 확인
- 하단 상태 바에서 **"Build"** 아이콘 클릭
- 빌드가 진행 중이면 아이콘이 표시됩니다

## 📊 빌드 상태 확인

### 빌드 진행 중
- "Gradle build running..." 표시
- 진행률 표시줄 (Progress bar)
- 로그 메시지가 실시간으로 출력됨

### 빌드 완료
- ✅ "BUILD SUCCESSFUL"
- ⚠️ "BUILD FAILED" (오류 발생 시)

### 빌드 실패 시
- 오류 메시지 확인
- 로그에서 "FAILURE" 또는 "ERROR" 키워드 검색

## 🎯 Android Studio 하단 패널 구성

일반적으로 하단에 다음 탭들이 있습니다:
- **Build**: 빌드 로그 및 상태
- **Run**: 앱 실행 로그
- **Debug**: 디버깅 정보
- **Terminal**: 터미널 (현재 사용 중인 것)
- **Logcat**: Android 로그

## 💡 팁

1. **빌드가 안 보일 때:**
   - 하단 패널이 접혀있을 수 있음 → 하단 가장자리를 위로 드래그
   
2. **빌드 로그 필터링:**
   - Build 창에서 오류만 보고 싶으면 "ERROR" 검색

3. **빌드 속도 향상:**
   - **File** → **Settings** → **Build, Execution, Deployment** → **Gradle**
   - "Build and run using": Gradle (기본값)

## 🔄 실시간 빌드 확인 (터미널 방법)

Android Studio 외에도 PowerShell 터미널에서 확인:

```powershell
# 빌드 프로세스 확인
Get-Process | Where-Object {$_.ProcessName -like "*java*"}

# APK 파일 생성 확인
Test-Path "C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\frontend\android\app\build\outputs\apk\debug\app-debug.apk"
```












