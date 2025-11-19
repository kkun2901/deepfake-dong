# PowerShell 실행 명령어 모음

## 📋 단계별 명령어 (복사해서 사용)

### 1단계: 경로 이동 및 가상환경 활성화

```powershell
cd C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\backend
.\venv\Scripts\Activate.ps1
```

---

### 2단계: 데이터셋 다운로드 (선택)

#### 옵션 A: 작은 데이터셋 (500MB, 빠름 - 5-10분)
```powershell
kaggle datasets download -d saurabhbagchi/deepfake-image-detection
Expand-Archive deepfake-image-detection.zip -DestinationPath dataset_kaggle
```

#### 옵션 B: 중간 데이터셋 (1.8GB, 느림 - 20-30분)
```powershell
kaggle datasets download -d manjilkarki/deepfake-and-real-images
Expand-Archive deepfake-and-real-images.zip -DestinationPath dataset_kaggle
```

**참고**: 다운로드가 오래 걸리면 Ctrl+C로 중단하고 옵션 A 사용

---

### 3단계: 데이터셋 구조 확인 및 변환

다운로드한 데이터셋의 구조를 확인하고, 필요시 변환:

```powershell
# 데이터셋 구조 확인
Get-ChildItem dataset_kaggle -Recurse -Directory | Select-Object FullName
```

**필요한 구조**:
```
dataset/
├── REAL/
│   └── *.jpg
└── FAKE/
    └── *.jpg
```

구조가 다르면 파일을 이동/복사하여 위 구조로 맞춰야 합니다.

---

### 4단계: 데이터셋 구조 변환 (필요시)

다운로드한 데이터셋이 train/val/test 구조라면:

```powershell
python convert_dataset_for_cpu_training.py --source-dir dataset_kaggle --output-dir dataset_ready
```

---

### 5단계: 학습 시작

```powershell
# 기본 학습 (30 에포크)
python train_mesonet_cpu_optimized.py --data-dir dataset_ready --epochs 30 --batch-size 8 --save-model best_model.pt

# 빠른 테스트 (10 에포크)
python train_mesonet_cpu_optimized.py --data-dir dataset_ready --epochs 10 --batch-size 8 --save-model best_model.pt
```

**예상 시간**: 
- 10 에포크: 4-7시간
- 30 에포크: 12-20시간

---

### 6단계: 평가 (학습 후)

```powershell
python train_mesonet_cpu_optimized.py --mode eval --data-dir dataset_ready --model-path best_model.pt --batch-size 8
```

---

### 7단계: 예측 (선택)

```powershell
# 단일 이미지
python train_mesonet_cpu_optimized.py --mode predict --model-path best_model.pt --predict-path image.jpg

# 폴더 내 모든 이미지
python train_mesonet_cpu_optimized.py --mode predict --model-path best_model.pt --predict-path folder/
```

---

### 8단계: Threshold 튜닝 (선택)

```powershell
python train_mesonet_cpu_optimized.py --mode tune --data-dir dataset_ready --model-path best_model.pt --batch-size 8
```

---

## 🚀 빠른 시작 (한 번에 복사)

```powershell
# 1. 경로 이동 및 가상환경 활성화
cd C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\backend
.\venv\Scripts\Activate.ps1

# 2. 작은 데이터셋 다운로드 (500MB)
kaggle datasets download -d saurabhbagchi/deepfake-image-detection
Expand-Archive deepfake-image-detection.zip -DestinationPath dataset_kaggle

# 3. 데이터셋 구조 확인
Get-ChildItem dataset_kaggle -Recurse -Directory | Select-Object FullName

# 4. 구조 변환 (필요시)
python convert_dataset_for_cpu_training.py --source-dir dataset_kaggle --output-dir dataset_ready

# 5. 학습 시작
python train_mesonet_cpu_optimized.py --data-dir dataset_ready --epochs 10 --batch-size 8
```

---

## 💡 팁

1. **가상환경 활성화**: 매번 PowerShell을 열 때마다 필요
2. **다운로드 중단**: Ctrl+C로 중단 가능
3. **진행 상황 확인**: 각 명령어 실행 시 출력 메시지 확인
4. **밤에 학습**: 12-20시간이 걸리므로 밤에 실행 권장

---

## ⚠️ 문제 해결

### 메모리 부족
```powershell
# batch-size 줄이기
--batch-size 4
```

### 다운로드 실패
- 인터넷 연결 확인
- Kaggle API 키 확인: `Test-Path $env:USERPROFILE\.kaggle\kaggle.json`

### 파일명 오류
- 파일명이 `videoID_frameID.jpg` 형식인지 확인
- 아니면 간단히 `video001_001.jpg` 형식으로 변경



