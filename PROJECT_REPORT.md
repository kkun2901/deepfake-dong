# 딥페이크 탐지 앱 프로젝트 보고서

## 1. 프로젝트 설명

### 기술적 구현 방식

모바일 환경에서 실시간 딥페이크 탐지를 구현하기 위해 React Native 프레임워크와 Android Native Module을 결합한 하이브리드 아키텍처를 설계하였다. Android MediaProjection API와 Foreground Service를 활용하여 플로팅 위젯 형태로 사용자 화면을 백그라운드에서 녹화하고, FastAPI 백엔드 서버로 영상을 전송하여 딥러닝 모델로 분석하는 파이프라인을 구축하였다.

딥페이크 탐지 엔진은 Hugging Face Transformers 라이브러리의 두 가지 Vision Transformer 모델(Deep-Fake-Detector-v2-Model, google/vit-base-patch16-224-in21k)을 앙상블 방식으로 결합하여 구현하였다. OpenCV Haar Cascade 얼굴 감지기를 활용하여 얼굴이 포함된 프레임만 선별 분석함으로써 연산 효율을 높이고 정확도를 향상시켰다. 영상 길이에 따라 동적으로 프레임 추출 간격을 조정하는 알고리즘(5초 이하: 0.5초, 10초 이하: 1초, 30초 이하: 2초, 30초 초과: 3초)을 적용하여 짧은 영상은 상세 분석하고 긴 영상은 효율적으로 처리하도록 설계하였다.

프레임별 분석 결과는 Python ProcessPoolExecutor를 활용한 멀티프로세싱으로 병렬 처리하며, 배치 크기 3개 단위로 나누어 메모리 사용량을 관리한다. 연속된 동일 결과를 최소 2초 이상 구간으로 그룹화하는 타임라인 세그먼트 생성 알고리즘을 적용하여 사용자에게 의미있는 분석 구간을 제공한다. 정적 화면의 오탐을 방지하기 위해 프레임 수가 5개 미만이고 confidence가 0.85 미만인 경우 confidence를 60%로 감소시키는 보정 알고리즘을 구현하였다.

분석 결과는 JSONL, CSV, JSON 형식의 텍스트 파일로 자동 변환되며, FastAPI 엔드포인트를 통해 개별 다운로드가 가능하도록 구현하였다. React Native Linking API를 활용하여 모바일 브라우저에서 직접 파일을 다운로드할 수 있도록 설계하였다.

### 독창성과 차별성

기존 PC 기반 딥페이크 탐지 도구와 달리, Android 플로팅 위젯을 활용한 실시간 스크린 레코딩 기능은 사용자가 현재 사용 중인 앱 화면을 별도 앱 전환 없이 바로 녹화하고 분석할 수 있는 차별화된 사용자 경험을 제공한다. 이는 Android MediaProjection API와 Foreground Service를 결합하여 구현한 독창적인 기술적 접근 방식이다.

얼굴 감지 기반 스마트 프레임 추출은 OpenCV Haar Cascade를 활용하여 분석 전 단계에서 얼굴이 없는 프레임을 사전에 제거함으로써 불필요한 딥러닝 연산을 감소시키고 분석 정확도를 향상시킨다. 이는 단순히 모든 프레임을 분석하는 기존 방식과 차별화된 전처리 최적화 방법이다.

동적 프레임 추출 간격 조정 알고리즘은 영상 길이에 따라 자동으로 최적의 분석 밀도를 결정함으로써, 짧은 영상은 상세하게 분석하고 긴 영상은 효율적으로 처리하는 적응형 분석 시스템을 구현하였다. 이는 고정된 프레임 샘플링 방식과 비교하여 분석 품질과 효율성을 균형있게 확보한 차별화된 설계이다.

정적 화면 보정 알고리즘은 실제 테스트 과정에서 발견된 문제(홈 화면 등 얼굴이 없는 정적 화면의 오탐)를 해결하기 위해 개발된 실용적인 보정 메커니즘이다. 프레임 수와 confidence 값을 종합적으로 고려하여 정적 화면일 가능성을 판단하고 confidence를 조정함으로써 오탐률을 현저히 감소시켰다.

