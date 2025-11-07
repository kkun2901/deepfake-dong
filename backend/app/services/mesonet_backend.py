"""
MesoNet 백엔드 (TensorFlow/Keras)
"""
import cv2
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
import threading
import time

from app.core.config import MESONET_WEIGHTS, FRAME_SAMPLES, USE_FACE_CROP

# MesoNet 입력 크기 (256x256)
MESONET_INPUT_SIZE = 256

# TensorFlow는 지연 로딩 (lazy import)
_tf = None
_tf_loaded = False

def _get_tensorflow():
    """TensorFlow/Keras 지연 로딩 (여러 방법 시도)"""
    global _tf, _tf_loaded
    if not _tf_loaded:
        # 방법 1: TensorFlow를 통한 Keras (환경 변수 설정 후 시도)
        try:
            import os
            import sys
            
            # sys.path 정리: 잘못된 경로 제거하고 올바른 경로만 사용
            current_python = sys.executable
            print(f"[DEBUG] Python 실행 파일: {current_python}")
            
            # 현재 Python 실행 파일 기반으로 올바른 site-packages 경로 찾기
            if 'venv' in current_python or 'Scripts' in current_python:
                # 가상환경인 경우
                venv_base = os.path.dirname(os.path.dirname(current_python))
                correct_site_packages = os.path.join(venv_base, 'Lib', 'site-packages')
                if os.path.exists(correct_site_packages):
                    # 잘못된 경로 제거 (Downloads 폴더의 경로)
                    sys.path = [p for p in sys.path if 'Downloads' not in p]
                    # 올바른 경로를 맨 앞에 추가
                    if correct_site_packages not in sys.path:
                        sys.path.insert(0, correct_site_packages)
                    print(f"[DEBUG] 올바른 site-packages 경로 추가: {correct_site_packages}")
            
            # Windows 경로 문제 해결을 위한 환경 변수
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 경고 메시지 억제
            
            # TensorFlow import 전에 sys.path 확인
            print(f"[DEBUG] sys.path (처음 5개):")
            for i, p in enumerate(sys.path[:5]):
                print(f"  {i}: {p}")
            
            import tensorflow as tf
            print(f"[DEBUG] TensorFlow 로드 성공: {tf.__file__}")
            
            # CPU 전용 설정
            tf.config.set_visible_devices([], 'GPU')  # GPU 비활성화
            tf.config.threading.set_intra_op_parallelism_threads(4)
            tf.config.threading.set_inter_op_parallelism_threads(2)
            _tf = tf
            _tf_loaded = True
            print("✓ TensorFlow를 통한 Keras 사용")
            return _tf
        except Exception as e1:
            print(f"✗ TensorFlow 로딩 실패: {e1}")
            import traceback
            traceback.print_exc()
            print(f"[DEBUG] 현재 sys.path:")
            for i, p in enumerate(sys.path):
                print(f"  {i}: {p}")
            raise ImportError(
                f"TensorFlow를 로드할 수 없습니다.\n"
                f"오류: {e1}\n"
                f"해결 방법:\n"
                f"1. TensorFlow 2.16 버전 설치: pip uninstall tensorflow-cpu -y && pip install tensorflow-cpu==2.16.1\n"
                f"2. 또는 가상환경을 더 짧은 경로에 재생성"
            )
    return _tf

# 전역 모델 변수
meso_model = None
model_loaded = False
loading_lock = threading.Lock()

def load_face_detector():
    """얼굴 감지기 로드 (MediaPipe 또는 OpenCV)"""
    try:
        import mediapipe as mp
        mp_face = mp.solutions.face_detection.FaceDetection(
            model_selection=1, 
            min_detection_confidence=0.5
        )
        return mp_face, 'mediapipe'
    except ImportError:
        # MediaPipe 없으면 OpenCV Haar Cascade 사용
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        if face_cascade.empty():
            return None, None
        return face_cascade, 'opencv'

_face_detector = None
_face_detector_type = None

def get_face_detector():
    """얼굴 감지기 싱글톤"""
    global _face_detector, _face_detector_type
    if _face_detector is None:
        _face_detector, _face_detector_type = load_face_detector()
    return _face_detector, _face_detector_type

