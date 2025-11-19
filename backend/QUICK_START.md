# 빠른 시작 가이드

## ✅ 1단계 완료: Kaggle API 설치

Kaggle API가 설치되었습니다!

## 📋 다음 단계

### 2단계: Kaggle API 키 설정

1. **Kaggle 계정 생성/로그인**
   - https://www.kaggle.com/ 접속
   - 계정이 없으면 회원가입 (무료)

2. **API 키 다운로드**
   - 로그인 후 프로필 클릭 (우측 상단)
   - Account → API → "Create New Token" 클릭
   - `kaggle.json` 파일이 다운로드됨

3. **API 키 설치**
   ```powershell
   # PowerShell에서 실행
   mkdir $env:USERPROFILE\.kaggle -ErrorAction SilentlyContinue
   copy kaggle.json $env:USERPROFILE\.kaggle\kaggle.json
   ```

### 3단계: 데이터셋 다운로드

```powershell
# 가상환경 활성화 (이미 활성화되어 있으면 생략)
cd C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\backend
.\venv\Scripts\Activate.ps1

# DFDC Preview 다운로드
kaggle competitions download -c deepfake-detection-challenge

# 압축 해제
Expand-Archive deepfake-detection-challenge.zip -DestinationPath dfdc_preview
```

**예상 시간**: 10-30분 (인터넷 속도에 따라)

### 4단계: 프레임 추출 (2GB 데이터셋 생성)

```powershell
# 가상환경 활성화된 상태에서
python prepare_dfdc_with_metadata.py `
    --video-dir dfdc_preview/train_sample_videos `
    --metadata dfdc_preview/metadata.json `
    --output-dir dataset_2gb `
    --max-frames-per-video 40 `
    --train-ratio 0.7
```

**예상 시간**: 30분-1시간

### 5단계: 데이터셋 구조 변환

```powershell
# CPU 학습 코드용 형식으로 변환
python convert_dataset_for_cpu_training.py `
    --source-dir dataset_2gb `
    --output-dir dataset_2gb_flat
```

### 6단계: 학습 시작

```powershell
# CPU 최적화 학습
python train_mesonet_cpu_optimized.py `
    --data-dir dataset_2gb_flat `
    --epochs 30 `
    --batch-size 8 `
    --save-model best_model.pt
```

**예상 시간**: 12-20시간 (밤에 실행 권장)

---

## 💡 팁

1. **가상환경 활성화**: 매번 명령어 실행 전에 가상환경 활성화 필요
   ```powershell
   cd C:\dev\deepfake-detector-app-main\deepfake-detector-app-main\backend
   .\venv\Scripts\Activate.ps1
   ```

2. **PowerShell 백틱(`)**: 여러 줄 명령어에서 줄바꿈용

3. **진행 상황 확인**: 각 단계마다 출력 메시지 확인

---

## 🚨 문제 해결

### Kaggle API 인증 오류
```powershell
# API 키 경로 확인
Test-Path $env:USERPROFILE\.kaggle\kaggle.json

# 권한 설정
icacls $env:USERPROFILE\.kaggle\kaggle.json /inheritance:r
icacls $env:USERPROFILE\.kaggle\kaggle.json /grant:r "$env:USERNAME:R"
```

### 메모리 부족
- `--batch-size` 줄이기 (8 → 4)

### 디스크 공간 부족
- 최소 20-30GB 여유 공간 필요



