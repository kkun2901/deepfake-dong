"""
EfficientNet-B0 (DFDC) + MesoNet 앙상블 딥페이크 탐지 모델
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import cv2
import numpy as np
import threading
import time
import gc
from pathlib import Path

from app.core.config import (
    EFFICIENTNET_WEIGHTS, MESONET_WEIGHTS, IMAGE_SIZE,
    ENSEMBLE_WEIGHT_EFFICIENTNET, ENSEMBLE_WEIGHT_MESONET,
    USE_FACE_CROP, TORCH_NUM_THREADS, CV2_NUM_THREADS
)

# CPU 스레드 설정
torch.set_num_threads(TORCH_NUM_THREADS)
cv2.setNumThreads(CV2_NUM_THREADS)

device = torch.device("cpu")  # CPU 전용

# ==================== EfficientNet-B0 모델 ====================

def _load_efficientnet_model():
    """EfficientNet-B0 모델 구조 생성"""
    try:
        from efficientnet_pytorch import EfficientNet
        # ImageNet pretrained 모델 사용 (DFDC pretrained가 없을 경우)
        model = EfficientNet.from_pretrained('efficientnet-b0', num_classes=1000)
        # 마지막 레이어를 2개 클래스로 변경
        model._fc = nn.Linear(model._fc.in_features, 2)
        return model
    except ImportError:
        try:
            import timm
            # timm 사용 시 ImageNet pretrained 사용
            return timm.create_model('efficientnet_b0', pretrained=True, num_classes=2)
        except ImportError:
            raise ImportError(
                "efficientnet-pytorch 또는 timm 패키지가 필요합니다.\n"
                "설치: pip install efficientnet-pytorch 또는 pip install timm"
            )

# ==================== MesoNet 모델 ====================

class Meso4(nn.Module):
    """MesoNet 모델 구조 (Meso4)"""
    def __init__(self, num_classes=2):
        super(Meso4, self).__init__()
        self.conv1 = nn.Conv2d(3, 8, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(8)
        self.conv2 = nn.Conv2d(8, 8, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm2d(8)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.drop1 = nn.Dropout2d(0.25)
        
        self.conv3 = nn.Conv2d(8, 16, kernel_size=5, padding=2)
        self.bn3 = nn.BatchNorm2d(16)
        self.conv4 = nn.Conv2d(16, 16, kernel_size=5, padding=2)
        self.bn4 = nn.BatchNorm2d(16)
        self.pool2 = nn.MaxPool2d(2, 2)
        self.drop2 = nn.Dropout2d(0.25)
        
        self.conv5 = nn.Conv2d(16, 16, kernel_size=5, padding=2)
        self.bn5 = nn.BatchNorm2d(16)
        self.conv6 = nn.Conv2d(16, 16, kernel_size=5, padding=2)
        self.bn6 = nn.BatchNorm2d(16)
        self.pool3 = nn.MaxPool2d(2, 2)
        self.drop3 = nn.Dropout2d(0.25)
        
        self.fc1 = nn.Linear(16 * 28 * 28, 16)  # 224/8 = 28
        self.bn7 = nn.BatchNorm1d(16)
        self.drop4 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(16, num_classes)
    
    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool1(x)
        x = self.drop1(x)
        
        x = F.relu(self.bn3(self.conv3(x)))
        x = F.relu(self.bn4(self.conv4(x)))
        x = self.pool2(x)
        x = self.drop2(x)
        
        x = F.relu(self.bn5(self.conv5(x)))
        x = F.relu(self.bn6(self.conv6(x)))
        x = self.pool3(x)
        x = self.drop3(x)
        
        x = x.view(x.size(0), -1)
        x = F.relu(self.bn7(self.fc1(x)))
        x = self.drop4(x)
        x = self.fc2(x)
        return x

# ==================== 전역 모델 변수 ====================

eff_model = None
meso_model = None
models_loaded = False
loading_lock = threading.Lock()

# EfficientNet 전처리 (ImageNet 정규화)
eff_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# MesoNet 전처리
meso_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

def _crop_face(image: np.ndarray):
    """얼굴 영역 crop"""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        if len(faces) > 0:
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            margin = int(min(w, h) * 0.2)
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(image.shape[1] - x, w + 2 * margin)
            h = min(image.shape[0] - y, h + 2 * margin)
            return image[y:y+h, x:x+w]
        else:
            # 얼굴 미감지 시 중앙 crop
            h, w = image.shape[:2]
            size = min(h, w)
            y, x = (h - size) // 2, (w - size) // 2
            return image[y:y+size, x:x+size]
    except Exception as e:
        print(f"얼굴 crop 오류: {e}, 원본 이미지 사용")
        return image

def load_models():
    """모델 로드 (스레드 안전)"""
    global eff_model, meso_model, models_loaded
    
    if models_loaded:
        return True
    
    with loading_lock:
        if models_loaded:
            return True
        
        print("=" * 60)
        print("EfficientNet-B0 + MesoNet 모델 로딩 시작...")
        print("=" * 60)
        start_time = time.time()
        
        try:
            # EfficientNet-B0 로드
            print(f"[1/2] EfficientNet-B0 로딩 중...")
            eff_model = _load_efficientnet_model()
            
            # DFDC pretrained 가중치가 있으면 로드, 없으면 ImageNet pretrained 사용
            if Path(EFFICIENTNET_WEIGHTS).exists():
                print(f"  - DFDC pretrained 가중치 로드: {EFFICIENTNET_WEIGHTS}")
                checkpoint = torch.load(EFFICIENTNET_WEIGHTS, map_location=device)
                
                if isinstance(checkpoint, dict):
                    state_dict = checkpoint.get('state_dict', checkpoint.get('model', checkpoint))
                else:
                    state_dict = checkpoint
                
                # 키 정리
                cleaned = {k.replace('module.', '').replace('model.', ''): v 
                          for k, v in state_dict.items()}
                eff_model.load_state_dict(cleaned, strict=False)
                print("  ✓ EfficientNet-B0 (DFDC pretrained) 로딩 완료")
            else:
                print(f"  - DFDC pretrained 가중치 없음, ImageNet pretrained 사용")
                print("  ⚠ 참고: DFDC pretrained 가중치를 사용하면 더 나은 성능을 기대할 수 있습니다.")
                print("  ✓ EfficientNet-B0 (ImageNet pretrained) 로딩 완료")
            
            eff_model.to(device).eval()
            
            # MesoNet 로드 (선택적)
            print(f"[2/2] MesoNet 로딩 중...")
            meso_model = Meso4(num_classes=2)
            
            # MesoNet 가중치가 있으면 로드, 없으면 랜덤 초기화
            if Path(MESONET_WEIGHTS).exists():
                print(f"  - MesoNet 가중치 로드: {MESONET_WEIGHTS}")
                checkpoint = torch.load(MESONET_WEIGHTS, map_location=device)
                
                if isinstance(checkpoint, dict):
                    state_dict = checkpoint.get('state_dict', checkpoint.get('model', checkpoint))
                else:
                    state_dict = checkpoint
                
                cleaned = {k.replace('module.', '').replace('model.', ''): v 
                          for k, v in state_dict.items()}
                meso_model.load_state_dict(cleaned, strict=False)
                print("  ✓ MesoNet 로딩 완료")
            else:
                print(f"  - MesoNet 가중치 없음, 랜덤 초기화 사용")
                print("  ⚠ 참고: MesoNet 가중치 없이는 앙상블 성능이 저하될 수 있습니다.")
                print("  ⚠ MesoNet 없이 EfficientNet만 사용하는 것을 권장합니다.")
                print("  ✓ MesoNet (랜덤 초기화) 로딩 완료")
            
            meso_model.to(device).eval()
            
            models_loaded = True
            loading_time = time.time() - start_time
            print("=" * 60)
            print(f"모델 로딩 완료! (소요시간: {loading_time:.2f}초)")
            eff_has_weights = Path(EFFICIENTNET_WEIGHTS).exists()
            meso_has_weights = Path(MESONET_WEIGHTS).exists()
            print(f"모델 상태:")
            print(f"  - EfficientNet-B0: {'DFDC pretrained' if eff_has_weights else 'ImageNet pretrained'}")
            print(f"  - MesoNet: {'Pretrained' if meso_has_weights else '랜덤 초기화 (권장하지 않음)'}")
            if not meso_has_weights:
                print(f"  ⚠ MesoNet 가중치가 없으므로 EfficientNet만 사용하는 것을 권장합니다.")
            print(f"앙상블 가중치: EfficientNet={ENSEMBLE_WEIGHT_EFFICIENTNET}, MesoNet={ENSEMBLE_WEIGHT_MESONET}")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"모델 로딩 실패: {e}")
            import traceback
            traceback.print_exc()
            eff_model = meso_model = None
            models_loaded = False
            return False

def ensure_models_loaded():
    """모델 로딩 확인"""
    if not models_loaded:
        return load_models()
    return True

def predict_image(image_path: str):
    """이미지 예측 (EfficientNet-B0 + MesoNet 앙상블)"""
    if not ensure_models_loaded():
        return {"error": "모델 로딩 실패"}
    
    try:
        # 이미지 로드 및 전처리
        image = cv2.imread(image_path)
        if image is None:
            return {"error": f"이미지 로드 실패: {image_path}"}
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 얼굴 crop
        if USE_FACE_CROP:
            image = _crop_face(image)
        
        pil_image = Image.fromarray(image)
        
        # EfficientNet 예측
        eff_input = eff_transform(pil_image).unsqueeze(0).to(device)
        with torch.no_grad():
            eff_output = eff_model(eff_input)
            eff_probs = F.softmax(eff_output, dim=1)
            eff_fake = eff_probs[0][1].item()
            eff_real = eff_probs[0][0].item()
        
        # MesoNet 예측 (가중치가 있을 때만)
        meso_has_weights = Path(MESONET_WEIGHTS).exists()
        if meso_has_weights:
            meso_input = meso_transform(pil_image).unsqueeze(0).to(device)
            with torch.no_grad():
                meso_output = meso_model(meso_input)
                meso_probs = F.softmax(meso_output, dim=1)
                meso_fake = meso_probs[0][1].item()
                meso_real = meso_probs[0][0].item()
            
            # 앙상블: 가중 평균
            ensemble_fake = (ENSEMBLE_WEIGHT_EFFICIENTNET * eff_fake) + (ENSEMBLE_WEIGHT_MESONET * meso_fake)
            meso_result = {
                "label": "FAKE" if meso_fake > 0.5 else "REAL",
                "confidence": round(max(meso_fake, meso_real), 4),
                "fake_prob": round(meso_fake, 4)
            }
        else:
            # MesoNet 가중치가 없으면 EfficientNet만 사용
            ensemble_fake = eff_fake
            meso_fake = 0.0
            meso_real = 0.0
            meso_result = None
        
        ensemble_real = 1.0 - ensemble_fake
        ensemble_confidence = max(ensemble_fake, ensemble_real)
        ensemble_label = "FAKE" if ensemble_fake > 0.5 else "REAL"
        
        # 메모리 정리
        del eff_input, eff_output, eff_probs
        if meso_has_weights:
            del meso_input, meso_output, meso_probs
        gc.collect()
        
        return {
            "ensemble_result": ensemble_label,
            "confidence": round(ensemble_confidence, 4),
            "fake_confidence": round(ensemble_fake, 4),
            "real_confidence": round(ensemble_real, 4),
            "meta": {
                "ensemble": True,
                "weights": {
                    "efficientnet": ENSEMBLE_WEIGHT_EFFICIENTNET,
                    "mesonet": ENSEMBLE_WEIGHT_MESONET
                },
                "models": {
                    "efficientnet": {
                        "label": "FAKE" if eff_fake > 0.5 else "REAL",
                        "confidence": round(max(eff_fake, eff_real), 4),
                        "fake_prob": round(eff_fake, 4)
                    },
                    "mesonet": meso_result if meso_result else {
                        "label": "N/A",
                        "confidence": 0.0,
                        "fake_prob": 0.0,
                        "note": "가중치 없음"
                    }
                }
            }
        }
        
    except Exception as e:
        print(f"이미지 예측 오류: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def predict_batch(images: list):
    """배치 예측 - 여러 이미지를 한 번에 처리"""
    if not ensure_models_loaded():
        return [{"error": "모델 로딩 실패"}] * len(images)
    
    results = []
    try:
        for image_path in images:
            result = predict_image(image_path)
            results.append(result)
    except Exception as e:
        print(f"배치 예측 오류: {e}")
        results = [{"error": str(e)}] * len(images)
    
    return results

def cleanup_memory():
    """메모리 정리"""
    gc.collect()
    if device.type == "cuda":
        torch.cuda.empty_cache()
        print("GPU 메모리 정리 완료")
    else:
        print("CPU 메모리 정리 완료")




