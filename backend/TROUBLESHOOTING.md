# 압축 해제 문제 해결

## ⚠️ 30분 이상 걸리는 경우

### 1. 프로세스 확인
```powershell
# PowerShell 프로세스 확인
Get-Process powershell

# 압축 해제 프로세스 확인
Get-Process | Where-Object {$_.ProcessName -like "*expand*" -or $_.ProcessName -like "*7z*"}
```

### 2. 디스크 공간 확인
```powershell
# C: 드라이브 여유 공간 확인
Get-PSDrive C | Select-Object Used,Free

# 또는
Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'" | Select-Object Size,FreeSpace
```

**필요 공간**: 최소 5-10GB 여유 공간 필요

### 3. 강제 종료 후 다른 방법 시도

#### 방법 A: 7-Zip 사용 (더 빠름)
```powershell
# 7-Zip 설치되어 있다면
& "C:\Program Files\7-Zip\7z.exe" x deepfake-and-real-images.zip -odataset_1.8gb
```

#### 방법 B: WinRAR 사용
- WinRAR로 수동 압축 해제

#### 방법 C: 작은 데이터셋으로 변경
```powershell
# 500MB 데이터셋 다운로드 (더 빠름)
kaggle datasets download -d saurabhbagchi/deepfake-image-detection
Expand-Archive deepfake-image-detection.zip -DestinationPath dataset_500mb -Force
```

### 4. 현재 상태 확인
```powershell
# dataset_1.8gb 폴더가 생성되었는지 확인
Test-Path dataset_1.8gb

# 부분적으로 생성되었는지 확인
if (Test-Path dataset_1.8gb) {
    Get-ChildItem dataset_1.8gb -Recurse | Measure-Object -Property Length -Sum
}
```

---

## 💡 권장 조치

1. **Ctrl+C로 중단**
2. **작은 데이터셋(500MB)으로 변경** - 더 빠르고 테스트하기 좋음
3. **또는 7-Zip 사용** - PowerShell Expand-Archive보다 빠를 수 있음

---

## 🚀 빠른 대안

```powershell
# 1. 현재 프로세스 중단 (Ctrl+C)

# 2. 작은 데이터셋 다운로드 (500MB, 5-10분)
kaggle datasets download -d saurabhbagchi/deepfake-image-detection
Expand-Archive deepfake-image-detection.zip -DestinationPath dataset_500mb -Force

# 3. 바로 학습 시작 가능
```



