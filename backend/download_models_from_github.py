"""
GitHub releases에서 모델 파일 다운로드
"""
import urllib.request
import os
from pathlib import Path

def download_file(url, output_path):
    """파일 다운로드"""
    try:
        print(f"  다운로드 중: {url}")
        print(f"  저장 위치: {output_path}")
        urllib.request.urlretrieve(url, output_path)
        print(f"  ✓ 다운로드 완료!")
        return True
    except Exception as e:
        print(f"  ✗ 다운로드 실패: {e}")
        return False

def main():
    """메인 함수"""
    base_dir = Path(__file__).parent
    weights_dir = base_dir / "weights"
    weights_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("GitHub Releases에서 모델 다운로드")
    print("=" * 60)
    
    # EfficientNet-B0는 GitHub releases에 없을 수 있음
    # 대신 B7 모델이 있지만, 우리는 B0를 사용해야 함
    print("\n⚠ 참고:")
    print("  - GitHub releases에는 EfficientNet-B7 모델만 있습니다")
    print("  - EfficientNet-B0 모델은 별도로 필요합니다")
    print("  - 현재는 ImageNet pretrained EfficientNet-B0를 사용합니다")
    
    # MesoNet은 .h5 파일만 있고 PyTorch 버전이 없음
    print("\n⚠ MesoNet:")
    print("  - 원본 저장소에는 .h5 파일(Keras)만 있습니다")
    print("  - PyTorch 버전(.pth)이 필요합니다")
    print("  - 현재는 EfficientNet만 사용합니다")
    
    print("\n" + "=" * 60)
    print("현재 상태")
    print("=" * 60)
    
    eff_exists = (weights_dir / "effb0_dfdc.pth").exists()
    meso_exists = (weights_dir / "mesonet_pretrained.pth").exists()
    
    print(f"  - EfficientNet-B0: {'✓ 있음' if eff_exists else '✗ 없음 (ImageNet pretrained 사용)'}")
    print(f"  - MesoNet: {'✓ 있음' if meso_exists else '✗ 없음 (EfficientNet만 사용)'}")
    
    if eff_exists and meso_exists:
        print("\n  🎉 듀오(앙상블) 모델 사용 가능!")
    elif eff_exists:
        print("\n  ⚠ EfficientNet 단독 사용")
    else:
        print("\n  ⚠ EfficientNet ImageNet pretrained 사용 (정상 동작)")
    
    print("\n💡 권장사항:")
    print("  1. EfficientNet-B0 DFDC pretrained 가중치가 있다면:")
    print("     python copy_models.py 실행 후 파일 경로 입력")
    print("  2. MesoNet PyTorch 버전이 있다면:")
    print("     python copy_models.py 실행 후 파일 경로 입력")
    print("  3. 현재 상태로도 정상 동작합니다 (EfficientNet ImageNet pretrained)")

if __name__ == "__main__":
    main()


