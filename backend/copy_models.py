"""
모델 파일 복사 스크립트
GPT에게 받은 모델 파일을 weights 폴더로 복사합니다.
"""
import shutil
from pathlib import Path

def copy_models():
    """모델 파일 복사"""
    base_dir = Path(__file__).parent
    weights_dir = base_dir / "weights"
    weights_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("모델 파일 복사")
    print("=" * 60)
    
    # 1. EfficientNet-B0
    print("\n[1/2] EfficientNet-B0 (DFDC) 모델 파일 찾기...")
    eff_target = weights_dir / "effb0_dfdc.pth"
    
    if eff_target.exists():
        print(f"  ✓ 이미 존재: {eff_target}")
    else:
        # 여러 가능한 경로 확인
        possible_paths = [
            base_dir / "dfdc_deepfake_challenge" / "pretrained" / "efficientnet_b0_dfdc.pth",
            base_dir / "dfdc_deepfake_challenge" / "weights" / "efficientnet_b0_dfdc.pth",
            base_dir / "efficientnet_b0_dfdc.pth",
            base_dir / "effb0_dfdc.pth",
        ]
        
        found = False
        for path in possible_paths:
            if path.exists():
                print(f"  - 파일 발견: {path}")
                shutil.copy(path, eff_target)
                print(f"  ✓ 복사 완료: {eff_target}")
                found = True
                break
        
        if not found:
            print(f"  ✗ 파일을 찾을 수 없습니다.")
            print(f"  파일 경로를 입력하세요 (Enter로 건너뛰기):")
            user_path = input("  > ").strip().strip('"').strip("'")
            if user_path:
                user_path = Path(user_path)
                if user_path.exists():
                    shutil.copy(user_path, eff_target)
                    print(f"  ✓ 복사 완료: {eff_target}")
                else:
                    print(f"  ✗ 파일이 존재하지 않습니다: {user_path}")
    
    # 2. MesoNet
    print("\n[2/2] MesoNet 모델 파일 찾기...")
    meso_target = weights_dir / "mesonet_pretrained.pth"
    
    if meso_target.exists():
        print(f"  ✓ 이미 존재: {meso_target}")
    else:
        # .h5 파일 찾기 (Keras 형식)
        h5_path = base_dir / "MesoNet" / "weights" / "Meso4_DF.h5"
        
        if h5_path.exists():
            print(f"  - .h5 파일 발견: {h5_path}")
            print(f"  ⚠ MesoNet은 .h5 파일(Keras)만 있습니다.")
            print(f"  ⚠ PyTorch 버전(.pth)이 필요합니다.")
            print(f"  .pth 파일 경로를 입력하세요 (Enter로 건너뛰기):")
            user_path = input("  > ").strip().strip('"').strip("'")
            if user_path:
                user_path = Path(user_path)
                if user_path.exists():
                    shutil.copy(user_path, meso_target)
                    print(f"  ✓ 복사 완료: {meso_target}")
                else:
                    print(f"  ✗ 파일이 존재하지 않습니다: {user_path}")
        else:
            # .pth 파일 찾기
            possible_paths = [
                base_dir / "MesoNet" / "Meso4_DF.pth",
                base_dir / "mesonet_pretrained.pth",
                base_dir / "Meso4_DF.pth",
            ]
            
            found = False
            for path in possible_paths:
                if path.exists():
                    print(f"  - 파일 발견: {path}")
                    shutil.copy(path, meso_target)
                    print(f"  ✓ 복사 완료: {meso_target}")
                    found = True
                    break
            
            if not found:
                print(f"  ✗ 파일을 찾을 수 없습니다.")
                print(f"  파일 경로를 입력하세요 (Enter로 건너뛰기):")
                user_path = input("  > ").strip().strip('"').strip("'")
                if user_path:
                    user_path = Path(user_path)
                    if user_path.exists():
                        shutil.copy(user_path, meso_target)
                        print(f"  ✓ 복사 완료: {meso_target}")
                    else:
                        print(f"  ✗ 파일이 존재하지 않습니다: {user_path}")
    
    print("\n" + "=" * 60)
    print("모델 파일 상태")
    print("=" * 60)
    eff_exists = (weights_dir / "effb0_dfdc.pth").exists()
    meso_exists = (weights_dir / "mesonet_pretrained.pth").exists()
    
    print(f"  - EfficientNet-B0: {'✓ 있음' if eff_exists else '✗ 없음'}")
    print(f"  - MesoNet: {'✓ 있음' if meso_exists else '✗ 없음'}")
    
    if eff_exists and meso_exists:
        print("\n  🎉 모든 모델 파일이 준비되었습니다!")
        print("  듀오(앙상블) 모델을 사용할 수 있습니다.")
    elif eff_exists:
        print("\n  ⚠ EfficientNet만 사용 가능합니다.")
    else:
        print("\n  ⚠ 모델 파일이 부족합니다.")

if __name__ == "__main__":
    copy_models()


