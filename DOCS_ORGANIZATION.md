# 📚 문서 정리 가이드

프로젝트 루트에 있는 .md 파일들을 적절한 위치로 정리하는 가이드입니다.

## 📁 권장 디렉토리 구조

```
deepfake-detector-app-main/
├── README.md                          # ✅ 루트에 유지 (메인 프로젝트 설명)
│
├── docs/                              # 📁 새로 생성 필요
│   ├── prd/                           # PRD 및 프로젝트 계획 문서
│   │   ├── REALGUARD_PRD.md          # 원본 PRD (REALGUARD_PRD (2).md에서 이름 변경)
│   │   ├── REALGUARD_PRD_REVISED.md  # 수정된 PRD
│   │   ├── PROJECT_STRUCTURE.md      # 프로젝트 구조 문서
│   │   ├── PROJECT_OVERVIEW.md       # 프로젝트 개요
│   │   ├── PROJECT_DOCUMENT.md       # 프로젝트 문서
│   │   └── PROJECT_REPORT.md         # 프로젝트 리포트
│   │
│   ├── guides/                        # 개발 가이드 문서
│   │   ├── QUICK_START.md            # 빠른 시작 가이드
│   │   ├── DEVELOPMENT_CONTEXT.md    # 개발 컨텍스트
│   │   ├── INTEGRATION_GUIDE.md      # 통합 가이드
│   │   ├── SETUP_CHECKLIST.md        # 설정 체크리스트
│   │   └── SETUP_NEW_REPO.md         # 새 저장소 설정
│   │
│   ├── build/                         # 빌드 및 테스트 가이드
│   │   ├── BUILD_GUIDE.md            # 빌드 가이드
│   │   ├── ANDROID_STUDIO_BUILD_GUIDE.md
│   │   ├── TEST_STEPS.md             # 테스트 단계
│   │   └── EMULATOR_TEST_GUIDE.md    # 에뮬레이터 테스트 가이드
│   │
│   ├── firebase/                      # Firebase 관련 문서
│   │   ├── FIREBASE_SETUP_GUIDE.md   # Firebase 설정 가이드
│   │   └── FIREBASE_REQUIREMENTS.md  # Firebase 요구사항
│   │
│   ├── packages/                      # 패키지 및 의존성 문서
│   │   └── REQUIRED_PACKAGES.md      # 필요한 패키지 목록
│   │
│   └── other/                         # 기타 문서
│       └── FLOW_DIAGRAM.md           # 플로우 다이어그램
│
├── backend/
│   └── README_MODEL_SETUP.md         # ✅ 이미 적절한 위치
│
└── frontend/
    └── README_DEV.md                  # ✅ 이미 적절한 위치
```

---

## 📋 파일 이동 목록

### 1. PRD 및 프로젝트 계획 문서 → `docs/prd/`

다음 파일들을 `docs/prd/` 폴더로 이동:

- [ ] `REALGUARD_PRD (2).md` → `docs/prd/REALGUARD_PRD.md` (이름 변경)
- [ ] `REALGUARD_PRD_REVISED.md` → `docs/prd/REALGUARD_PRD_REVISED.md`
- [ ] `PROJECT_STRUCTURE.md` → `docs/prd/PROJECT_STRUCTURE.md`
- [ ] `PROJECT_OVERVIEW.md` → `docs/prd/PROJECT_OVERVIEW.md`
- [ ] `PROJECT_DOCUMENT.md` → `docs/prd/PROJECT_DOCUMENT.md`
- [ ] `PROJECT_REPORT.md` → `docs/prd/PROJECT_REPORT.md`

**이유:** PRD와 프로젝트 계획 문서는 개발 참고용이므로 별도 폴더로 분리

---

### 2. 개발 가이드 문서 → `docs/guides/`

다음 파일들을 `docs/guides/` 폴더로 이동:

