"""
MesoNet 백엔드
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import cv2
import numpy as np
from pathlib import Path
import threading
import time

from app.core.config import MESONET_WEIGHTS, IMAGE_SIZE, TORCH_NUM_THREADS, CV2_NUM_THREADS

# CPU 스레드 설정
torch.set_num_threads(TORCH_NUM_THREADS)
cv2.setNumThreads(CV2_NUM_THREADS)

class Meso4(nn.Module):
    """MesoNet-4 모델 구조 (256x256 입력용, 튜닝된 버전)"""
    def __init__(self, num_classes=2, dropout_rate=0.4):
        super(Meso4, self).__init__()
        
        # 첫 번째 블록
        self.conv1 = nn.Conv2d(3, 8, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(8)
        self.conv2 = nn.Conv2d(8, 8, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm2d(8)
        self.pool1 = nn.MaxPool2d(2, 2)  # 256 -> 128
        self.drop1 = nn.Dropout2d(dropout_rate)
        
        # 두 번째 블록
        self.conv3 = nn.Conv2d(8, 16, kernel_size=5, padding=2)
        self.bn3 = nn.BatchNorm2d(16)
        self.conv4 = nn.Conv2d(16, 16, kernel_size=5, padding=2)
        self.bn4 = nn.BatchNorm2d(16)
        self.pool2 = nn.MaxPool2d(2, 2)  # 128 -> 64
        self.drop2 = nn.Dropout2d(dropout_rate)
        
        # 세 번째 블록
        self.conv5 = nn.Conv2d(16, 16, kernel_size=5, padding=2)
        self.bn5 = nn.BatchNorm2d(16)
        self.conv6 = nn.Conv2d(16, 16, kernel_size=5, padding=2)
        self.bn6 = nn.BatchNorm2d(16)
        self.pool3 = nn.MaxPool2d(2, 2)  # 64 -> 32
        self.drop3 = nn.Dropout2d(dropout_rate)
        
        # Fully Connected (256x256 -> 32x32 after 3 pools)
        self.fc1 = nn.Linear(16 * 32 * 32, 16)
        self.bn7 = nn.BatchNorm1d(16)
        self.drop4 = nn.Dropout(dropout_rate)
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

class MesoNetBackend:
    """MesoNet 백엔드"""
    
    def __init__(self):
        self.model = None
        self.device = torch.device("cpu")
        # 튜닝된 모델에 맞는 전처리 (학습 시 사용한 것과 동일)
        # Resize(256, 256) + ToTensor() + Normalize(-1~1)
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),  # 튜닝된 모델 입력 크기
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # -1~1 정규화
        ])
        self.loading_lock = threading.Lock()
        self.model_loaded = False
    
    def load_model(self):
        """모델 로드"""
        if self.model_loaded:
            return True
            
        with self.loading_lock:
            if self.model_loaded:
                return True
                
            try:
                # 모델 구조 생성 (튜닝된 모델: 256x256 입력, dropout=0.4)
                self.model = Meso4(num_classes=2, dropout_rate=0.4)
                
                # 모델 파일 확인 및 로드
                if not Path(MESONET_WEIGHTS).exists():
                    print(f"⚠ 경고: MesoNet 모델 파일을 찾을 수 없습니다: {MESONET_WEIGHTS}")
                    print(f"⚠ 랜덤 초기화된 모델을 사용합니다. 성능이 저하될 수 있습니다.")
                    print(f"💡 모델 파일을 설정하려면:")
                    print(f"   1. 기존 컴퓨터에서 backend/weights/best_model_tuned.pt 파일을 복사")
                    print(f"   2. 또는 python backend/download_models.py 실행")
                    self.model.to(self.device).eval()
                    self.model_loaded = True
                    return True
                
                # 가중치 로드
                checkpoint = torch.load(MESONET_WEIGHTS, map_location=self.device)
                
                # 체크포인트 구조에 따라 가중치 로드
                if isinstance(checkpoint, dict):
                    if 'model_state_dict' in checkpoint:
                        state_dict = checkpoint['model_state_dict']
                    elif 'state_dict' in checkpoint:
                        state_dict = checkpoint['state_dict']
                    elif 'model' in checkpoint:
                        state_dict = checkpoint['model']
                    else:
                        state_dict = checkpoint
                else:
                    state_dict = checkpoint
                
                # state_dict 키 정리
                cleaned_state_dict = {}
                for k, v in state_dict.items():
                    new_key = k.replace('module.', '').replace('model.', '')
                    cleaned_state_dict[new_key] = v
                
                self.model.load_state_dict(cleaned_state_dict, strict=True)
                self.model.to(self.device)
                self.model.eval()
                
                self.model_loaded = True
                return True
                
            except Exception as e:
                print(f"[MesoNet] 모델 로딩 실패: {e}")
                self.model = None
                self.model_loaded = False
                return False
    
    def preprocess_image(self, image_path: str, face_crop: bool = True):
        """
        이미지 전처리 (얼굴 crop + 256x256 리사이즈)
        
        Args:
            image_path: 이미지 파일 경로
            face_crop: 얼굴 crop 사용 여부
        
        Returns:
            tuple: (전처리된 이미지 텐서, 얼굴_감지_여부)
        """
        try:
            # 이미지 로드
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"이미지를 로드할 수 없습니다: {image_path}")
            
            # BGR -> RGB 변환
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 얼굴 crop (옵션)
            face_detected = True
            if face_crop:
                image, face_detected = self._crop_face(image)
            
            # PIL Image로 변환
            pil_image = Image.fromarray(image)
            
            # 리사이즈 및 정규화
            image_tensor = self.transform(pil_image).unsqueeze(0)
            
            return image_tensor.to(self.device), face_detected
            
        except Exception as e:
            print(f"[MesoNet] 이미지 전처리 오류: {e}")
            raise
    
    def _crop_face(self, image: np.ndarray):
        """얼굴 영역 crop (화면 녹화 영상에 최적화)
        
        Returns:
            tuple: (cropped_image, face_detected)
                - cropped_image: crop된 이미지
                - face_detected: 얼굴 감지 여부 (bool)
        """
        try:
            # Haar Cascade 얼굴 감지
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            h, w = image.shape[:2]
            
            # 여러 파라미터로 얼굴 감지 시도 (화면 녹화 영상의 경우 UI 오버레이로 인해 감지가 어려울 수 있음)
            face_detection_params = [
                # 파라미터 세트 1: 기본 (가장 엄격)
                {
                    'scaleFactor': 1.1,
                    'minNeighbors': 5,
                    'minSize': (max(30, int(min(h, w) * 0.05)), max(30, int(min(h, w) * 0.05)))
                },
                # 파라미터 세트 2: 더 완화 (작은 얼굴도 감지)
                {
                    'scaleFactor': 1.05,
                    'minNeighbors': 3,
                    'minSize': (max(20, int(min(h, w) * 0.03)), max(20, int(min(h, w) * 0.03)))
                },
                # 파라미터 세트 3: 가장 완화 (UI 오버레이가 있어도 감지)
                {
                    'scaleFactor': 1.05,
                    'minNeighbors': 2,
                    'minSize': (max(15, int(min(h, w) * 0.02)), max(15, int(min(h, w) * 0.02)))
                }
            ]
            
            all_faces = []
            for params in face_detection_params:
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=params['scaleFactor'],
                    minNeighbors=params['minNeighbors'],
                    minSize=params['minSize'],
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                if len(faces) > 0:
                    all_faces.extend(faces)
            
            # 중복 제거 (겹치는 얼굴 제거)
            if len(all_faces) > 0:
                # 가장 큰 얼굴 선택
                largest_face = max(all_faces, key=lambda x: x[2] * x[3])
                x, y, w_face, h_face = largest_face
                
                # 얼굴 크기 검증: 얼굴이 이미지의 최소 1% 이상을 차지해야 함 (2% -> 1%로 완화)
                face_area = w_face * h_face
                image_area = h * w
                face_ratio = face_area / image_area
                
                if face_ratio < 0.01:  # 얼굴이 너무 작으면 무시
                    # 얼굴이 감지되지 않음으로 처리
                    size = min(h, w)
                    y = (h - size) // 2
                    x = (w - size) // 2
                    return image[y:y+size, x:x+size], False
                
                # 얼굴 비율 검증: 얼굴의 가로/세로 비율이 0.4~2.5 범위여야 함 (0.5~2.0 -> 0.4~2.5로 완화)
                face_aspect_ratio = w_face / h_face if h_face > 0 else 0
                if face_aspect_ratio < 0.4 or face_aspect_ratio > 2.5:
                    # 비율이 이상하면 얼굴이 아닐 가능성 높음
                    size = min(h, w)
                    y = (h - size) // 2
                    x = (w - size) // 2
                    return image[y:y+size, x:x+size], False
                
                # 여유 공간 추가 (20%)
                margin = int(min(w_face, h_face) * 0.2)
                x = max(0, x - margin)
                y = max(0, y - margin)
                w_face = min(image.shape[1] - x, w_face + 2 * margin)
                h_face = min(image.shape[0] - y, h_face + 2 * margin)
                
                # 얼굴 영역 crop
                face_image = image[y:y+h_face, x:x+w_face]
                return face_image, True
            else:
                # 얼굴이 감지되지 않으면 중앙 crop
                size = min(h, w)
                y = (h - size) // 2
                x = (w - size) // 2
                return image[y:y+size, x:x+size], False
                
        except Exception as e:
            print(f"[MesoNet] 얼굴 crop 오류: {e}, 원본 이미지 사용")
            return image, False
    
    def predict(self, image_path: str, face_crop: bool = True):
        """
        이미지 예측
        
        Args:
            image_path: 이미지 파일 경로
            face_crop: 얼굴 crop 사용 여부
        
        Returns:
            예측 결과 딕셔너리 (face_detected 필드 포함)
        """
        if not self.model_loaded:
            if not self.load_model():
                return {"error": "모델 로딩 실패"}
        
        try:
            # 이미지 전처리 (얼굴 감지 여부 포함)
            image_tensor, face_detected = self.preprocess_image(image_path, face_crop=face_crop)
            
            # 얼굴이 감지되지 않으면 신뢰도 낮은 REAL로 처리
            if not face_detected:
                return {
                    "label": "REAL",
                    "score": 0.0,  # 신뢰도 0
                    "fake_prob": 0.0,  # FAKE 확률 0
                    "real_prob": 1.0,  # REAL 확률 1.0 (의미 없음)
                    "model": "MesoNet",
                    "face_detected": False,
                    "warning": "얼굴이 감지되지 않아 계산에서 제외됩니다"
                }
            
            # 추론
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probs = F.softmax(outputs, dim=1)
                fake_prob = probs[0][1].item()  # FAKE 클래스 확률
                real_prob = probs[0][0].item()  # REAL 클래스 확률
                confidence = max(fake_prob, real_prob)
                label = "FAKE" if fake_prob > 0.5 else "REAL"
            
            return {
                "label": label,
                "score": float(confidence),
                "fake_prob": float(fake_prob),
                "real_prob": float(real_prob),
                "model": "MesoNet",
                "face_detected": True
            }
            
        except Exception as e:
            print(f"[MesoNet] 예측 오류: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}