def maybe_face_crop(img: np.ndarray, enable: bool = True) -> np.ndarray:
    """얼굴 crop (선택적)"""
    if not enable:
        return img
    
    detector, detector_type = get_face_detector()
    if detector is None:
        return img
    
    try:
        if detector_type == 'mediapipe':
            # MediaPipe 사용
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb_img)
            if results.detections:
                h, w = img.shape[:2]
                b = results.detections[0].location_data.relative_bounding_box
                x = int(b.xmin * w)
                y = int(b.ymin * h)
                w2 = int(b.width * w)
                h2 = int(b.height * h)
                # 여유 공간 추가 (20%)
                margin = int(min(w2, h2) * 0.2)
                x = max(0, x - margin)
                y = max(0, y - margin)
                w2 = min(img.shape[1] - x, w2 + 2 * margin)
                h2 = min(img.shape[0] - y, h2 + 2 * margin)
                return img[y:y+h2, x:x+w2]
        elif detector_type == 'opencv':
            # OpenCV Haar Cascade 사용
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            if len(faces) > 0:
                # 가장 큰 얼굴 선택
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_face
                # 여유 공간 추가 (20%)
                margin = int(min(w, h) * 0.2)
                x = max(0, x - margin)
                y = max(0, y - margin)
                w = min(img.shape[1] - x, w + 2 * margin)
                h = min(img.shape[0] - y, h + 2 * margin)
                return img[y:y+h, x:x+w]
    except Exception as e:
        print(f"얼굴 crop 오류: {e}, 원본 이미지 사용")
    
    # 얼굴 미감지 시 중앙 crop
    h, w = img.shape[:2]
    size = min(h, w)
    y = (h - size) // 2
    x = (w - size) // 2
    return img[y:y+size, x:x+size]

