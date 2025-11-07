# EfficientNet-B0 + MesoNet 앙상블 모델 설정 가이드

## 📥 모델 다운로드

1. **모델 다운로드 스크립트 실행**:
```bash
cd backend
python download_models.py
```

이 스크립트는 다음 모델을 자동으로 다운로드합니다:
- EfficientNet-B0 (DFDC pretrained): `weights/effb0_dfdc.pth`
- MesoNet: `weights/mesonet_pretrained.pth`

## ⚙️ 설정

모델 설정은 `app/core/config.py`에서 관리됩니다:

- `FRAME_SAMPLES = 10`: 분석할 프레임 수
- `USE_FACE_CROP = True`: 얼굴 crop 사용 여부
- `IMAGE_SIZE = 224`: 이미지 리사이즈 크기
- `ENSEMBLE_WEIGHT_EFFICIENTNET = 0.7`: EfficientNet 가중치
- `ENSEMBLE_WEIGHT_MESONET = 0.3`: MesoNet 가중치
- `TORCH_NUM_THREADS = 4`: PyTorch 스레드 수
- `CV2_NUM_THREADS = 1`: OpenCV 스레드 수

## 🚀 사용 방법

1. **서버 시작**:
```bash
cd backend
python run_server.bat
```

2. **API 엔드포인트 사용**:
```
POST /analyze-video/
- user_id: str
- video: UploadFile
```

## 📊 모델 구조

### EfficientNet-B0 (DFDC)
- DFDC (Deepfake Detection Challenge) 데이터셋으로 사전 훈련된 EfficientNet-B0
- 가중치: 0.7

### MesoNet
- 딥페이크 탐지를 위한 경량 CNN 모델
- 가중치: 0.3

### 앙상블
- 최종 결과 = 0.7 × EfficientNet-B0 + 0.3 × MesoNet

## ✅ 기능

- ✅ CPU 전용 추론 (GPU 미사용)
- ✅ 10개 프레임 샘플링
- ✅ 얼굴 crop 후 224×224 리사이즈
- ✅ 앙상블 가중 평균 (0.7 × EfficientNet + 0.3 × MesoNet)
- ✅ 기존 API 엔드포인트 구조 유지 (`/analyze-video/`)
- ✅ CPU 추론 최적화 (torch.set_num_threads(4), cv2.setNumThreads(1))

## 📝 주의사항

1. 모델 파일이 없으면 `download_models.py`를 실행하세요.
2. `efficientnet-pytorch` 패키지가 필요합니다: `pip install efficientnet-pytorch`
3. 모델 로딩은 첫 요청 시 자동으로 수행됩니다.


