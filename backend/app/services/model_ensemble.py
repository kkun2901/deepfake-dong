"""
EfficientNet-B0 + MesoNet 앙상블 백엔드
"""
from app.services.model_efficientnet import EfficientNetB0Backend
from app.services.model_mesonet import MesoNetBackend
from app.core.config import (
    ENSEMBLE_WEIGHT_EFFICIENTNET,
    ENSEMBLE_WEIGHT_MESONET,
    USE_FACE_CROP
)

class EnsembleBackend:
    """EfficientNet-B0 + MesoNet 앙상블 백엔드"""
    
    def __init__(self, eff_backend: EfficientNetB0Backend, meso_backend: MesoNetBackend, 
                 w_eff: float = 0.7, w_meso: float = 0.3):
        """
        Args:
            eff_backend: EfficientNet-B0 백엔드 인스턴스
            meso_backend: MesoNet 백엔드 인스턴스
            w_eff: EfficientNet 가중치 (기본: 0.7)
            w_meso: MesoNet 가중치 (기본: 0.3)
        """
        self.eff_backend = eff_backend
        self.meso_backend = meso_backend
        self.w_eff = w_eff
        self.w_meso = w_meso
        
        # 가중치 정규화
        total_weight = w_eff + w_meso
        if total_weight > 0:
            self.w_eff = w_eff / total_weight
            self.w_meso = w_meso / total_weight
    
    def predict(self, image_path: str, face_crop: bool = None):
        """
        앙상블 예측
        
        Args:
            image_path: 이미지 파일 경로
            face_crop: 얼굴 crop 사용 여부 (None이면 설정값 사용)
        
        Returns:
            앙상블 예측 결과 딕셔너리
        """
        if face_crop is None:
            face_crop = USE_FACE_CROP
        
        # 각 모델로 예측
        eff_result = self.eff_backend.predict(image_path, face_crop=face_crop)
        meso_result = self.meso_backend.predict(image_path, face_crop=face_crop)
        
        # 오류 체크
        if "error" in eff_result:
            print(f"[Ensemble] EfficientNet 오류: {eff_result['error']}")
            # EfficientNet 실패 시 MesoNet 결과만 반환
            if "error" not in meso_result:
                return {
                    **meso_result,
                    "meta": {
                        "ensemble": False,
                        "weights": {"efficientnet": 0.0, "mesonet": 1.0}
                    }
                }
            return {"error": f"모든 모델 실패: EfficientNet={eff_result['error']}, MesoNet={meso_result.get('error', 'unknown')}"}
        
        if "error" in meso_result:
            print(f"[Ensemble] MesoNet 오류: {meso_result['error']}")
            # MesoNet 실패 시 EfficientNet 결과만 반환
            return {
                **eff_result,
                "meta": {
                    "ensemble": False,
                    "weights": {"efficientnet": 1.0, "mesonet": 0.0}
                }
            }
        
        # 앙상블: 가중 평균
        eff_fake = eff_result.get("fake_prob", 0.0)
        meso_fake = meso_result.get("fake_prob", 0.0)
        
        ensemble_fake = (self.w_eff * eff_fake) + (self.w_meso * meso_fake)
        ensemble_real = 1.0 - ensemble_fake
        ensemble_confidence = max(ensemble_fake, ensemble_real)
        ensemble_label = "FAKE" if ensemble_fake > 0.5 else "REAL"
        
        return {
            "label": ensemble_label,
            "score": float(ensemble_confidence),
            "fake_prob": float(ensemble_fake),
            "real_prob": float(ensemble_real),
            "meta": {
                "ensemble": True,
                "weights": {
                    "efficientnet": self.w_eff,
                    "mesonet": self.w_meso
                },
                "models": {
                    "efficientnet": {
                        "label": eff_result.get("label", "UNKNOWN"),
                        "score": eff_result.get("score", 0.0),
                        "fake_prob": eff_fake
                    },
                    "mesonet": {
                        "label": meso_result.get("label", "UNKNOWN"),
                        "score": meso_result.get("score", 0.0),
                        "fake_prob": meso_fake
                    }
                }
            }
        }


