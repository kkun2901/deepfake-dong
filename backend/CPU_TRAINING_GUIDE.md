# CPU 최적화 MesoNet-4 학습 가이드

## 📋 개요

`train_mesonet_cpu_optimized.py`는 CPU 환경에 최적화된 완전한 MesoNet-4 학습/평가/추론 코드입니다.

## ✨ 주요 특징

- ✅ **CPU ONLY**: GPU 코드 없음, CPU 전용 최적화
- ✅ **영상 단위 분할**: 같은 비디오의 프레임은 같은 split에만 포함 (데이터 누수 방지)
- ✅ **256×256 입력**: MesoNet-4에 최적화된 입력 크기
- ✅ **Early Stopping**: 과적합 방지
- ✅ **Confusion Matrix**: 평가 시각화
- ✅ **Threshold 튜닝**: 최적 threshold 계산

## 📁 데이터셋 구조

```
dataset/
├── REAL/
│   ├── video001_frame001.jpg
│   ├── video001_frame002.jpg
│   ├── video002_frame001.jpg
│   └── ...
└── FAKE/
    ├── video101_frame001.jpg
    ├── video101_frame002.jpg
    └── ...
```

**중요**: 파일명에 비디오 ID가 포함되어야 합니다 (예: `videoID_frameID.jpg`)

## 🚀 사용 방법

### 1. 학습

```bash
python train_mesonet_cpu_optimized.py \
    --data-dir dataset \
    --epochs 30 \
    --batch-size 8 \
    --lr 0.001 \
    --patience 5 \
    --save-model best_model.pt
```

**주요 옵션**:
- `--data-dir`: 데이터셋 디렉토리 (REAL/, FAKE/ 포함)
- `--epochs`: 학습 에포크 수 (기본: 30)
- `--batch-size`: 배치 크기 (기본: 8, CPU 메모리에 따라 조정)
- `--lr`: 학습률 (기본: 0.001)
- `--patience`: Early stopping patience (기본: 5)
- `--dropout`: Dropout 비율 (기본: 0.4)
- `--train-ratio`: 학습 데이터 비율 (기본: 0.7)
- `--val-ratio`: 검증 데이터 비율 (기본: 0.15)
- `--test-ratio`: 테스트 데이터 비율 (기본: 0.15)

### 2. 평가

```bash
python train_mesonet_cpu_optimized.py \
    --mode eval \
    --data-dir dataset \
    --model-path best_model.pt \
    --batch-size 8
```

### 3. 단일 이미지 예측

```bash
python train_mesonet_cpu_optimized.py \
    --mode predict \
    --model-path best_model.pt \
    --predict-path image.jpg
```

### 4. 폴더 내 모든 이미지 예측

```bash
python train_mesonet_cpu_optimized.py \
    --mode predict \
    --model-path best_model.pt \
    --predict-path folder/
```

### 5. Threshold 튜닝

```bash
python train_mesonet_cpu_optimized.py \
    --mode tune \
    --data-dir dataset \
    --model-path best_model.pt \
    --batch-size 8
```

## 📊 출력 결과

### 학습 중:
- 매 에포크마다 train_loss, train_acc, val_loss, val_acc 출력
- 최고 성능 모델 자동 저장
- Early stopping 시 자동 중단

### 평가 시:
- Confusion Matrix 시각화 (`confusion_matrix.png`)
- 테스트 정확도 출력

### Threshold 튜닝 시:
- 평균값 (mean)
- 표준편차 (std)
- 권장 threshold

## ⚙️ CPU 최적화 설정

코드 내부에서 자동으로 설정됩니다:

```python
torch.set_num_threads(4)  # CPU 스레드 수
device = torch.device("cpu")
num_workers=0  # DataLoader에서 CPU 부하 방지
```

## 🔧 배치 크기 조정

메모리 부족 시 배치 크기를 줄이세요:

```bash
# 메모리 부족 시
--batch-size 4

# 메모리 여유 시
--batch-size 16
```

## 📈 예상 학습 시간

- **2GB 데이터셋**: CPU 기준 약 12-20시간
- **1GB 데이터셋**: CPU 기준 약 6-10시간
- **500MB 데이터셋**: CPU 기준 약 3-5시간

## 💡 팁

1. **밤에 학습**: 시간이 오래 걸리므로 밤에 실행
2. **체크포인트**: 최고 모델만 저장되므로 안전
3. **Early Stopping**: 과적합 방지로 더 나은 일반화
4. **영상 단위 분할**: 데이터 누수 방지로 정확한 평가

## ⚠️ 주의사항

1. **파일명 형식**: 비디오 ID가 파일명에 포함되어야 함
   - ✅ 좋은 예: `video001_frame001.jpg`
   - ❌ 나쁜 예: `001.jpg` (비디오 ID 없음)

2. **메모리**: 배치 크기가 크면 메모리 부족 가능
   - 16GB RAM: batch_size=8 권장
   - 8GB RAM: batch_size=4 권장

3. **디스크 공간**: 학습 중 임시 파일 생성 가능

## 📚 예제

### 전체 워크플로우:

```bash
# 1. 학습
python train_mesonet_cpu_optimized.py \
    --data-dir dataset_2gb \
    --epochs 30 \
    --batch-size 8

# 2. 평가
python train_mesonet_cpu_optimized.py \
    --mode eval \
    --data-dir dataset_2gb \
    --model-path best_model.pt

# 3. Threshold 튜닝
python train_mesonet_cpu_optimized.py \
    --mode tune \
    --data-dir dataset_2gb \
    --model-path best_model.pt

# 4. 예측
python train_mesonet_cpu_optimized.py \
    --mode predict \
    --model-path best_model.pt \
    --predict-path test_images/
```

## 🔍 문제 해결

### 메모리 부족:
- `--batch-size` 줄이기 (8 → 4)
- 데이터셋 크기 줄이기

### 학습이 너무 느림:
- `--batch-size` 늘리기 (8 → 16, 메모리 허용 시)
- `--epochs` 줄이기
- 데이터셋 크기 줄이기

### 파일명 인식 오류:
- 파일명에 비디오 ID가 포함되어 있는지 확인
- `extract_video_id()` 함수의 정규식 패턴 확인



