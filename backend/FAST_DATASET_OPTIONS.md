# 빠른 데이터셋 옵션

## 🚀 빠른 시작을 위한 옵션

### 옵션 1: 작은 데이터셋 다운로드 (500MB, 빠름)

```bash
# 가상환경 활성화
cd C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\backend
.\venv\Scripts\Activate.ps1

# 작은 데이터셋 다운로드 (500MB)
kaggle datasets download -d saurabhbagchi/deepfake-image-detection
```

**예상 시간**: 5-10분

### 옵션 2: 이미 있는 데이터셋 사용

이미 딥페이크 이미지 데이터셋이 있다면:

1. **폴더 구조 준비**:
   ```
   dataset/
   ├── REAL/
   │   ├── image1.jpg
   │   └── ...
   └── FAKE/
       ├── image1.jpg
       └── ...
   ```

2. **파일명 변경** (영상 단위 split을 위해):
   - `video001_frame001.jpg` 형식으로 변경
   - 또는 간단히 `video001_001.jpg` 형식

3. **바로 학습 시작**:
   ```bash
   python train_mesonet_cpu_optimized.py --data-dir dataset --epochs 30 --batch-size 8
   ```

### 옵션 3: 테스트용 작은 데이터셋 (100-200개 이미지)

실제 데이터셋 없이도 파이프라인 테스트 가능:

1. **샘플 이미지 수집**: 인터넷에서 REAL/FAKE 얼굴 이미지 각 50-100개
2. **폴더 구조 생성**:
   ```
   dataset_test/
   ├── REAL/
   └── FAKE/
   ```
3. **학습 테스트**:
   ```bash
   python train_mesonet_cpu_optimized.py --data-dir dataset_test --epochs 10 --batch-size 8
   ```

---

## 💡 추천

**지금 바로 시작하려면**:
- 옵션 2 또는 3으로 작은 데이터셋으로 먼저 테스트
- 파이프라인이 정상 작동하면 더 큰 데이터셋 준비

**시간 여유가 있다면**:
- 옵션 1로 500MB 데이터셋 다운로드 (5-10분)
- 또는 밤에 큰 데이터셋 다운로드

---

## 📋 다음 단계

데이터셋이 준비되면:

```bash
# 가상환경 활성화
cd C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\backend
.\venv\Scripts\Activate.ps1

# 학습 시작
python train_mesonet_cpu_optimized.py --data-dir dataset --epochs 30 --batch-size 8
```



