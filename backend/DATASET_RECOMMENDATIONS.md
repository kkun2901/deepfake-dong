# 데이터셋 추천 (현재 사양 기준)

## 🎯 현재 사양 고려사항
- **CPU 학습만 가능** (GPU 없음)
- **16GB RAM** (충분함)
- **학습 시간 제약** (빠른 테스트 필요)
- **작은 데이터셋 선호** (1-2GB)

## ⭐ 1순위: DFDC Preview Dataset (Kaggle)

### 추천 이유:
- ✅ **작은 크기**: ~5GB (비디오) → 프레임 추출 후 1-2GB
- ✅ **무료**: Kaggle 계정만 있으면 됨
- ✅ **고품질**: 실제 경진대회 데이터셋
- ✅ **다운로드 쉬움**: Kaggle API 사용 가능
- ✅ **샘플링 가능**: 일부만 사용하여 크기 조절

### 다운로드 방법:
```bash
# 1. Kaggle API 설치
pip install kaggle

# 2. API 키 설정
# ~/.kaggle/kaggle.json에 API 키 저장

# 3. 데이터셋 다운로드
kaggle competitions download -c deepfake-detection-challenge

# 4. 일부 비디오만 프레임 추출 (작은 데이터셋 생성)
python prepare_dataset_from_video.py \
    --video-dir dfdc_preview/real_videos \
    --output-dir dataset_temp/real \
    --label 0 \
    --frame-interval 20 \
    --max-frames-per-video 30
```

### 예상 결과:
- **원본**: ~5GB (비디오)
- **프레임 추출 후**: ~1-1.5GB (이미지)
- **학습 시간**: CPU 기준 6-10시간

### 링크:
- **Kaggle**: https://www.kaggle.com/c/deepfake-detection-challenge/data
- **Preview 데이터셋**: 작은 샘플 제공

---

## ⭐ 2순위: 작은 데이터셋 직접 생성

### 추천 이유:
- ✅ **완전 제어**: 원하는 크기로 정확히 조절
- ✅ **빠른 테스트**: 500MB-1GB로 빠르게 시작
- ✅ **유연성**: 필요에 따라 확장 가능

### 방법 1: DFDC에서 샘플링
```bash
# 1. DFDC Preview 다운로드 (일부만)

# 2. 작은 데이터셋 생성
python create_small_dataset.py \
    --source-dir dataset_full \
    --output-dir dataset_small \
    --target-size-mb 1000  # 1GB
```

### 방법 2: 비디오에서 직접 생성
```bash
# 비디오 10개씩만 사용
python create_small_dataset.py \
    --from-videos \
    --video-dir-real path/to/real/videos \
    --video-dir-fake path/to/fake/videos \
    --output-dir dataset_mini \
    --max-videos 10 \
    --frames-per-video 20
```

### 예상 결과:
- **500MB 데이터셋**: 학습 시간 3-5시간
- **1GB 데이터셋**: 학습 시간 6-10시간

---

## 3순위: AI허브 딥페이크 데이터셋 (한국어)

### 추천 이유:
- ✅ **한국어 지원**: 한국어 환경에서 사용 가능
- ✅ **다양한 데이터셋**: 여러 딥페이크 데이터셋 제공
- ✅ **무료**: 회원가입만 하면 됨

### 단점:
- ⚠️ **승인 필요**: 사용 목적에 따라 승인 필요할 수 있음
- ⚠️ **크기 불명확**: 데이터셋마다 크기가 다름

### 링크:
- **AI허브**: https://www.aihub.or.kr/
- **검색어**: "딥페이크", "deepfake", "얼굴 조작"

---

## 4순위: FaceForensics++ (선택적)

### 추천 이유:
- ✅ **고품질**: 연구용으로 널리 사용
- ✅ **다양한 방법**: 여러 딥페이크 생성 방법 포함

### 단점:
- ⚠️ **큰 크기**: 전체 다운로드 시 수십 GB
- ⚠️ **샘플링 필요**: 일부만 사용해야 함

### 링크:
- **GitHub**: https://github.com/ondyari/FaceForensics
- **다운로드**: Google Drive 링크 제공

---

## 📊 데이터셋 비교표