텍스트 기반 데이터셋 자동 생성 기능은 분석 결과를 JSONL, CSV, JSON 형식으로 즉시 변환하여 딥러닝 학습용 데이터셋으로 활용할 수 있도록 제공한다. ZIP 압축 없이 개별 텍스트 파일로 직접 다운로드 가능하도록 설계하여 모바일 환경에서도 빠르고 편리하게 접근할 수 있으며, 머신러닝 연구자들이 별도 변환 과정 없이 바로 학습 데이터로 활용할 수 있는 실용성을 확보하였다.

### 결과 활용성

사용자는 모바일 앱을 통해 의심스러운 영상을 발견 즉시 녹화하고 분석할 수 있어, 정보 검증 시간을 대폭 단축할 수 있다. 플로팅 위젯 방식으로 앱 전환 없이 실시간 스크린 레코딩이 가능하여 사용자 편의성이 극대화된다.

분석 결과는 딥페이크 확률을 정수 퍼센트로 명확하게 표시하며, 타임라인 세그먼트 정보를 통해 영상 내 어느 구간에서 딥페이크가 탐지되었는지 상세하게 확인할 수 있다. 이를 통해 사용자는 신뢰할 수 있는 정보와 의심스러운 정보를 구분할 수 있다.

데이터셋 자동 생성 기능을 통해 분석 결과가 JSONL, CSV, JSON 형식으로 즉시 변환되어 딥러닝 모델 학습 데이터로 활용 가능하다. 프레임별 또는 세그먼트별 분석 정보, confidence 값, 라벨 등 학습에 필요한 모든 정보가 포함되어 있어 연구자들이 별도 전처리 과정 없이 바로 모델 학습에 활용할 수 있다.

Excel 호환 CSV 파일과 구조화된 JSON 메타데이터를 제공함으로써, 비기술 사용자도 분석 결과를 쉽게 확인하고 관리할 수 있다. UTF-8 BOM이 포함된 CSV 파일은 Excel에서 바로 열어볼 수 있어 추가 도구 없이 결과를 검토할 수 있다.

Android 네이티브 앱으로 제공되어 설치형 서비스를 통해 접근성이 향상되며, 백엔드 API를 통한 대량 영상 처리도 가능하여 다양한 사용 시나리오에 대응할 수 있다. 플로팅 위젯 기반 녹화와 업로드 기반 분석 두 가지 방식을 모두 제공하여 사용자의 다양한 니즈를 충족시킨다.

---

## 2. 프로젝트 수행 과정

### 1단계: 모바일 플로팅 위젯 기반 스크린 레코딩 시스템 설계 및 구현

초기 아이디어는 사용자가 의심스러운 영상을 발견했을 때 별도 앱으로 전환하지 않고 즉시 녹화할 수 있는 방식을 모색하는 것이었다. 이를 위해 Android Native Module 개발을 수행하였다. React Native에서 Kotlin으로 작성된 FloatingService를 호출할 수 있도록 FloatingWidgetModule을 구현하고, React Native와 Native Layer 간 통신을 위해 NativeEventEmitter를 활용한 이벤트 기반 브릿지를 설계하였다.

Android MediaProjection API의 특성상 사용자 권한 획득이 필수이므로, MainActivity에서 createScreenCaptureIntent를 통해 시스템 권한 다이얼로그를 띄우고 onActivityResult에서 결과를 받아 FloatingService로 전달하는 흐름을 설계하였다. Android 14 이상에서는 MediaProjection 사용 시 Foreground Service 타입 지정이 필수이므로, AndroidManifest.xml에 foregroundServiceType="mediaProjection"을 선언하고 FloatingService의 startForeground 호출을 서비스 시작 전에 수행하도록 설계하였다.

스크린 레코딩은 MediaRecorder와 VirtualDisplay를 조합하여 구현하였다. 비디오만 녹화하도록 설정하였으며, 해상도와 비트레이트를 에뮬레이터 환경에 맞게 조정하였다. 15초 자동 종료 기능을 구현하기 위해 Handler.postDelayed를 사용하여 타이머를 설정하고, 녹화 완료 시 React Native로 이벤트를 전달하도록 설계하였다.

녹화 완료 이벤트 전달 과정에서 React Native 컨텍스트가 준비되지 않은 경우를 대비하여 FloatingWidgetModule.sendRecordingCompleteEvent에 재시도 로직을 구현하였다. 최대 30회까지 200ms 간격으로 ReactApplicationContext를 확인하고, 준비되면 DeviceEventManagerModule.RCTDeviceEventEmitter를 통해 onRecordingComplete 이벤트를 발송하도록 설계하였다. 이는 앱이 백그라운드에 있을 때 발생할 수 있는 타이밍 문제를 해결하기 위한 설계이다.

