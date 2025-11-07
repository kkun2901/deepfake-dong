import cv2
import os
import numpy as np

# 얼굴 감지용 Haar Cascade 로더 (한 번만 로드)
_face_cascade = None

def load_face_detector():
    """얼굴 감지기 로드 (한 번만 로드)"""
    global _face_cascade
    if _face_cascade is None:
        try:
            # OpenCV의 기본 얼굴 감지 모델 사용
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            _face_cascade = cv2.CascadeClassifier(cascade_path)
            if _face_cascade.empty():
                print("경고: Haar Cascade 로드 실패, 얼굴 감지 비활성화")
                return None
            print("얼굴 감지기 로드 완료")
        except Exception as e:
            print(f"얼굴 감지기 로드 실패: {e}")
            return None
    return _face_cascade

def detect_faces_in_frame(frame):
    """프레임에서 얼굴 감지"""
    face_cascade = load_face_detector()
    if face_cascade is None:
        # 얼굴 감지 실패 시 모든 프레임 허용 (기존 동작 유지)
        return True
    
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),  # 최소 얼굴 크기
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return len(faces) > 0
    except Exception as e:
        print(f"얼굴 감지 중 오류: {e}")
        return True  # 오류 시 프레임 허용

def extract_frames(video_path: str, output_dir: str, frame_rate: float = 0.2, face_detection: bool = True):
    """
    영상에서 일정 간격으로 프레임 추출 (기본: 5fps), 각 프레임의 타임스탬프 포함
    
    Args:
        video_path: 비디오 파일 경로
        output_dir: 프레임 저장 디렉토리
        frame_rate: 프레임 추출 간격 (초)
        face_detection: 얼굴 감지 활성화 여부 (True면 얼굴이 있는 프레임만 추출)
    
    Returns:
        추출된 프레임 정보 리스트 (path, time 포함)
    """
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * frame_rate) if fps > 0 else 1

    frame_count = 0
    saved_frames = []
    total_checked = 0
    face_detected_count = 0
    
    print(f"프레임 추출 시작 (얼굴 감지: {'활성화' if face_detection else '비활성화'})...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            total_checked += 1
            frame_time = frame_count / fps if fps > 0 else 0  # 현재 프레임의 시간(초)
            
            # 얼굴 감지 활성화 시 얼굴이 있는 프레임만 저장
            if face_detection:
                has_face = detect_faces_in_frame(frame)
                if not has_face:
                    frame_count += 1
                    continue
                face_detected_count += 1
            
            frame_filename = os.path.join(output_dir, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_filename, frame)
            saved_frames.append({"path": frame_filename, "time": round(frame_time, 2)})
        
        frame_count += 1
    
    cap.release()
    
    # 얼굴 감지 통계 출력
    if face_detection and total_checked > 0:
        face_ratio = (face_detected_count / total_checked) * 100
        print(f"프레임 추출 완료: {len(saved_frames)}개 프레임 저장")
        print(f"얼굴 감지 통계: {face_detected_count}/{total_checked}개 프레임에 얼굴 감지 ({face_ratio:.1f}%)")
        
        # 얼굴이 감지된 프레임이 너무 적으면 경고
        if face_ratio < 30 and len(saved_frames) < 3:
            print(f"경고: 얼굴이 감지된 프레임이 매우 적습니다 ({face_ratio:.1f}%). 분석 정확도가 낮을 수 있습니다.")
    
    return saved_frames
