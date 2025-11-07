# 개발 가이드

## ⚠️ 중요: Expo Go 사용 금지

**이 프로젝트는 Expo Go를 사용할 수 없습니다.**

### 이유:
- 위젯 기능(플로팅 위젯)은 커스텀 네이티브 모듈을 사용합니다
- Expo Go는 커스텀 네이티브 모듈을 지원하지 않습니다

### 올바른 실행 방법:

#### 1. 개발 빌드 실행 (권장)
```powershell
cd frontend
npm start
# 또는
npx expo start --dev-client
```

#### 2. Android 빌드 및 실행
```powershell
cd frontend
npm run android
```

#### 3. Expo Go로 실행 (작동하지 않음 ❌)
```powershell
npm run start:expo  # ❌ 위젯 기능이 작동하지 않습니다
```

## 한글 키보드 지원

앱에서 한글 입력이 가능하도록 설정되어 있습니다. 만약 한글 키보드가 나타나지 않으면:

1. **Android 시스템 설정 확인**
   - 설정 > 시스템 > 언어 및 입력 > 가상 키보드
   - 한글 키보드(예: 삼성 키보드, Gboard)가 활성화되어 있는지 확인

2. **키보드 전환**
   - 키보드 하단의 언어 전환 버튼을 사용하여 한글로 전환

3. **키보드 앱 설치**
   - Gboard(Google 키보드) 설치 권장
   - 한글 입력 지원

## 개발 서버 실행 순서

1. **백엔드 서버 시작**
   ```powershell
   cd backend
   .\run_server.bat
   ```

2. **프론트엔드 개발 서버 시작**
   ```powershell
   cd frontend
   npm start
   ```

3. **앱 실행**
   - 개발 빌드가 이미 설치되어 있어야 함
   - `npm run android`로 빌드 및 실행

## 네트워크 설정

- **실제 기기**: PC와 같은 WiFi에 연결되어야 함
- **에뮬레이터**: `http://10.0.2.2:8000` 사용
- **API URL**: `frontend/src/api/index.ts`에서 확인




