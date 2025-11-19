# 📦 REALGUARD 프로젝트 - 추가 필요 패키지 목록

## 현재 상태
현재 프로젝트는 기본 딥페이크 탐지 기능이 구현되어 있으나, PRD 요구사항 중 일부 기능을 위해 추가 패키지가 필요합니다.

## 🔄 향후 구현 시 필요한 패키지

### Backend (`requirements.txt`에 추가 필요)

#### 1. 암호화 및 보안
```txt
# AES256 암호화를 위한 패키지
cryptography>=41.0.0
pycryptodome>=3.19.0
```

#### 2. 데이터 시각화
```txt
# Plotly를 통한 시각화 피드백
plotly>=5.18.0
kaleido>=0.2.1  # Plotly 이미지 내보내기용
```

#### 3. 데이터베이스 (선택사항 - Supabase 지원 시)
```txt
# Supabase 클라이언트 (선택사항)
supabase>=2.0.0
postgrest>=0.13.0
```

#### 4. 얼굴 임베딩 (선택사항 - FaceNet 추가 시)
```txt
# FaceNet 모델 지원 (선택사항)
facenet-pytorch>=2.5.3
```

### Frontend (`package.json`에 추가 필요)

#### 1. 차트 라이브러리 (시각화 피드백용)
```json
{
  "react-native-chart-kit": "^6.12.0",
  "react-native-svg": "^13.14.0"
}
```

또는

```json
{
  "react-native-webview": "^13.6.0"
}
```
(Plotly를 WebView로 표시하는 경우)

#### 2. 암호화 (클라이언트 측 암호화용, 선택사항)
```json
{
  "react-native-crypto": "^2.2.0",
  "react-native-randombytes": "^3.6.1"
}
```

#### 3. 사용자 인증 (선택사항)
```json
{
  "@react-native-async-storage/async-storage": "^1.21.0",
  "@react-native-firebase/auth": "^18.6.1"
}
```

## ✅ 현재 설치된 패키지 (확인 완료)

### Backend
- ✅ FastAPI, Uvicorn
- ✅ PyTorch, Transformers
- ✅ TensorFlow/Keras (MesoNet용)
- ✅ Whisper, SpeechRecognition
- ✅ OpenCV, MediaPipe
- ✅ Firebase Admin SDK
- ✅ Pandas

### Frontend
- ✅ React Native + Expo
- ✅ Expo Camera, Expo AV
- ✅ Firebase SDK
- ✅ Axios

## 📋 설치 명령어

### Backend
```bash
cd backend
pip install cryptography>=41.0.0 plotly>=5.18.0 kaleido>=0.2.1
```

### Frontend
```bash
cd frontend
npm install react-native-chart-kit react-native-svg
# 또는
npm install react-native-webview
```

## ⚠️ 주의사항

1. **Plotly 설치 시:**
   - `kaleido`는 Plotly 이미지 내보내기에 필요하지만, Windows에서 설치 문제가 있을 수 있음
   - 대안: `react-native-chart-kit` 사용 고려

2. **암호화 패키지:**
   - `cryptography`는 Python 네이티브 확장을 사용하므로 빌드 도구 필요
   - Windows: Visual C++ Build Tools 필요
   - Linux/Mac: gcc, python-dev 필요

3. **FaceNet (선택사항):**
   - 현재는 Vision Transformer 사용 중이므로 필수 아님
   - 얼굴 임베딩이 필요한 경우에만 추가

## 🎯 우선순위별 설치 가이드

### Phase 2 (핵심 기능 강화)
```bash
# Backend
pip install cryptography>=41.0.0

# Frontend
npm install @react-native-async-storage/async-storage
```

### Phase 3 (리워드 및 분석)
```bash
# Backend
pip install plotly>=5.18.0 kaleido>=0.2.1

# Frontend
npm install react-native-chart-kit react-native-svg
```

### Phase 4 (확장 기능)
```bash
# Backend (선택사항)
pip install supabase>=2.0.0 facenet-pytorch>=2.5.3
```








