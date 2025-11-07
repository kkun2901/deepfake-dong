"""
EfficientNet-B0 (DFDC pretrained) 백엔드
"""
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import cv2
import numpy as np
from pathlib import Path
import threading
import time

from app.core.config import EFFICIENTNET_WEIGHTS, IMAGE_SIZE, TORCH_NUM_THREADS, CV2_NUM_THREADS

# CPU 스레드 설정
torch.set_num_threads(TORCH_NUM_THREADS)
cv2.setNumThreads(CV2_NUM_THREADS)

class EfficientNetB0Backend:
    """EfficientNet-B0 (DFDC pretrained) 백엔드"""
    
    def __init__(self):
        self.model = None
        self.device = torch.device("cpu")
        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.loading_lock = threading.Lock()
        self.model_loaded = False
        
    def _build_model(self):
        """EfficientNet-B0 모델 구조 생성"""
        try:
            # efficientnet-pytorch 사용
            from efficientnet_pytorch import EfficientNet
            model = EfficientNet.from_name('efficientnet-b0', num_classes=2)
            return model
        except ImportError:
            # timm 사용 (대안)
            try:
                import timm
                model = timm.create_model('efficientnet_b0', pretrained=False, num_classes=2)
                return model
            except ImportError:
                raise ImportError(
                    "efficientnet-pytorch 또는 timm 패키지가 필요합니다.\n"
                    "설치: pip install efficientnet-pytorch 또는 pip install timm"
                )
    
    def load_model(self):
        """모델 로드"""
        if self.model_loaded:
            return True
            
        with self.loading_lock:
            if self.model_loaded:
                return True
                
            try:
                print(f"[EfficientNet-B0] 모델 로딩 시작: {EFFICIENTNET_WEIGHTS}")
                start_time = time.time()
                
                # 모델 파일 확인
                if not Path(EFFICIENTNET_WEIGHTS).exists():
                    raise FileNotFoundError(
                        f"모델 파일을 찾을 수 없습니다: {EFFICIENTNET_WEIGHTS}\n"
                        f"다운로드 스크립트 실행: python download_models.py"
                    )
                
                # 모델 구조 생성
                self.model = self._build_model()
                
                # 가중치 로드
                checkpoint = torch.load(EFFICIENTNET_WEIGHTS, map_location=self.device)
                
                # 체크포인트 구조에 따라 가중치 로드
                if isinstance(checkpoint, dict):
                    if 'state_dict' in checkpoint:
                        state_dict = checkpoint['state_dict']
                    elif 'model' in checkpoint:
                        state_dict = checkpoint['model']
                    else:
                        state_dict = checkpoint
                else:
                    state_dict = checkpoint
                
                # state_dict 키 정리 (불필요한 prefix 제거)
                cleaned_state_dict = {}
                for k, v in state_dict.items():
                    new_key = k.replace('module.', '').replace('model.', '')
                    cleaned_state_dict[new_key] = v
                
                self.model.load_state_dict(cleaned_state_dict, strict=False)
                self.model.to(self.device)
                self.model.eval()
                
                loading_time = time.time() - start_time
                print(f"[EfficientNet-B0] 모델 로딩 완료! (소요시간: {loading_time:.2f}초)")
                self.model_loaded = True
                return True
                
            except Exception as e:
                print(f"[EfficientNet-B0] 모델 로딩 실패: {e}")
                import traceback
                traceback.print_exc()
                self.model = None
                self.model_loaded = False
                return False
    
    def preprocess_image(self, image_path: str, face_crop: bool = True):
        """
        이미지 전처리 (얼굴 crop + 224x224 리사이즈)
        
        Args:
            image_path: 이미지 파일 경로
            face_crop: 얼굴 crop 사용 여부
        
        Returns:
            전처리된 이미지 텐서
        """
        try:
            # 이미지 로드
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"이미지를 로드할 수 없습니다: {image_path}")
            
            # BGR -> RGB 변환
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 얼굴 crop (옵션)
            if face_crop:
                image = self._crop_face(image)
            
            # PIL Image로 변환
            pil_image = Image.fromarray(image)
            
            # 리사이즈 및 정규화
            image_tensor = self.transform(pil_image).unsqueeze(0)
            
            return image_tensor.to(self.device)
            
        except Exception as e:
            print(f"[EfficientNet-B0] 이미지 전처리 오류: {e}")
            raise
    
    def _crop_face(self, image: np.ndarray):
        """얼굴 영역 crop"""
        try:
            # Haar Cascade 얼굴 감지
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                # 가장 큰 얼굴 선택
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_face
                
                # 여유 공간 추가 (20%)
                margin = int(min(w, h) * 0.2)
                x = max(0, x - margin)
                y = max(0, y - margin)
                w = min(image.shape[1] - x, w + 2 * margin)
                h = min(image.shape[0] - y, h + 2 * margin)
                
                # 얼굴 영역 crop
                face_image = image[y:y+h, x:x+w]
                return face_image
            else:
                # 얼굴이 감지되지 않으면 중앙 crop
                h, w = image.shape[:2]
                size = min(h, w)
                y = (h - size) // 2
                x = (w - size) // 2
                return image[y:y+size, x:x+size]
                
        except Exception as e:
            print(f"[EfficientNet-B0] 얼굴 crop 오류: {e}, 원본 이미지 사용")
            return image
    
    def predict(self, image_path: str, face_crop: bool = True):
        """
        이미지 예측
        
        Args:
            image_path: 이미지 파일 경로
            face_crop: 얼굴 crop 사용 여부
        
        Returns:
            예측 결과 딕셔너리
        """
        if not self.model_loaded:
            if not self.load_model():
                return {"error": "모델 로딩 실패"}
        
        try:
            # 이미지 전처리
            image_tensor = self.preprocess_image(image_path, face_crop=face_crop)
            
            # 추론
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                fake_prob = probs[0][1].item()  # FAKE 클래스 확률
                real_prob = probs[0][0].item()  # REAL 클래스 확률
                confidence = max(fake_prob, real_prob)
                label = "FAKE" if fake_prob > 0.5 else "REAL"
            
            return {
                "label": label,
                "score": float(confidence),
                "fake_prob": float(fake_prob),
                "real_prob": float(real_prob),
                "model": "EfficientNet-B0"
            }
            
        except Exception as e:
            print(f"[EfficientNet-B0] 예측 오류: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}