- [ ] `QUICK_START.md` → `docs/guides/QUICK_START.md`
- [ ] `DEVELOPMENT_CONTEXT.md` → `docs/guides/DEVELOPMENT_CONTEXT.md`
- [ ] `INTEGRATION_GUIDE.md` → `docs/guides/INTEGRATION_GUIDE.md`
- [ ] `SETUP_CHECKLIST.md` → `docs/guides/SETUP_CHECKLIST.md`
- [ ] `SETUP_NEW_REPO.md` → `docs/guides/SETUP_NEW_REPO.md`

**이유:** 개발자를 위한 가이드 문서들을 한 곳에 모아 관리

---

### 3. 빌드 및 테스트 가이드 → `docs/build/`

다음 파일들을 `docs/build/` 폴더로 이동:

- [ ] `BUILD_GUIDE.md` → `docs/build/BUILD_GUIDE.md`
- [ ] `ANDROID_STUDIO_BUILD_GUIDE.md` → `docs/build/ANDROID_STUDIO_BUILD_GUIDE.md`
- [ ] `TEST_STEPS.md` → `docs/build/TEST_STEPS.md`
- [ ] `EMULATOR_TEST_GUIDE.md` → `docs/build/EMULATOR_TEST_GUIDE.md`

**이유:** 빌드 및 테스트 관련 문서들을 별도 폴더로 분리

---

### 4. Firebase 관련 문서 → `docs/firebase/`

다음 파일들을 `docs/firebase/` 폴더로 이동:

- [ ] `FIREBASE_SETUP_GUIDE.md` → `docs/firebase/FIREBASE_SETUP_GUIDE.md`
- [ ] `FIREBASE_REQUIREMENTS.md` → `docs/firebase/FIREBASE_REQUIREMENTS.md`

**이유:** Firebase 관련 문서들을 한 곳에 모아 관리

---

### 5. 패키지 및 의존성 문서 → `docs/packages/`

다음 파일을 `docs/packages/` 폴더로 이동:

- [ ] `REQUIRED_PACKAGES.md` → `docs/packages/REQUIRED_PACKAGES.md`

**이유:** 패키지 관련 문서를 별도 폴더로 분리

---

### 6. 기타 문서 → `docs/other/`

다음 파일을 `docs/other/` 폴더로 이동:

- [ ] `FLOW_DIAGRAM.md` → `docs/other/FLOW_DIAGRAM.md`

**이유:** 기타 참고 문서를 별도 폴더로 분리

---

### 7. 루트에 유지할 파일

다음 파일은 루트에 유지:

- ✅ `README.md` - 메인 프로젝트 설명 (GitHub에서 자동 표시)

---

## 🚀 이동 명령어 (Windows PowerShell)

```powershell
# 1. docs 디렉토리 구조 생성
New-Item -ItemType Directory -Force -Path "docs\prd"
New-Item -ItemType Directory -Force -Path "docs\guides"
New-Item -ItemType Directory -Force -Path "docs\build"
New-Item -ItemType Directory -Force -Path "docs\firebase"
New-Item -ItemType Directory -Force -Path "docs\packages"
New-Item -ItemType Directory -Force -Path "docs\other"

# 2. PRD 문서 이동
Move-Item "REALGUARD_PRD (2).md" "docs\prd\REALGUARD_PRD.md"
Move-Item "REALGUARD_PRD_REVISED.md" "docs\prd\"
Move-Item "PROJECT_STRUCTURE.md" "docs\prd\"
Move-Item "PROJECT_OVERVIEW.md" "docs\prd\"
Move-Item "PROJECT_DOCUMENT.md" "docs\prd\"
Move-Item "PROJECT_REPORT.md" "docs\prd\"

# 3. 개발 가이드 문서 이동
Move-Item "QUICK_START.md" "docs\guides\"
Move-Item "DEVELOPMENT_CONTEXT.md" "docs\guides\"
Move-Item "INTEGRATION_GUIDE.md" "docs\guides\"
Move-Item "SETUP_CHECKLIST.md" "docs\guides\"
Move-Item "SETUP_NEW_REPO.md" "docs\guides\"

# 4. 빌드 및 테스트 가이드 이동
Move-Item "BUILD_GUIDE.md" "docs\build\"
Move-Item "ANDROID_STUDIO_BUILD_GUIDE.md" "docs\build\"
Move-Item "TEST_STEPS.md" "docs\build\"
Move-Item "EMULATOR_TEST_GUIDE.md" "docs\build\"

# 5. Firebase 문서 이동
Move-Item "FIREBASE_SETUP_GUIDE.md" "docs\firebase\"
Move-Item "FIREBASE_REQUIREMENTS.md" "docs\firebase\"

# 6. 패키지 문서 이동
Move-Item "REQUIRED_PACKAGES.md" "docs\packages\"

# 7. 기타 문서 이동
Move-Item "FLOW_DIAGRAM.md" "docs\other\"
```

