"""
모델 파일 다운로드 및 복사 스크립트
"""
import os
import subprocess
import shutil
import urllib.request
from pathlib import Path

def download_efficientnet():
    """EfficientNet-B0 (DFDC) 모델 다운로드"""
    base_dir = Path(__file__).parent
    weights_dir = base_dir / "weights"
    weights_dir.mkdir(exist_ok=True)
    
    target_file = weights_dir / "effb0_dfdc.pth"
    
    if target_file.exists():
        print(f"✓ EfficientNet-B0 모델이 이미 존재합니다: {target_file}")
        return True
    
    print("\n[1/2] EfficientNet-B0 (DFDC) 모델 다운로드...")
    print("  ⚠ GitHub releases에서 직접 다운로드가 필요합니다.")
    print("  다음 URL에서 파일을 다운로드하세요:")
    print("  https://github.com/selimsef/dfdc_deepfake_challenge/releases")
    print("  또는 직접 파일 경로를 입력하세요:")
    
    user_path = input("  파일 경로 (Enter로 건너뛰기): ").strip().strip('"').strip("'")
    
    if user_path:
        user_path = Path(user_path)
        if user_path.exists():
            shutil.copy(user_path, target_file)
            print(f"  ✓ 복사 완료: {target_file}")
            return True
        else:
            print(f"  ✗ 파일이 존재하지 않습니다: {user_path}")
    
    print("  ⚠ EfficientNet-B0 모델 파일이 없습니다.")
    print("  ImageNet pretrained 모델을 사용합니다.")
    return False

def handle_mesonet():
    """MesoNet 모델 처리"""
    base_dir = Path(__file__).parent
    weights_dir = base_dir / "weights"
    weights_dir.mkdir(exist_ok=True)
    
    target_file = weights_dir / "mesonet_pretrained.pth"
    
    if target_file.exists():
        print(f"✓ MesoNet PyTorch 모델이 이미 존재합니다: {target_file}")
        return True
    
    print("\n[2/2] MesoNet 모델 처리...")
    
    # .h5 파일 확인
    h5_path = base_dir / "MesoNet" / "weights" / "Meso4_DF.h5"
    
    if h5_path.exists():
        print(f"  ✓ .h5 파일 발견: {h5_path}")
        print(f"  ⚠ MesoNet은 Keras(.h5) 형식으로만 제공됩니다.")
        print(f"  ⚠ PyTorch(.pth) 버전이 필요합니다.")
        print(f"  다음 중 하나를 선택하세요:")
        print(f"  1. PyTorch 버전 .pth 파일 경로 입력")
        print(f"  2. Enter로 건너뛰기 (EfficientNet만 사용)")
        
        user_path = input("  > ").strip().strip('"').strip("'")
        
        if user_path:
            user_path = Path(user_path)
            if user_path.exists():
                shutil.copy(user_path, target_file)
                print(f"  ✓ 복사 완료: {target_file}")
                return True
            else:
                print(f"  ✗ 파일이 존재하지 않습니다: {user_path}")
    
    print("  ⚠ MesoNet PyTorch 모델 파일이 없습니다.")
    print("  EfficientNet만 사용합니다.")
    return False

def main():
    """메인 함수"""
    print("=" * 60)
    print("모델 파일 다운로드 및 복사")
    print("=" * 60)
    
    eff_ok = download_efficientnet()
    meso_ok = handle_mesonet()
    
    print("\n" + "=" * 60)
    print("최종 상태")
    print("=" * 60)
    print(f"  - EfficientNet-B0: {'✓ 있음' if eff_ok else '✗ 없음 (ImageNet pretrained 사용)'}")
    print(f"  - MesoNet: {'✓ 있음' if meso_ok else '✗ 없음 (EfficientNet만 사용)'}")
    
    if eff_ok and meso_ok:
        print("\n  🎉 듀오(앙상블) 모델 사용 가능!")
    elif eff_ok:
        print("\n  ⚠ EfficientNet 단독 사용 (정상 동작)")
    else:
        print("\n  ⚠ EfficientNet ImageNet pretrained 사용")

if __name__ == "__main__":
    main()