### 2단계: 딥러닝 기반 딥페이크 탐지 엔진 구축

백엔드 분석 파이프라인은 FastAPI 프레임워크를 기반으로 구축하였다. 프론트엔드에서 FormData로 전송된 영상 파일을 UploadFile로 받아 임시 디렉토리에 저장한 후, OpenCV VideoCapture로 영상 정보(FPS, 총 프레임 수, 길이)를 추출하였다. 영상 길이에 따라 동적으로 프레임 추출 간격을 결정하는 로직을 구현하였다. 5초 이하 영상은 0.5초 간격, 10초 이하는 1초 간격, 30초 이하는 2초 간격, 30초 초과는 3초 간격으로 설정하여 짧은 영상은 상세 분석하고 긴 영상은 효율적으로 처리하도록 설계하였다.

OpenCV Haar Cascade 얼굴 감지기를 이용한 전처리 시스템을 설계하였다. cv2.data.haarcascades 경로의 haarcascade_frontalface_default.xml을 로드하여 각 프레임에 대해 얼굴을 감지하고, 얼굴이 감지된 프레임만 저장하도록 extract_frames 함수를 수정하였다. 얼굴이 전혀 감지되지 않은 경우 조기 종료하여 불필요한 분석을 방지하는 에러 응답을 반환하도록 설계하였다. 이는 사용자가 홈 화면 등 얼굴이 없는 영상을 업로드했을 때 명확한 피드백을 제공하기 위한 설계이다.

PyTorch와 Hugging Face Transformers를 활용한 딥러닝 모델 추론 시스템을 구현하였다. AutoImageProcessor.from_pretrained와 AutoModelForImageClassification.from_pretrained를 사용하여 두 개의 ViT 모델을 로드하였다. GPU 환경에서는 torch.float16을 사용하여 메모리를 절약하고, CPU 환경에서는 단일 모델만 사용하도록 조건부 로딩 로직을 구현하였다. 모델 로딩은 지연 로딩 방식으로 구현하여 서버 시작 시 메모리를 낭비하지 않도록 설계하였다.

앙상블 방식은 두 모델의 결과를 다수결로 결합하도록 설계하였다. predict_image 함수에서 각 모델의 예측 결과를 받아 ensemble_result를 "FAKE" if [label1, label2].count("FAKE") >= 1 else "REAL"로 결정하고, 평균 confidence를 계산하였다. ProcessPoolExecutor를 사용하여 프레임 분석을 병렬 처리함으로써 분석 속도를 향상시켰다. 배치 크기를 3개로 제한하여 메모리 사용량을 관리하고, 각 배치 처리 후 gc.collect()를 호출하여 메모리를 정리하도록 설계하였다.

정적 화면 보정 알고리즘을 analyze_video 엔드포인트에 구현하였다. total_frames가 5개 미만이고 fake_conf가 0.85 미만인 경우 정적 화면일 가능성이 높다고 판단하여 fake_conf를 원래 값의 60%로 감소시켰다. 이를 통해 홈 화면 등 얼굴이 없는 정적 화면이 딥페이크로 오판되는 것을 방지하였다. 이는 실제 테스트에서 발견된 문제를 해결하기 위해 추가한 보정 로직이다.

### 3단계: 분석 결과 처리 및 타임라인 생성 시스템 설계

프레임별 분석 결과를 시간 구간별로 그룹화하는 create_smart_timeline 함수를 설계하였다. 연속된 동일 결과를 하나의 세그먼트로 묶되, 최소 구간 길이(2초)를 유지하도록 should_split_segment 함수에서 판단 로직을 구현하였다. 세그먼트 내 프레임들의 confidence 평균을 계산하여 세그먼트 단위 confidence를 산출하였다. 이는 프레임 단위 분석 결과를 사용자가 이해하기 쉬운 구간 단위로 변환하기 위한 설계이다.

create_analysis_summary 함수를 설계하여 전체 분석 결과를 요약하였다. 타임라인의 세그먼트 중 FAKE와 REAL의 개수를 비교하여 전체 결과를 결정하고, 모든 세그먼트의 confidence 평균을 overall_confidence로 계산하였다. video_analysis 객체에는 전체 프레임 수, FAKE/REAL 프레임 개수, 보정된 overall_confidence를 포함시켰다. 이를 통해 프론트엔드에서 전체적인 분석 결과를 쉽게 파악할 수 있도록 설계하였다.

