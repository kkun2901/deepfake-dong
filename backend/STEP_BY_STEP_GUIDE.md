# 단계별 실행 가이드

## 🎯 목표
DFDC Preview Dataset으로 2GB 데이터셋을 만들고 MesoNet-4를 학습하기

## 📋 전체 프로세스

### 1단계: Kaggle API 설정 (5분)

#### 1.1 Kaggle 계정 생성
- https://www.kaggle.com/ 접속
- 회원가입 (무료)

#### 1.2 API 키 다운로드
1. 로그인 후 프로필 클릭
2. Account → API → "Create New Token" 클릭
3. `kaggle.json` 파일 다운로드

#### 1.3 API 키 설치
```bash
# Windows PowerShell
mkdir $env:USERPROFILE\.kaggle
copy kaggle.json $env:USERPROFILE\.kaggle\kaggle.json

# 또는 수동으로
# C:\Users\사용자명\.kaggle\kaggle.json 에 파일 복사
```

#### 1.4 Kaggle API 설치
```bash
cd backend
pip install kaggle
```

---

### 2단계: DFDC Preview Dataset 다운로드 (10-30분)

```bash
cd backend

# 데이터셋 다운로드
kaggle competitions download -c deepfake-detection-challenge

# 압축 해제 (7-Zip 또는 WinRAR 사용)
# 또는 PowerShell
Expand-Archive deepfake-detection-challenge.zip -DestinationPath dfdc_preview
```

**예상 시간**: 인터넷 속도에 따라 다름 (5GB)

---

### 3단계: 프레임 추출 및 데이터셋 생성 (30분-1시간)

```bash
# 메타데이터 기반으로 자동 분류 및 프레임 추출
python prepare_dfdc_with_metadata.py \
    --video-dir dfdc_preview/train_sample_videos \
    --metadata dfdc_preview/metadata.json \
    --output-dir dataset_2gb \
    --max-frames-per-video 40 \
    --train-ratio 0.7
```

**결과**: `dataset_2gb/` 폴더에 train/val/test 자동 생성

**예상 시간**: 비디오 개수에 따라 다름

---

### 4단계: 데이터셋 구조 확인

```bash
# 폴더 구조 확인
# dataset_2gb/
# ├── train/
# │   ├── real/
# │   └── fake/
# ├── val/
# │   ├── real/
# │   └── fake/
# └── test/
#     ├── real/
#     └── fake/
```

**중요**: 파일명이 `videoID_frameID.jpg` 형식인지 확인

---

### 5단계: 데이터셋을 CPU 학습용 형식으로 변환

현재 `dataset_2gb/train/real/`, `dataset_2gb/train/fake/` 구조를
`dataset_2gb/REAL/`, `dataset_2gb/FAKE/` 구조로 변환 필요:

```bash
# Python 스크립트로 변환 (또는 수동으로)
python -c "
from pathlib import Path
import shutil

source = Path('dataset_2gb')
dest = Path('dataset_2gb_flat')

# REAL과 FAKE 폴더 생성
(dest / 'REAL').mkdir(parents=True, exist_ok=True)
(dest / 'FAKE').mkdir(parents=True, exist_ok=True)

# train/val/test의 real 이미지를 REAL로 복사
for split in ['train', 'val', 'test']:
    real_dir = source / split / 'real'
    if real_dir.exists():
        for img in real_dir.glob('*.jpg'):
            shutil.copy2(img, dest / 'REAL' / img.name)

# train/val/test의 fake 이미지를 FAKE로 복사
for split in ['train', 'val', 'test']:
    fake_dir = source / split / 'fake'
    if fake_dir.exists():
        for img in fake_dir.glob('*.jpg'):
            shutil.copy2(img, dest / 'FAKE' / img.name)

print('변환 완료!')
"
```

---

### 6단계: 학습 시작 (12-20시간)

```bash
python train_mesonet_cpu_optimized.py \
    --data-dir dataset_2gb_flat \
    --epochs 30 \
    --batch-size 8 \
    --lr 0.001 \
    --patience 5 \
    --save-model best_model.pt
```

**예상 시간**: CPU 기준 12-20시간 (밤에 실행 권장)

---

### 7단계: 평가 및 결과 확인

```bash
# 테스트 평가 (학습 중 자동 실행됨)
# 또는 수동으로:
python train_mesonet_cpu_optimized.py \
    --mode eval \
    --data-dir dataset_2gb_flat \
    --model-path best_model.pt \
    --batch-size 8
```

---

## 🚀 빠른 시작 (한 번에 실행)

### 스크립트로 자동화 (선택사항)

모든 단계를 자동화하는 스크립트를 만들 수 있습니다.

---

## ⚠️ 주의사항

1. **디스크 공간**: 최소 20-30GB 여유 공간 필요
2. **시간**: 전체 프로세스 약 13-21시간 소요
3. **파일명**: 비디오 ID가 파일명에 포함되어야 함
4. **메모리**: 16GB RAM이면 batch_size=8 권장

---

## 💡 팁

1. **밤에 학습**: 12-20시간이 걸리므로 밤에 실행
2. **작은 데이터셋으로 테스트**: 먼저 500MB로 테스트 후 확장
3. **체크포인트**: 최고 모델만 저장되므로 안전
4. **진행 상황 확인**: 로그를 통해 확인 가능

---

## 📞 문제 발생 시

1. **Kaggle API 오류**: API 키 경로 확인
2. **메모리 부족**: batch_size 줄이기 (8 → 4)
3. **디스크 공간 부족**: 임시 파일 정리
4. **파일명 오류**: 파일명 형식 확인



