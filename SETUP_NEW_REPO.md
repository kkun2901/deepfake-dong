# 새 GitHub 저장소 설정 가이드

## 단계별 가이드

### 1. GitHub에서 새 저장소 생성

1. https://github.com/new 접속
2. Repository name 입력 (예: `deepfake-detector-app`)
3. Description 입력 (선택사항)
4. Public 또는 Private 선택
5. ⚠️ **중요**: "Initialize this repository with a README" 체크하지 마세요!
6. "Create repository" 클릭

### 2. 새 저장소 URL 복사

저장소 생성 후 나타나는 페이지에서 HTTPS URL을 복사합니다:
- 예: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git`

### 3. Git 원격 저장소 변경

#### 방법 1: 기존 origin을 새 저장소로 변경 (권장)

```powershell
# 1. 현재 원격 저장소 확인
git remote -v

# 2. 기존 origin 제거
git remote remove origin

# 3. 새 저장소를 origin으로 추가
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 4. 확인
git remote -v
```

#### 방법 2: 기존 origin을 새 URL로 변경

```powershell
# 1. 기존 origin의 URL을 새 URL로 변경
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 2. 확인
git remote -v
```

### 4. 변경사항 커밋 및 푸시

```powershell
# 1. 모든 변경사항 스테이징
git add .

# 2. 커밋
git commit -m "Initial commit: Add comprehensive installation guide and project files"

# 3. 새 저장소에 푸시
git push -u origin main
```

### 5. 확인

GitHub 웹사이트에서 저장소가 업데이트되었는지 확인하세요!

---

## 주의사항

- ✅ Firebase 키 파일(`firebase-key.json`)은 `.gitignore`에 의해 제외됩니다
- ✅ `local.properties` 파일도 제외됩니다
- ✅ `venv/`, `node_modules/` 등도 제외됩니다
- ⚠️ 커밋 전에 `git status`로 확인하세요!