def sample_frames(video_path: str, num_samples: int = 10) -> List[tuple]:
    """
    영상에서 프레임 샘플링
    
    Returns:
        List[tuple]: (frame, timestamp) 리스트
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []
    
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = cap.get(cv2.CAP_PROP_FPS) or 1.0
    
    if total <= 0:
        cap.release()
        return []
    
    # 균등하게 샘플링
    if num_samples == 1:
        idxs = [0]
    else:
        idxs = [round(i * (total - 1) / max(1, num_samples - 1)) for i in range(num_samples)]
    
    frames = []
    for idx in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if ok:
            timestamp = idx / fps if fps > 0 else 0
            frames.append((frame, timestamp))
    
    cap.release()
    return frames

def _build_mesonet_model():
    """MesoNet 모델 구조 정의 (Meso4)"""
    tf = _get_tensorflow()
    from tensorflow.keras.layers import Input, Dense, Flatten, Conv2D, MaxPooling2D, BatchNormalization, Dropout, LeakyReLU
    
    # Meso4 모델 구조 (256x256 입력)
    x = Input(shape=(MESONET_INPUT_SIZE, MESONET_INPUT_SIZE, 3))
    
    x1 = Conv2D(8, (3, 3), padding='same', activation='relu')(x)
    x1 = BatchNormalization()(x1)
    x1 = MaxPooling2D(pool_size=(2, 2), padding='same')(x1)
    
    x2 = Conv2D(8, (5, 5), padding='same', activation='relu')(x1)
    x2 = BatchNormalization()(x2)
    x2 = MaxPooling2D(pool_size=(2, 2), padding='same')(x2)
    
    x3 = Conv2D(16, (5, 5), padding='same', activation='relu')(x2)
    x3 = BatchNormalization()(x3)
    x3 = MaxPooling2D(pool_size=(2, 2), padding='same')(x3)
    
    x4 = Conv2D(16, (5, 5), padding='same', activation='relu')(x3)
    x4 = BatchNormalization()(x4)
    x4 = MaxPooling2D(pool_size=(4, 4), padding='same')(x4)
    
    y = Flatten()(x4)
    y = Dropout(0.5)(y)
    y = Dense(16)(y)
    y = LeakyReLU(negative_slope=0.1)(y)
    y = Dropout(0.5)(y)
    y = Dense(1, activation='sigmoid')(y)
    
    model = tf.keras.Model(inputs=x, outputs=y)
    return model

def load_model():
    """모델 로드 (스레드 안전)"""
    global meso_model, model_loaded
    
    if model_loaded:
        return True
    
    with loading_lock:
        if model_loaded:
            return True
        
        try:
            print("=" * 60)
            print("MesoNet 모델 로딩 시작...")
            print("=" * 60)
            start_time = time.time()
            
            weights_path = Path(MESONET_WEIGHTS)
            if not weights_path.exists():
                raise FileNotFoundError(
                    f"MesoNet 모델 파일을 찾을 수 없습니다: {MESONET_WEIGHTS}\n"
                    f"파일 경로: {weights_path.absolute()}"
                )
            
            print(f"모델 파일: {weights_path.absolute()}")
            tf = _get_tensorflow()
            
            # 모델 구조 생성
            print("MesoNet 모델 구조 생성 중...")
            meso_model = _build_mesonet_model()
            
            # 가중치만 로드
            print("가중치 파일 로딩 중...")
            meso_model.load_weights(str(weights_path))
            print("✓ 가중치 로딩 완료!")
            
            loading_time = time.time() - start_time
            print("=" * 60)
            print(f"MesoNet 모델 로딩 완료! (소요시간: {loading_time:.2f}초)")
            print(f"프레임 샘플링: {FRAME_SAMPLES}개")
            print(f"얼굴 crop: {'활성화' if USE_FACE_CROP else '비활성화'}")
            print("=" * 60)
            
            model_loaded = True
            return True
            
        except Exception as e:
            print(f"MesoNet 모델 로딩 실패: {e}")
            import traceback
            traceback.print_exc()
            meso_model = None
            model_loaded = False
            return False

def ensure_model_loaded():
    """모델 로딩 확인"""
    if not model_loaded:
        return load_model()
    return True

def _prep_image(img: np.ndarray) -> np.ndarray:
    """이미지 전처리 (얼굴 crop + 리사이즈)"""
    # 얼굴 crop
    if USE_FACE_CROP:
        img = maybe_face_crop(img, enable=True)
    
    # 리사이즈 (MesoNet은 256x256 입력)
    img = cv2.resize(img, (MESONET_INPUT_SIZE, MESONET_INPUT_SIZE))
    
    # 정규화 [0, 1]
    img = img.astype(np.float32) / 255.0
    
    return img

def predict_image(image_path: str) -> Dict:
    """이미지 예측"""
    if not ensure_model_loaded():
        return {"error": "모델 로딩 실패"}
    
    try:
        # 이미지 로드
        img = cv2.imread(image_path)
        if img is None:
            return {"error": f"이미지 로드 실패: {image_path}"}
        
        # 전처리
        preprocessed = _prep_image(img)
        
        # 예측
        x = np.expand_dims(preprocessed, axis=0)
        y = meso_model.predict(x, verbose=0)
        
        # 결과 처리
        if y.shape[-1] == 2:
            # 2개 클래스 (real, fake)
            fake_prob = float(y[0][1])
        else:
            # 1개 클래스 (fake 확률)
            fake_prob = float(y[0][0])
        
        label = "FAKE" if fake_prob >= 0.5 else "REAL"
        confidence = max(fake_prob, 1.0 - fake_prob)
        
        return {
            "ensemble_result": label,
            "confidence": round(confidence, 4),
            "fake_confidence": round(fake_prob, 4),
            "real_confidence": round(1.0 - fake_prob, 4),
            "meta": {
                "model": "MesoNet",
                "ensemble": False,
                "n_frames": 1
            }
        }
        
    except Exception as e:
        print(f"이미지 예측 오류: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def predict_frames(frames: List[tuple]) -> List[Dict]:
    """여러 프레임 예측"""
    if not ensure_model_loaded():
        # 오류가 있어도 기본 구조 반환
        return [{
            "error": "모델 로딩 실패",
            "ensemble_result": "REAL",
            "confidence": 0.0,
            "fake_confidence": 0.0,
            "real_confidence": 1.0,
            "time": timestamp if len(frames) > 0 else 0.0,
            "meta": {"model": "MesoNet", "error": True}
        } for _, timestamp in frames] if frames else []
    
    if not frames:
        return []
    
    try:
        # 전처리
        preprocessed = [_prep_image(frame) for frame, _ in frames]
        x = np.stack(preprocessed, axis=0)
        
        # 예측
        y = meso_model.predict(x, verbose=0)
        
        # 결과 처리
        results = []
        if y.shape[-1] == 2:
            # 2개 클래스
            fake_probs = y[:, 1].astype(float)
        else:
            # 1개 클래스
            fake_probs = y.squeeze(-1).astype(float)
        
        for i, (frame, timestamp) in enumerate(frames):
            fake_prob = float(fake_probs[i])
            label = "FAKE" if fake_prob >= 0.5 else "REAL"
            confidence = max(fake_prob, 1.0 - fake_prob)
            
            results.append({
                "ensemble_result": label,
                "confidence": round(confidence, 4),
                "fake_confidence": round(fake_prob, 4),
                "real_confidence": round(1.0 - fake_prob, 4),
                "time": round(timestamp, 2),
                "meta": {
                    "model": "MesoNet"
                }
            })
        
        return results
        
    except Exception as e:
        print(f"프레임 예측 오류: {e}")
        import traceback
        traceback.print_exc()
        return [{"error": str(e)}]

