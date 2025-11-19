# 작은 데이터셋으로 빠르게 시작하기 (1~2GB)

## 🎯 목표
- 데이터셋 크기: 1~2GB 이하
- 학습 시간: GPU 기준 30분 ~ 2시간
- 빠른 테스트 및 프로토타입 개발

## 방법 1: 기존 데이터셋에서 샘플링 (가장 간단)

### 1단계: 대형 데이터셋 다운로드
- DFDC Preview (~5GB) 또는 다른 데이터셋 다운로드
- 비디오에서 프레임 추출 (일부만)

### 2단계: 작은 데이터셋 생성
```bash
cd backend

# 1.5GB 크기의 작은 데이터셋 생성
python create_small_dataset.py \
    --source-dir dataset_full \
    --output-dir dataset_small \
    --target-size-mb 1500
```

### 3단계: 학습
```bash
python train_mesonet.py \
    --data-dir dataset_small/train \
    --val-dir dataset_small/val \
    --epochs 20 \
    --batch-size 64 \
    --gpu
```

**예상 시간**: GPU 기준 1~2시간

---

## 방법 2: 비디오에서 직접 미니 데이터셋 생성

### 1단계: 비디오 준비
- REAL 비디오 10개
- FAKE 비디오 10개

### 2단계: 미니 데이터셋 생성
```bash
python create_small_dataset.py \
    --from-videos \
    --video-dir-real path/to/real/videos \
    --video-dir-fake path/to/fake/videos \
    --output-dir dataset_mini \
    --max-videos 10 \
    --frames-per-video 20
```

**결과**: 약 200~500MB 데이터셋 (비디오당 20프레임 × 20개 비디오)

### 3단계: 학습
```bash
python train_mesonet.py \
    --data-dir dataset_mini/train \
    --val-dir dataset_mini/val \
    --epochs 15 \
    --batch-size 32 \
    --gpu
```

**예상 시간**: GPU 기준 30분 ~ 1시간

---

## 방법 3: DFDC Preview에서 샘플링

### 1단계: DFDC Preview 다운로드
- Kaggle: https://www.kaggle.com/c/deepfake-detection-challenge/data
- Preview 데이터셋 다운로드 (~5GB)

### 2단계: 일부 비디오만 프레임 추출
```bash
# REAL 비디오 20개만 처리
python prepare_dataset_from_video.py \
    --video-dir dfdc_preview/real_videos \
    --output-dir dataset_temp/real \
    --label 0 \
    --frame-interval 20 \
    --max-frames-per-video 30

# FAKE 비디오 20개만 처리
python prepare_dataset_from_video.py \
    --video-dir dfdc_preview/fake_videos \
    --output-dir dataset_temp/fake \
    --label 1 \
    --frame-interval 20 \
    --max-frames-per-video 30
```

**결과**: 약 1~1.5GB 데이터셋

### 3단계: train/val 분할
```bash
python create_small_dataset.py \
    --source-dir dataset_temp \
    --output-dir dataset_final \
    --target-size-mb 1500
```

### 4단계: 학습
```bash
python train_mesonet.py \
    --data-dir dataset_final/train \
    --val-dir dataset_final/val \
    --epochs 20 \
    --batch-size 64 \
    --gpu
```

---

## 📊 데이터셋 크기별 예상 시간

| 데이터셋 크기 | 이미지 수 (대략) | GPU 학습 시간 | CPU 학습 시간 |
|-------------|----------------|-------------|-------------|
| 500MB       | ~5,000개       | 30분~1시간   | 3~5시간      |
| 1GB         | ~10,000개      | 1~1.5시간    | 6~10시간     |
| 1.5GB       | ~15,000개      | 1.5~2시간    | 9~15시간     |
| 2GB         | ~20,000개      | 2~3시간      | 12~20시간    |

---

## 💡 팁

1. **처음에는 작게 시작**: 500MB~1GB로 빠르게 테스트
2. **결과 확인 후 확장**: 성능이 좋으면 데이터셋 크기 증가
3. **프레임 간격 조정**: `--frame-interval 20` (더 적은 프레임)
4. **비디오당 프레임 수 제한**: `--max-frames-per-video 20~30`
5. **에포크 수 조정**: 작은 데이터셋은 15~20 에포크면 충분

---

## 🚀 빠른 시작 명령어 (복사해서 사용)

```bash
# 1. 작은 데이터셋 생성 (기존 데이터셋에서)
python create_small_dataset.py \
    --source-dir dataset_full \
    --output-dir dataset_small \
    --target-size-mb 1000

# 2. 학습
python train_mesonet.py \
    --data-dir dataset_small/train \
    --val-dir dataset_small/val \
    --epochs 20 \
    --batch-size 64 \
    --gpu
```

**총 소요 시간**: 약 1~2시간 (GPU 기준)



