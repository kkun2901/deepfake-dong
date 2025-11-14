# 커밋 및 푸시 가이드

현재까지의 변경사항을 GitHub에 올리는 방법입니다.

## 변경사항 요약

1. ✅ 플로팅 위젯 아이콘 변경 (camera_icon.png)
2. ✅ 버튼 아이콘 변경 (icon_capture.png, icon_close.png)
3. ✅ 버튼 크기 조정 (메인 60dp, 서브 50dp)
4. ✅ README.md 업데이트
5. ✅ 새 컴퓨터 설정 가이드 추가 (SETUP_NEW_COMPUTER.md)
6. ✅ .gitattributes 추가

## 커밋 및 푸시 명령어

### 1. 모든 변경사항 추가

```bash
cd deepfake-detector-app-main
git add .
```

### 2. 커밋

```bash
git commit -m "feat: 플로팅 위젯 UI 개선 및 설정 가이드 추가

- 플로팅 위젯 메인 아이콘 변경 (camera_icon.png)
- 버튼 아이콘 변경 (a.png -> icon_capture.png, c.png -> icon_close.png)
- 버튼 크기 조정 (메인 60dp, 서브 50dp)
- README.md 업데이트 (빠른 시작 가이드 추가)
- 새 컴퓨터 설정 가이드 추가 (SETUP_NEW_COMPUTER.md)
- .gitattributes 추가 (라인 엔딩 통일)"
```

### 3. GitHub에 푸시

```bash
git push origin main
```

## 간단 버전 (한 줄로)

```bash
cd deepfake-detector-app-main
git add .
git commit -m "feat: 플로팅 위젯 UI 개선 및 설정 가이드 추가"
git push origin main
```

## 다른 컴퓨터에서 사용하기

프로젝트를 푸시한 후, 다른 컴퓨터에서:

```bash
git clone [저장소 URL]
cd [저장소 이름]
```

그 다음 [SETUP_NEW_COMPUTER.md](./SETUP_NEW_COMPUTER.md) 파일을 참고하여 설정하세요.

