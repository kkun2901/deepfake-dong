# 데이터셋 다운로드 대안

## ⚠️ DFDC 경진대회 종료됨

DFDC (Deepfake Detection Challenge) 경진대회가 종료되어 직접 다운로드가 어려울 수 있습니다.

## 🔄 대안 방법

### 방법 1: Kaggle Datasets에서 검색

```bash
# 가상환경 활성화 후
kaggle datasets list -s deepfake
```

다른 딥페이크 데이터셋을 찾아서 사용할 수 있습니다.

### 방법 2: 직접 데이터셋 준비

이미 가지고 있는 딥페이크 이미지 데이터셋이 있다면:

1. **폴더 구조 준비**:
   ```
   dataset/
   ├── REAL/
   │   ├── video001_frame001.jpg
   │   ├── video001_frame002.jpg
   │   └── ...
   └── FAKE/
       ├── video101_frame001.jpg
       └── ...
   ```

2. **파일명 형식**: `videoID_frameID.jpg` 형식으로 이름 변경

3. **학습 시작**:
   ```bash
   python train_mesonet_cpu_optimized.py \
       --data-dir dataset \
       --epochs 30 \
       --batch-size 8
   ```

### 방법 3: 작은 테스트 데이터셋으로 시작

실제 데이터셋이 없어도 테스트할 수 있습니다:

1. **샘플 이미지 수집**: 인터넷에서 REAL/FAKE 얼굴 이미지 수집
2. **작은 데이터셋 생성**: 100-200개 이미지로 시작
3. **학습 테스트**: 파이프라인 검증

### 방법 4: AI허브 데이터셋

한국 AI허브에서 딥페이크 데이터셋 확인:
- https://www.aihub.or.kr/
- 검색어: "딥페이크", "deepfake", "얼굴 조작"

---

## 💡 권장 사항

**현재 상황에서는**:
1. 이미 가지고 있는 데이터셋이 있다면 그것을 사용
2. 없다면 작은 테스트 데이터셋(100-200개)으로 먼저 파이프라인 테스트
3. 파이프라인이 정상 작동하면 더 큰 데이터셋 준비

---

## 📋 다음 단계

데이터셋이 준비되면:

```bash
# 1. 데이터셋 구조 확인
# dataset/REAL/ 와 dataset/FAKE/ 폴더가 있어야 함

# 2. 학습 시작
cd C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\backend
.\venv\Scripts\Activate.ps1
python train_mesonet_cpu_optimized.py --data-dir dataset --epochs 30 --batch-size 8
```



