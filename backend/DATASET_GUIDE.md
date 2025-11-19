# 딥페이크 탐지 데이터셋 가이드

## 📥 데이터셋 다운로드 소스

### 0. **작은 데이터셋 생성 (1~2GB)** ⭐ 추천

기존 대형 데이터셋에서 샘플링하여 작은 데이터셋 생성:

```bash
# 방법 1: 기존 이미지 데이터셋에서 샘플링
python create_small_dataset.py \
    --source-dir dataset_full \
    --output-dir dataset_small \
    --target-size-mb 1500  # 1.5GB

# 방법 2: 비디오에서 직접 미니 데이터셋 생성 (테스트용)
python create_small_dataset.py \
    --from-videos \
    --video-dir-real path/to/real/videos \
    --video-dir-fake path/to/fake/videos \
    --output-dir dataset_mini \
    --max-videos 10 \
    --frames-per-video 20
```

**예상 크기**: 500MB ~ 2GB  
**학습 시간**: GPU 기준 30분 ~ 2시간

### 1. **MesoNet 공식 데이터셋** ⚠️ 링크 만료됨
- **원본 링크**: https://my.pcloud.com/publink/show?code=XZLGvd7ZI9LjgIy7iOLzXBG5RNJzGFQzhTRy (현재 작동 안 함)
- **크기**: 
  - Training set: ~150MB (REAL: 7250개, FAKE: 5111개)
  - Validation set: ~50MB (REAL: 4259개, FAKE: 2889개)
- **형식**: 이미지 파일 (얼굴 정렬 완료)
- **대안**: 
  - MesoNet GitHub 저장소 확인: https://github.com/DariusAf/MesoNet
  - 논문 작성자에게 직접 문의
  - 아래 대체 데이터셋 사용 권장

### 1-1. **DFDC Preview Dataset** (추천 - 작은 크기)
- **Kaggle 링크**: https://www.kaggle.com/c/deepfake-detection-challenge/data
- **크기**: Preview 버전은 상대적으로 작음 (~5GB)
- **형식**: 비디오 파일 (프레임 추출 필요)
- **용도**: MesoNet 튜닝에 적합
- **주의**: Kaggle 계정 필요, 비디오에서 프레임 추출 필요

### 2. **DFDC (Deepfake Detection Challenge) Full**
- **Kaggle 링크**: https://www.kaggle.com/c/deepfake-detection-challenge
- **크기**: 매우 큼 (수백 GB)
- **형식**: 비디오 파일
- **용도**: 대규모 학습, EfficientNet 등 고성능 모델 학습
- **주의**: Kaggle 계정 필요, 비디오에서 프레임 추출 필요

### 3. **FaceForensics++**
- **GitHub**: https://github.com/ondyari/FaceForensics
- **크기**: 대용량
- **형식**: 비디오 파일
- **용도**: 연구 및 고성능 모델 학습

### 4. **Celeb-DF**
- **GitHub**: https://github.com/yuezunli/celeb-deepfakeforensics
- **크기**: 중간 크기
- **형식**: 비디오 파일
- **용도**: 고품질 딥페이크 탐지 학습

### 5. **FFHQ (Fake Face HQ)**
- **다양한 소스에서 수집 가능**
- **용도**: 추가 학습 데이터로 활용

### 6. **AI허브 딥페이크 데이터셋** (한국어 지원)
- **링크**: https://www.aihub.or.kr/
- **검색어**: "딥페이크", "deepfake", "얼굴 조작"
- **용도**: 한국어 환경에서 사용 가능한 데이터셋
- **주의**: 회원가입 필요, 사용 목적에 따라 승인 필요할 수 있음

## 📁 데이터셋 준비 방법

### 방법 1: DFDC Preview Dataset 사용 (추천)

1. **Kaggle에서 다운로드**:
   - https://www.kaggle.com/c/deepfake-detection-challenge/data
   - Kaggle 계정 필요 (무료)
   - Preview 데이터셋 다운로드 (~5GB)

2. **비디오에서 프레임 추출**:
   ```bash
   cd backend
   
   # REAL 비디오에서 프레임 추출
   python prepare_dataset_from_video.py \
       --video-dir path/to/real/videos \
       --output-dir dataset/real \
       --label 0 \
       --frame-interval 10 \
       --max-frames-per-video 50
   
   # FAKE 비디오에서 프레임 추출
   python prepare_dataset_from_video.py \
       --video-dir path/to/fake/videos \
       --output-dir dataset/fake \
       --label 1 \
       --frame-interval 10 \
       --max-frames-per-video 50
   
   # train/val 자동 분할
   python prepare_dataset_from_video.py \
       --video-dir path/to/real/videos \
       --output-dir dataset/real \
       --label 0 \
       --split
   ```

