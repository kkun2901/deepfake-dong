"""튜닝된 모델 로딩 테스트"""
import sys
from pathlib import Path

# 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from app.services.model_mesonet import MesoNetBackend
from app.core.config import MESONET_WEIGHTS, IMAGE_SIZE

print("=" * 60)
print("튜닝된 모델 로딩 테스트")
print("=" * 60)
print(f"모델 경로: {MESONET_WEIGHTS}")
print(f"파일 존재: {Path(MESONET_WEIGHTS).exists()}")
print(f"IMAGE_SIZE: {IMAGE_SIZE}")
print()

try:
    backend = MesoNetBackend()
    print("MesoNetBackend 인스턴스 생성 완료")
    print(f"전처리 입력 크기: {backend.transform.transforms[0].size}")
    print()
    
    result = backend.load_model()
    if result:
        print("=" * 60)
        print("[SUCCESS] 모델 로딩 성공!")
        print("=" * 60)
        print(f"모델 파라미터 수: {sum(p.numel() for p in backend.model.parameters()):,}")
        print(f"모델 입력 크기: 256x256")
        print(f"Dropout rate: 0.4")
    else:
        print("=" * 60)
        print("[FAIL] 모델 로딩 실패!")
        print("=" * 60)
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()

