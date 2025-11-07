"""
모델 다운로드 스크립트
EfficientNet-B0 (DFDC)와 MesoNet 모델을 다운로드합니다.
"""
import os
import subprocess
import shutil
from pathlib import Path

def download_models():
    """모델 다운로드 및 준비"""
    base_dir = Path(__file__).parent
    weights_dir = base_dir / "weights"
    weights_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("모델 다운로드 시작")
    print("=" * 60)
    
    # 1. EfficientNet-B0 (DFDC) 모델 다운로드
    print("\n[1/2] EfficientNet-B0 (DFDC) 모델 다운로드 중...")
    dfdc_repo = base_dir / "dfdc_deepfake_challenge"
    
    if not (weights_dir / "effb0_dfdc.pth").exists():
        if not dfdc_repo.exists():
            print("  - dfdc_deepfake_challenge 저장소 클론 중...")
            subprocess.run([
                "git", "clone", 
                "https://github.com/selimsef/dfdc_deepfake_challenge.git",
                str(dfdc_repo)
            ], check=True)
        else:
            print("  - 저장소가 이미 존재합니다. 업데이트 중...")
            subprocess.run(["git", "-C", str(dfdc_repo), "pull"], check=False)
        
        # 여러 경로 확인
        possible_paths = [
            dfdc_repo / "pretrained" / "efficientnet_b0_dfdc.pth",
            dfdc_repo / "weights" / "efficientnet_b0_dfdc.pth",
        ]
        
        model_path = None
        for path in possible_paths:
            if path.exists():
                model_path = path
                break
        
        if model_path:
            print(f"  - 모델 파일 복사 중: {model_path} -> {weights_dir / 'effb0_dfdc.pth'}")
            shutil.copy(model_path, weights_dir / "effb0_dfdc.pth")
            print("  ✓ EfficientNet-B0 모델 다운로드 완료")
        else:
            print(f"  ⚠ 경고: EfficientNet-B0 모델 파일을 찾을 수 없습니다.")
            print("  GitHub releases에서 직접 다운로드하거나 다른 소스를 사용해야 합니다.")
            print("  대안: ImageNet pretrained EfficientNet-B0를 사용할 수 있습니다.")
            print("  (서버 시작 시 자동으로 다운로드됩니다)")
    else:
        print("  ✓ EfficientNet-B0 모델이 이미 존재합니다.")
    
    # 2. MesoNet 모델 다운로드
    print("\n[2/2] MesoNet 모델 다운로드 중...")
    mesonet_repo = base_dir / "MesoNet"
    
    if not (weights_dir / "mesonet_pretrained.pth").exists():
        if not mesonet_repo.exists():
            print("  - MesoNet 저장소 클론 중...")
            subprocess.run([
                "git", "clone",
                "https://github.com/DariusAf/MesoNet.git",
                str(mesonet_repo)
            ], check=True)
        else:
            print("  - 저장소가 이미 존재합니다. 업데이트 중...")
            subprocess.run(["git", "-C", str(mesonet_repo), "pull"], check=False)
        
        # MesoNet은 .h5 파일로 제공됨 (Keras/TensorFlow 형식)
        model_path = mesonet_repo / "weights" / "Meso4_DF.h5"
        if model_path.exists():
            print(f"  - MesoNet 모델 파일 발견: {model_path}")
            print(f"  ⚠ MesoNet은 .h5 파일(Keras)입니다. PyTorch 버전으로 변환하거나 다른 소스를 사용해야 합니다.")
            print("  대안: PyTorch로 구현된 MesoNet을 사용하거나, .h5 파일을 PyTorch로 변환해야 합니다.")
            print("  현재는 MesoNet 없이 EfficientNet만 사용하거나, 다른 소스에서 PyTorch 모델을 찾아야 합니다.")
        else:
            print(f"  ⚠ 경고: MesoNet 모델 파일을 찾을 수 없습니다: {model_path}")
            print("  MesoNet은 Keras/TensorFlow 형식(.h5)으로만 제공됩니다.")
            print("  PyTorch 버전을 직접 구현하거나 다른 소스를 사용해야 합니다.")
    else:
        print("  ✓ MesoNet 모델이 이미 존재합니다.")
    
    print("\n" + "=" * 60)
    print("모델 다운로드 완료")
    print(f"모델 위치: {weights_dir}")
    print("=" * 60)
    
    # 모델 파일 확인
    eff_exists = (weights_dir / "effb0_dfdc.pth").exists()
    meso_exists = (weights_dir / "mesonet_pretrained.pth").exists()
    
    print("\n📋 모델 파일 상태:")
    print(f"  - EfficientNet-B0: {'✓ 있음' if eff_exists else '✗ 없음'}")
    print(f"  - MesoNet: {'✓ 있음' if meso_exists else '✗ 없음'}")
    
    if not eff_exists or not meso_exists:
        print("\n⚠ 일부 모델 파일이 없습니다.")
        print("다음 옵션을 고려하세요:")
        print("1. EfficientNet: ImageNet pretrained 모델 사용 (자동 다운로드)")
        print("2. MesoNet: PyTorch 버전 직접 구현 또는 다른 소스 사용")
        print("3. 일단 EfficientNet만 사용하여 테스트")
    
    # 정리: 임시 저장소 삭제 (선택사항)
    print("\n" + "=" * 60)
    cleanup = input("임시 저장소를 삭제하시겠습니까? (y/n): ").strip().lower()
    if cleanup == 'y':
        if dfdc_repo.exists():
            shutil.rmtree(dfdc_repo)
            print("  ✓ dfdc_deepfake_challenge 저장소 삭제됨")
        if mesonet_repo.exists():
            shutil.rmtree(mesonet_repo)
            print("  ✓ MesoNet 저장소 삭제됨")
    else:
        print("  임시 저장소를 유지합니다.")

if __name__ == "__main__":
    download_models()

