# DFDC Preview Dataset으로 2GB 데이터셋 만들기

## 🎯 목표
- **데이터셋 크기**: 2GB
- **학습 시간**: CPU 기준 약 12-20시간
- **데이터셋**: DFDC Preview (Kaggle)

## 📋 단계별 가이드

### 1단계: Kaggle API 설정

#### 1.1 Kaggle 계정 생성
- https://www.kaggle.com/ 에서 계정 생성 (무료)

#### 1.2 API 키 다운로드
1. Kaggle 로그인
2. 프로필 → Account → API → "Create New Token"
3. `kaggle.json` 파일 다운로드

#### 1.3 API 키 설치
```bash
# Windows
mkdir %USERPROFILE%\.kaggle
copy kaggle.json %USERPROFILE%\.kaggle\kaggle.json

# 또는 수동으로
# C:\Users\사용자명\.kaggle\kaggle.json 에 파일 복사
```

#### 1.4 Kaggle API 설치
```bash
pip install kaggle
```

---

### 2단계: DFDC Preview Dataset 다운로드

#### 2.1 데이터셋 다운로드
```bash
cd backend

# DFDC Preview 다운로드
kaggle competitions download -c deepfake-detection-challenge

# 또는 특정 파일만 다운로드 (더 빠름)
# kaggle competitions files -c deepfake-detection-challenge
# kaggle competitions download -c deepfake-detection-challenge -f sample_submission.csv
```

#### 2.2 압축 해제
```bash
# 압축 해제
unzip deepfake-detection-challenge.zip -d dfdc_preview

# 또는 7-Zip 사용 (Windows)
# 7z x deepfake-detection-challenge.zip -odfdc_preview
```

#### 2.3 폴더 구조 확인
```
dfdc_preview/
├── sample_submission.csv
├── test_videos/          # 테스트 비디오
├── train_sample_videos/  # 학습용 샘플 비디오
└── metadata.json         # 레이블 정보
```

---

### 3단계: 메타데이터 확인

#### 3.1 레이블 확인
```python
import json

# metadata.json 확인
with open('dfdc_preview/metadata.json', 'r') as f:
    metadata = json.load(f)

# REAL과 FAKE 비디오 개수 확인
real_count = sum(1 for v in metadata.values() if v.get('label') == 'REAL')
fake_count = sum(1 for v in metadata.values() if v.get('label') == 'FAKE')

print(f"REAL 비디오: {real_count}개")
print(f"FAKE 비디오: {fake_count}개")
```

---

### 4단계: 비디오에서 프레임 추출 (2GB 목표)

#### 4.1 REAL 비디오 프레임 추출
```bash
# REAL 비디오에서 프레임 추출
# 목표: 약 1GB (REAL + FAKE = 2GB)
python prepare_dataset_from_video.py \
    --video-dir dfdc_preview/train_sample_videos \
    --output-dir dataset_temp/real \
    --label 0 \
    --frame-interval 15 \
    --max-frames-per-video 40
```

**설정 설명**:
- `--frame-interval 15`: 15프레임마다 추출 (더 많은 프레임)
- `--max-frames-per-video 40`: 비디오당 최대 40프레임

#### 4.2 FAKE 비디오 프레임 추출
```bash
# FAKE 비디오에서 프레임 추출
python prepare_dataset_from_video.py \
    --video-dir dfdc_preview/train_sample_videos \
    --output-dir dataset_temp/fake \
    --label 1 \
    --frame-interval 15 \
    --max-frames-per-video 40
```

**참고**: `prepare_dataset_from_video.py`는 메타데이터를 자동으로 읽어서 REAL/FAKE를 구분하지 않으므로, 
비디오를 REAL과 FAKE로 수동 분류하거나 스크립트를 수정해야 할 수 있습니다.

#### 4.3 메타데이터 기반 자동 분류 (권장)

메타데이터를 사용하여 자동으로 REAL/FAKE를 분류하는 스크립트:

```python
# prepare_dfdc_with_metadata.py (새 파일 생성 필요)
import json
import cv2
from pathlib import Path
from tqdm import tqdm

def extract_frames_with_metadata(video_dir, metadata_path, output_dir, 
                                  frame_interval=15, max_frames=40):
    """메타데이터를 사용하여 REAL/FAKE 자동 분류"""
    
    # 메타데이터 로드
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    video_dir = Path(video_dir)
    output_real = Path(output_dir) / "real"
    output_fake = Path(output_dir) / "fake"
    output_real.mkdir(parents=True, exist_ok=True)
    output_fake.mkdir(parents=True, exist_ok=True)
    
    # 비디오 파일 찾기
    video_files = list(video_dir.glob("*.mp4"))
    
    for video_path in tqdm(video_files, desc="비디오 처리"):
        video_name = video_path.stem
        
        # 메타데이터에서 레이블 확인
        if video_name not in metadata:
            continue
        
        label = metadata[video_name].get('label', 'REAL')
        output_dir_label = output_real if label == 'REAL' else output_fake
        
        # 프레임 추출
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            continue
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        interval = max(1, total_frames // max_frames)
        
        frame_count = 0
        saved = 0
        
        while saved < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % interval == 0:
                output_path = output_dir_label / f"{video_name}_{saved:04d}.jpg"
                cv2.imwrite(str(output_path), frame)
                saved += 1
            
            frame_count += 1
        
        cap.release()

# 사용 예시
if __name__ == "__main__":
    extract_frames_with_metadata(
        video_dir="dfdc_preview/train_sample_videos",
        metadata_path="dfdc_preview/metadata.json",
        output_dir="dataset_temp",
        frame_interval=15,
        max_frames=40
    )
```