프론트엔드에서 백엔드 응답을 해석하여 딥페이크 확률을 계산하는 로직을 구현하였다. video_analysis.overall_confidence를 최우선으로 사용하고, 없으면 summary.overall_confidence, 그마저도 없으면 timeline의 FAKE 세그먼트 confidence를 평균하여 계산하도록 설계하였다. Math.round()를 사용하여 정수 퍼센트로 반올림하여 표시하였다. 이는 백엔드 응답 형식이 변경되어도 유연하게 대응할 수 있도록 설계한 fallback 메커니즘이다.

분석 결과 표시를 위한 React Native Modal 컴포넌트를 설계하였다. analyzing 상태일 때는 ActivityIndicator와 "분석 중" 메시지를 표시하고, analysisResult가 설정되면 확률 퍼센트와 "딥페이크 확률" 레이블을 표시하도록 구현하였다. "닫기"와 "데이터셋 다운로드" 버튼을 배치하여 사용자가 결과를 확인하고 데이터셋을 내려받을 수 있도록 설계하였다. Modal은 transparent 배경과 fade 애니메이션을 사용하여 사용자 경험을 개선하였다.

### 4단계: 텍스트 기반 데이터셋 내보내기 시스템 구현

데이터셋 생성 로직을 백엔드에 구현하였다. create_dataset_jsonl 함수를 설계하여 타임라인의 각 세그먼트를 순회하며 프레임별 또는 세그먼트별로 JSON 객체를 생성하고, 각 줄에 json.dumps로 직렬화하여 JSONL 형식으로 변환하였다. video_id, time, label, confidence, fake_confidence, real_confidence 등 학습에 필요한 필드를 포함시켰다. 프레임 정보가 있는 경우 프레임 단위로, 없는 경우 세그먼트 단위로 데이터를 생성하도록 설계하였다.

create_timeline_csv 함수를 설계하여 Python의 csv.writer를 사용하여 타임라인 정보를 CSV 형식으로 변환하였다. StringIO를 사용하여 메모리에서 CSV 문자열을 생성하고, UTF-8 BOM('\ufeff')을 추가하여 Excel 호환성을 확보하였다. segment_id, start, end, result, confidence, frame_count, duration 컬럼으로 구성하였다. 이는 Excel에서 바로 열어볼 수 있도록 설계한 사용자 친화적 형식이다.

create_metadata_json 함수를 설계하여 영상 정보, 분석 요약, 비디오 분석 결과를 구조화된 JSON 딕셔너리로 생성하였다. json.dumps에 ensure_ascii=False와 indent=2 옵션을 적용하여 한글이 깨지지 않고 가독성 좋은 JSON 문자열을 생성하도록 구현하였다. video_info, summary, video_analysis 세 가지 주요 섹션으로 구성하여 구조화된 메타데이터를 제공하도록 설계하였다.

FastAPI 엔드포인트를 세 개로 분리하여 각 파일 형식별로 개별 다운로드를 제공하도록 설계하였다. /dataset/{video_id}/jsonl, /dataset/{video_id}/csv, /dataset/{video_id}/metadata 엔드포인트를 구현하고, 각각 FastAPI Response 객체를 반환하여 Content-Disposition 헤더로 파일명을 지정하도록 설계하였다. 텍스트 기반 파일이므로 ZIP 압축 없이 직접 다운로드 가능하도록 구현하였다. 이는 모바일 환경에서 압축 해제 과정 없이 바로 파일을 확인할 수 있도록 설계한 사용자 경험 개선이다.

프론트엔드 다운로드 로직을 구현하였다. downloadDataset 함수에서 fileType 파라미터를 받아 해당 파일 형식의 다운로드 URL을 생성하도록 설계하였다. RecordScreen과 UploadScreen의 "데이터셋 다운로드" 버튼 클릭 시 jsonl, csv, metadata 세 가지 파일을 순차적으로 다운로드하도록 for 루프를 사용하였고, 각 파일 사이에 500ms 딜레이를 두어 브라우저에서 순차적으로 다운로드가 시작되도록 구현하였다. React Native Linking.canOpenURL과 Linking.openURL을 사용하여 각 다운로드 URL을 브라우저에서 열도록 설계하였다. 이는 모바일 브라우저의 다운로드 매니저를 활용하여 파일을 저장하는 방식이다.