3. **최종 폴더 구조**:
   ```
   dataset/
   ├── train/
   │   ├── real/     # 실제 이미지들
   │   └── fake/     # 딥페이크 이미지들
   └── val/
       ├── real/
       └── fake/
   ```

4. **학습 실행**:
   ```bash
   python train_mesonet.py --data-dir dataset/train --val-dir dataset/val --epochs 20 --batch-size 32
   ```

### 방법 1-1: MesoNet 공식 데이터셋 (링크 만료됨 - 대안 사용 권장)

⚠️ 원본 링크가 작동하지 않습니다. 아래 대안을 사용하세요.

### 방법 2: 비디오 데이터셋에서 이미지 추출

비디오 데이터셋(DFDC, FaceForensics++ 등)을 사용하는 경우:

1. **비디오에서 프레임 추출**:
   ```python
   import cv2
   import os
   
   def extract_frames(video_path, output_dir, label):
       cap = cv2.VideoCapture(video_path)
       frame_count = 0
       while True:
           ret, frame = cap.read()
           if not ret:
               break
           # 10프레임마다 저장 (샘플링)
           if frame_count % 10 == 0:
               output_path = os.path.join(output_dir, f"{label}_{frame_count}.jpg")
               cv2.imwrite(output_path, frame)
           frame_count += 1
       cap.release()
   ```

2. **얼굴 crop** (선택사항):
   - 학습 스크립트에서 자동으로 처리됨 (`--face-crop` 옵션)

3. **폴더 구조 정리**:
   ```
   dataset/
   ├── train/
   │   ├── real/
   │   └── fake/
   └── val/
       ├── real/
       └── fake/
   ```

## 🚀 MesoNet 튜닝 실행

### 기본 사용법

```bash
cd backend
python train_mesonet.py --data-dir dataset/train --val-dir dataset/val
```

### 주요 옵션

- `--data-dir`: 학습 데이터 디렉토리 (필수)
- `--val-dir`: 검증 데이터 디렉토리 (선택사항)
- `--epochs`: 학습 에포크 수 (기본: 20)
- `--batch-size`: 배치 크기 (기본: 32)
- `--lr`: 학습률 (기본: 0.001)
- `--resume`: 이전 체크포인트 경로 (이어서 학습)
- `--output-dir`: 모델 저장 디렉토리 (기본: weights)
- `--face-crop`: 얼굴 crop 사용 (기본: True)
- `--gpu`: GPU 사용 (CUDA 사용 가능 시)

### 예시

```bash
# GPU 사용, 30 에포크, 학습률 0.0005
python train_mesonet.py \
    --data-dir dataset/train \
    --val-dir dataset/val \
    --epochs 30 \
    --batch-size 64 \
    --lr 0.0005 \
    --gpu

# 이어서 학습 (체크포인트에서)
python train_mesonet.py \
    --data-dir dataset/train \
    --val-dir dataset/val \
    --resume weights/mesonet_epoch_10.pth \
    --epochs 20 \
    --gpu
```

## 📊 학습 결과 확인

학습 후 `weights/` 폴더에 다음 파일들이 생성됩니다:

- `mesonet_best.pth`: 최고 성능 모델
- `mesonet_final.pth`: 최종 모델
- `mesonet_epoch_N.pth`: 주기적 체크포인트 (5 에포크마다)

## 🔄 튜닝된 모델 사용

튜닝된 모델을 사용하려면:

1. **가중치 파일 복사**:
   ```bash
   cp weights/mesonet_best.pth weights/Meso4_DF.pth
   ```

2. **또는 config.py에서 경로 변경**:
   ```python
   MESONET_WEIGHTS = str(WEIGHTS_DIR / "mesonet_best.pth")
   ```

3. **서버 재시작**: 백엔드 서버를 재시작하면 새 모델이 로드됩니다.

## 💡 팁

1. **데이터 불균형**: REAL과 FAKE 비율이 다르면 WeightedRandomSampler 사용 고려
2. **데이터 증강**: 학습 스크립트에 이미 포함됨 (RandomHorizontalFlip, ColorJitter)
3. **학습률 조정**: 검증 정확도가 개선되지 않으면 학습률을 낮춰보세요
4. **배치 크기**: GPU 메모리에 따라 조정 (16, 32, 64 등)
5. **얼굴 crop**: 고해상도 이미지에서는 `--face-crop` 사용 권장

## ⚠️ 주의사항

- 데이터셋이 클 경우 디스크 공간 확인
- GPU 메모리 부족 시 배치 크기 줄이기
- 학습 시간은 데이터셋 크기와 하드웨어에 따라 다름
- 검증 데이터셋이 없어도 학습 가능 (단, 과적합 위험)

