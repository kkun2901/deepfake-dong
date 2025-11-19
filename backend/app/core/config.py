"""
백엔드 설정 파일
"""
import os
from pathlib import Path

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).parent.parent.parent

# 모델 가중치 경로
WEIGHTS_DIR = BASE_DIR / "weights"
WEIGHTS_DIR.mkdir(exist_ok=True)

# EfficientNet-B0 (DFDC) 모델 경로
EFFICIENTNET_WEIGHTS = str(WEIGHTS_DIR / "effb0_dfdc.pth")

# MesoNet 모델 경로 (튜닝된 PyTorch .pt 파일)
MESONET_WEIGHTS = str(WEIGHTS_DIR / "best_model_tuned.pt")
# 기존 모델 (백업용)
MESONET_WEIGHTS_OLD = str(WEIGHTS_DIR / "Meso4_DF.h5")

# 프레임 샘플링 설정
FRAME_SAMPLES = 10  # 추출할 프레임 수

# 얼굴 crop 사용 여부
USE_FACE_CROP = True  # 고해상도(720~1080p) 영상일 경우 필수

# 이미지 리사이즈 크기
IMAGE_SIZE = 256  # 튜닝된 MesoNet 입력 크기 (256x256)

# 앙상블 가중치
ENSEMBLE_WEIGHT_EFFICIENTNET = 0.7
ENSEMBLE_WEIGHT_MESONET = 0.3

# CPU 스레드 설정
TORCH_NUM_THREADS = 4
CV2_NUM_THREADS = 1

# 모델 로딩 확인
def check_models():
    """모델 파일 존재 여부 확인"""
    eff_exists = os.path.exists(EFFICIENTNET_WEIGHTS)
    meso_exists = os.path.exists(MESONET_WEIGHTS)
    
    return {
        "efficientnet": eff_exists,
        "mesonet": meso_exists,
        "all_ready": eff_exists and meso_exists
    }

