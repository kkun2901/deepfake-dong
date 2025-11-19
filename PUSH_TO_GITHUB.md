# GitHub 저장소에 푸시하기

이 프로젝트를 `https://github.com/kkun2901/deepfake-dong` 저장소에 올리는 방법입니다.

## 1. 원격 저장소 확인

```bash
cd deepfake-detector-app-main
git remote -v
```

## 2. 원격 저장소 설정 (이미 설정되어 있으면 생략)

```bash
git remote set-url origin https://github.com/kkun2901/deepfake-dong.git
```

## 3. 모든 변경사항 추가

```bash
git add .
```

## 4. 커밋

```bash
git commit -m "feat: 플로팅 위젯 UI 개선 및 Cursor 개발 가이드 추가

- 플로팅 위젯 메인 아이콘 변경 (camera_icon.png)
- 버튼 아이콘 변경 (icon_capture.png, icon_close.png)
- 버튼 크기 조정 (메인 60dp, 서브 50dp)
- README.md 업데이트
- 새 컴퓨터 설정 가이드 추가 (SETUP_NEW_COMPUTER.md)
- Cursor 개발 가이드 추가 (.cursorrules, CURSOR_PROMPT.md)
- .gitattributes 추가"
```

## 5. GitHub에 푸시

```bash
git push origin main
```

또는 처음 푸시하는 경우:

```bash
git push -u origin main
```

## 한 번에 실행

```bash
cd deepfake-detector-app-main
git add .
git commit -m "feat: 플로팅 위젯 UI 개선 및 Cursor 개발 가이드 추가"
git push origin main
```

## 문제 해결

### 인증 오류가 발생하는 경우

GitHub에 인증이 필요할 수 있습니다:

1. **Personal Access Token 사용**:
   - GitHub Settings > Developer settings > Personal access tokens
   - 토큰 생성 후 사용

2. **SSH 키 사용**:
   ```bash
   git remote set-url origin git@github.com:kkun2901/deepfake-dong.git
   ```

### 충돌이 발생하는 경우

```bash
git pull origin main --rebase
git push origin main
```




