# GitHub에 올리기 가이드

이 프로젝트를 GitHub에 올리는 방법입니다.

## 1. Git 초기화 (아직 안 했다면)

```bash
cd deepfake-detector-app-main
git init
```

## 2. 모든 파일 추가

```bash
git add .
```

## 3. 첫 커밋

```bash
git commit -m "Initial commit: Deepfake detector app with floating widget"
```

## 4. GitHub 저장소 생성

1. GitHub에서 새 저장소 생성
2. 저장소 URL 복사 (예: `https://github.com/username/repo-name.git`)

## 5. 원격 저장소 연결 및 푸시

```bash
git remote add origin https://github.com/username/repo-name.git
git branch -M main
git push -u origin main
```

## 주의사항

다음 파일들은 `.gitignore`에 포함되어 있어 Git에 올라가지 않습니다:
- `frontend/android/local.properties` - 각 컴퓨터마다 다른 SDK 경로
- `backend/venv/` - Python 가상환경
- `node_modules/` - Node.js 의존성
- `firebase-key.json` - Firebase 키 파일 (보안)
- `*.h5`, `*.pth` - 모델 가중치 파일 (용량이 큼)

## 다른 컴퓨터에서 클론하기

```bash
git clone https://github.com/username/repo-name.git
cd repo-name
```

그 다음 [SETUP_NEW_COMPUTER.md](./SETUP_NEW_COMPUTER.md) 파일을 참고하여 설정하세요.