---

## 🚀 이동 명령어 (Linux/Mac)

```bash
# 1. docs 디렉토리 구조 생성
mkdir -p docs/{prd,guides,build,firebase,packages,other}

# 2. PRD 문서 이동
mv "REALGUARD_PRD (2).md" "docs/prd/REALGUARD_PRD.md"
mv REALGUARD_PRD_REVISED.md docs/prd/
mv PROJECT_STRUCTURE.md docs/prd/
mv PROJECT_OVERVIEW.md docs/prd/
mv PROJECT_DOCUMENT.md docs/prd/
mv PROJECT_REPORT.md docs/prd/

# 3. 개발 가이드 문서 이동
mv QUICK_START.md docs/guides/
mv DEVELOPMENT_CONTEXT.md docs/guides/
mv INTEGRATION_GUIDE.md docs/guides/
mv SETUP_CHECKLIST.md docs/guides/
mv SETUP_NEW_REPO.md docs/guides/

# 4. 빌드 및 테스트 가이드 이동
mv BUILD_GUIDE.md docs/build/
mv ANDROID_STUDIO_BUILD_GUIDE.md docs/build/
mv TEST_STEPS.md docs/build/
mv EMULATOR_TEST_GUIDE.md docs/build/

# 5. Firebase 문서 이동
mv FIREBASE_SETUP_GUIDE.md docs/firebase/
mv FIREBASE_REQUIREMENTS.md docs/firebase/

# 6. 패키지 문서 이동
mv REQUIRED_PACKAGES.md docs/packages/

# 7. 기타 문서 이동
mv FLOW_DIAGRAM.md docs/other/
```

---

## 📝 README.md 업데이트 필요

파일 이동 후 `README.md`를 업데이트하여 새로운 문서 위치를 반영해야 합니다:

```markdown
## 📚 문서

- [빠른 시작](docs/guides/QUICK_START.md)
- [프로젝트 구조](docs/prd/PROJECT_STRUCTURE.md)
- [PRD (수정본)](docs/prd/REALGUARD_PRD_REVISED.md)
- [빌드 가이드](docs/build/BUILD_GUIDE.md)
- [Firebase 설정](docs/firebase/FIREBASE_SETUP_GUIDE.md)
- [필요한 패키지](docs/packages/REQUIRED_PACKAGES.md)
```

---

## ⚠️ 주의사항

1. **파일 참조 업데이트**: 다른 파일에서 이동된 문서를 참조하는 경우 경로를 업데이트해야 합니다.

2. **Git 히스토리**: `git mv` 명령어를 사용하면 파일 이동 히스토리가 유지됩니다:
   ```bash
   git mv "REALGUARD_PRD (2).md" "docs/prd/REALGUARD_PRD.md"
   ```

3. **상대 경로**: 문서 내부의 상대 경로 참조가 있다면 업데이트가 필요할 수 있습니다.

---

## ✅ 체크리스트

이동 완료 후 확인:

- [ ] 모든 파일이 올바른 위치로 이동됨
- [ ] `docs/` 디렉토리 구조가 생성됨
- [ ] `README.md`의 문서 링크가 업데이트됨
- [ ] 다른 문서의 상대 경로 참조가 업데이트됨
- [ ] Git 커밋 완료