---

### 5단계: 2GB 데이터셋 생성

#### 5.1 데이터셋 크기 확인
```bash
# 현재 크기 확인
du -sh dataset_temp/real
du -sh dataset_temp/fake

# Windows PowerShell
Get-ChildItem dataset_temp/real -Recurse | Measure-Object -Property Length -Sum
Get-ChildItem dataset_temp/fake -Recurse | Measure-Object -Property Length -Sum
```

#### 5.2 2GB로 샘플링 (필요시)
```bash
# 2GB 목표로 샘플링
python create_small_dataset.py \
    --source-dir dataset_temp \
    --output-dir dataset_2gb \
    --target-size-mb 2000 \
    --train-ratio 0.8
```

---

### 6단계: train/val 분할

#### 6.1 자동 분할 (create_small_dataset.py 사용 시)
- `--train-ratio 0.8` 옵션으로 자동 분할됨

#### 6.2 수동 분할
```bash
# train/val 디렉토리 생성
mkdir -p dataset_2gb/train/real
mkdir -p dataset_2gb/train/fake
mkdir -p dataset_2gb/val/real
mkdir -p dataset_2gb/val/fake

# 80/20 분할 (Python 스크립트 사용)
python -c "
import shutil
from pathlib import Path
import random

source = Path('dataset_temp')
dest = Path('dataset_2gb')

for label in ['real', 'fake']:
    files = list((source / label).glob('*.jpg'))
    random.shuffle(files)
    
    n_train = int(len(files) * 0.8)
    
    for f in files[:n_train]:
        shutil.copy2(f, dest / 'train' / label / f.name)
    
    for f in files[n_train:]:
        shutil.copy2(f, dest / 'val' / label / f.name)
    
    print(f'{label}: train={n_train}, val={len(files)-n_train}')
"
```

---

### 7단계: 최종 확인

#### 7.1 데이터셋 구조 확인
```
dataset_2gb/
├── train/
│   ├── real/     # 학습용 REAL 이미지
│   └── fake/     # 학습용 FAKE 이미지
└── val/
    ├── real/     # 검증용 REAL 이미지
    └── fake/     # 검증용 FAKE 이미지
```

#### 7.2 크기 확인
```bash
# 전체 크기 확인
du -sh dataset_2gb

# Windows PowerShell
Get-ChildItem dataset_2gb -Recurse | Measure-Object -Property Length -Sum
```

---

### 8단계: 학습 시작

#### 8.1 기본 학습
```bash
python train_mesonet.py \
    --data-dir dataset_2gb/train \
    --val-dir dataset_2gb/val \
    --epochs 20 \
    --batch-size 32
```

#### 8.2 최적화된 학습 (CPU)
```bash
python train_mesonet.py \
    --data-dir dataset_2gb/train \
    --val-dir dataset_2gb/val \
    --epochs 20 \
    --batch-size 32 \
    --lr 0.001
```

**예상 시간**: CPU 기준 약 12-20시간

---

## 📊 예상 결과

### 데이터셋 구성:
- **총 크기**: 약 2GB
- **이미지 수**: 약 20,000-30,000개
- **Train/Val 비율**: 80/20

### 학습 설정:
- **에포크**: 20
- **배치 크기**: 32
- **학습 시간**: CPU 기준 12-20시간

---

## 🔧 문제 해결

### 문제 1: Kaggle API 인증 오류
```bash
# API 키 경로 확인
echo %USERPROFILE%\.kaggle\kaggle.json

# 권한 설정 (Windows)
icacls %USERPROFILE%\.kaggle\kaggle.json /inheritance:r
icacls %USERPROFILE%\.kaggle\kaggle.json /grant:r "%USERNAME%:R"
```

### 문제 2: 메모리 부족
- 배치 크기를 16으로 줄이기
- 프레임 간격을 늘리기 (15 → 20)

### 문제 3: 디스크 공간 부족
- 임시 파일 정리
- 압축 파일 삭제 (프레임 추출 후)

---

## 💡 팁

1. **밤에 학습**: 12-20시간이 걸리므로 밤에 실행
2. **체크포인트 저장**: 5 에포크마다 자동 저장됨
3. **진행 상황 모니터링**: 로그 확인
4. **SSD 사용**: C: 드라이브(SSD)에 데이터셋 저장

---

## ✅ 체크리스트

- [ ] Kaggle 계정 생성
- [ ] API 키 다운로드 및 설정
- [ ] Kaggle API 설치
- [ ] DFDC Preview 다운로드
- [ ] 압축 해제
- [ ] 메타데이터 확인
- [ ] REAL 비디오 프레임 추출
- [ ] FAKE 비디오 프레임 추출
- [ ] 2GB 데이터셋 생성
- [ ] train/val 분할
- [ ] 데이터셋 크기 확인
- [ ] 학습 시작

---

## 📚 참고 자료

- **Kaggle API 문서**: https://github.com/Kaggle/kaggle-api
- **DFDC 챌린지**: https://www.kaggle.com/c/deepfake-detection-challenge
- **데이터셋 가이드**: `DATASET_GUIDE.md`



