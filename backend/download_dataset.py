"""
데이터셋 다운로드 헬퍼 스크립트
"""
import os
import urllib.request
import zipfile
from pathlib import Path
import argparse

def download_mesonet_dataset(output_dir="dataset"):
    """
    MesoNet 공식 데이터셋 다운로드 안내
    pcloud 링크는 직접 다운로드가 필요합니다.
    """
    print("=" * 60)
    print("MesoNet 공식 데이터셋 다운로드")
    print("=" * 60)
    print("\n다음 링크에서 데이터셋을 다운로드하세요:")
    print("https://my.pcloud.com/publink/show?code=XZLGvd7ZI9LjgIy7iOLzXBG5RNJzGFQzhTRy")
    print("\n다운로드 후 압축을 해제하고 다음 구조로 정리하세요:")
    print(f"""
{output_dir}/
├── train/
│   ├── real/     # 실제 이미지들
│   └── fake/     # 딥페이크 이미지들
└── val/
    ├── real/
    └── fake/
""")
    print("\n또는 다운로드한 파일 경로를 입력하면 자동으로 정리해드립니다.")
    user_path = input("\n다운로드한 파일 경로 (Enter로 건너뛰기): ").strip().strip('"').strip("'")
    
    if user_path and Path(user_path).exists():
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\n압축 해제 중: {user_path}")
        with zipfile.ZipFile(user_path, 'r') as zip_ref:
            zip_ref.extractall(output_path)
        
        print(f"✓ 압축 해제 완료: {output_path}")
        print("\n다음 명령으로 학습을 시작하세요:")
        print(f"python train_mesonet.py --data-dir {output_dir}/train --val-dir {output_dir}/val")
    else:
        print("\n수동으로 다운로드 및 압축 해제를 진행하세요.")


def create_sample_structure(output_dir="dataset"):
    """샘플 데이터셋 구조 생성"""
    output_path = Path(output_dir)
    
    dirs = [
        output_path / "train" / "real",
        output_path / "train" / "fake",
        output_path / "val" / "real",
        output_path / "val" / "fake",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # README 파일 생성
    readme_path = output_path / "README.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("""딥페이크 탐지 데이터셋 구조

이 폴더에 데이터셋을 다음과 같이 배치하세요:

train/
├── real/     # 학습용 실제 이미지들 (.jpg 또는 .png)
└── fake/     # 학습용 딥페이크 이미지들 (.jpg 또는 .png)

val/
├── real/     # 검증용 실제 이미지들 (.jpg 또는 .png)
└── fake/     # 검증용 딥페이크 이미지들 (.jpg 또는 .png)

데이터셋 다운로드:
1. MesoNet 공식 데이터셋: https://my.pcloud.com/publink/show?code=XZLGvd7ZI9LjgIy7iOLzXBG5RNJzGFQzhTRy
2. DFDC (Kaggle): https://www.kaggle.com/c/deepfake-detection-challenge
3. FaceForensics++: https://github.com/ondyari/FaceForensics

자세한 내용은 DATASET_GUIDE.md를 참고하세요.
""")
    
    print(f"✓ 데이터셋 구조 생성 완료: {output_path}")
    print(f"\n각 폴더에 이미지 파일을 추가하세요:")
    for dir_path in dirs:
        print(f"  - {dir_path}")


def main():
    parser = argparse.ArgumentParser(description='데이터셋 다운로드 및 준비')
    parser.add_argument('--create-structure', action='store_true',
                        help='샘플 데이터셋 구조 생성')
    parser.add_argument('--output-dir', type=str, default='dataset',
                        help='출력 디렉토리 (기본: dataset)')
    
    args = parser.parse_args()
    
    if args.create_structure:
        create_sample_structure(args.output_dir)
    else:
        download_mesonet_dataset(args.output_dir)


if __name__ == "__main__":
    main()