| 데이터셋 | 크기 | 다운로드 | 학습 시간 (CPU) | 추천도 |
|---------|------|---------|----------------|--------|
| **DFDC Preview** | ~5GB (비디오) | 쉬움 ⭐⭐⭐ | 6-10시간 | ⭐⭐⭐⭐⭐ |
| **작은 데이터셋 (1GB)** | 1GB | 쉬움 ⭐⭐⭐ | 6-10시간 | ⭐⭐⭐⭐⭐ |
| **작은 데이터셋 (500MB)** | 500MB | 쉬움 ⭐⭐⭐ | 3-5시간 | ⭐⭐⭐⭐ |
| **AI허브** | 다양 | 보통 ⭐⭐ | 다양 | ⭐⭐⭐ |
| **FaceForensics++** | 수십 GB | 어려움 ⭐ | 매우 오래 | ⭐⭐ |

---

## 🚀 빠른 시작 가이드

### 옵션 1: DFDC Preview (권장)

```bash
# 1. Kaggle API 설정
pip install kaggle
# ~/.kaggle/kaggle.json에 API 키 저장

# 2. 데이터셋 다운로드
kaggle competitions download -c deepfake-detection-challenge

# 3. 압축 해제
unzip deepfake-detection-challenge.zip -d dfdc_preview

# 4. 일부 비디오만 프레임 추출 (1GB 목표)
python prepare_dataset_from_video.py \
    --video-dir dfdc_preview/real_videos \
    --output-dir dataset/real \
    --label 0 \
    --frame-interval 20 \
    --max-frames-per-video 30

python prepare_dataset_from_video.py \
    --video-dir dfdc_preview/fake_videos \
    --output-dir dataset/fake \
    --label 1 \
    --frame-interval 20 \
    --max-frames-per-video 30

# 5. train/val 분할
python create_small_dataset.py \
    --source-dir dataset \
    --output-dir dataset_final \
    --target-size-mb 1000

# 6. 학습 시작
python train_mesonet.py \
    --data-dir dataset_final/train \
    --val-dir dataset_final/val \
    --epochs 10 \
    --batch-size 32
```

**예상 시간**: 
- 다운로드: 10-30분
- 프레임 추출: 30분-1시간
- 학습: 6-10시간

---

### 옵션 2: 최소 데이터셋 (가장 빠름)

```bash
# 1. 비디오 10개씩만 사용
python create_small_dataset.py \
    --from-videos \
    --video-dir-real path/to/real/videos \
    --video-dir-fake path/to/fake/videos \
    --output-dir dataset_mini \
    --max-videos 10 \
    --frames-per-video 20

# 2. 학습
python train_mesonet.py \
    --data-dir dataset_mini/train \
    --val-dir dataset_mini/val \
    --epochs 10 \
    --batch-size 32
```

**예상 시간**: 
- 프레임 추출: 10-20분
- 학습: 1-2시간

---

## 💡 최종 추천

### 현재 사양에 가장 적합한 데이터셋:

1. **DFDC Preview Dataset** (1순위)
   - 이유: 무료, 고품질, 크기 조절 가능
   - 예상 시간: 6-10시간 (CPU)

2. **작은 데이터셋 (500MB-1GB)** (2순위)
   - 이유: 빠른 테스트, 완전 제어
   - 예상 시간: 3-10시간 (CPU)

### 추천 워크플로우:

1. **1단계**: 작은 데이터셋(500MB)으로 빠른 테스트
   - 목적: 파이프라인 검증
   - 시간: 3-5시간

2. **2단계**: 결과 확인 후 1GB 데이터셋으로 본격 학습
   - 목적: 성능 최적화
   - 시간: 6-10시간

3. **3단계**: 필요시 더 큰 데이터셋 사용
   - 목적: 최종 성능 향상
   - 시간: 9-15시간

---

## ⚠️ 주의사항

1. **라이선스**: 모든 데이터셋은 연구 목적으로만 사용
2. **재배포 금지**: 데이터셋을 그대로 공유하면 안 됨
3. **인용 필수**: 논문/README에 출처 명시
4. **디스크 공간**: 최소 20-30GB 여유 공간 필요

---

## 📚 참고 자료

- **Kaggle API 문서**: https://github.com/Kaggle/kaggle-api
- **DFDC 챌린지**: https://www.kaggle.com/c/deepfake-detection-challenge
- **AI허브**: https://www.aihub.or.kr/



