"""
데이터셋을 CPU 학습 코드 형식으로 변환
train/val/test 구조를 REAL/FAKE 구조로 변환
"""
import shutil
from pathlib import Path
from tqdm import tqdm

def convert_dataset(source_dir, output_dir):
    """
    train/val/test 구조를 REAL/FAKE 구조로 변환
    
    Args:
        source_dir: 원본 디렉토리 (train/, val/, test/ 포함)
        output_dir: 출력 디렉토리 (REAL/, FAKE/ 생성)
    """
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    
    # REAL과 FAKE 폴더 생성
    (output_dir / 'REAL').mkdir(parents=True, exist_ok=True)
    (output_dir / 'FAKE').mkdir(parents=True, exist_ok=True)
    
    # train/val/test의 real 이미지를 REAL로 복사
    real_count = 0
    fake_count = 0
    
    for split in ['train', 'val', 'test']:
        real_dir = source_dir / split / 'real'
        fake_dir = source_dir / split / 'fake'
        
        if real_dir.exists():
            for img in tqdm(real_dir.glob('*.jpg'), desc=f"{split}/real 복사"):
                shutil.copy2(img, output_dir / 'REAL' / img.name)
                real_count += 1
        
        if fake_dir.exists():
            for img in tqdm(fake_dir.glob('*.jpg'), desc=f"{split}/fake 복사"):
                shutil.copy2(img, output_dir / 'FAKE' / img.name)
                fake_count += 1
    
    print(f"\n변환 완료!")
    print(f"  REAL: {real_count}개")
    print(f"  FAKE: {fake_count}개")
    print(f"  출력 디렉토리: {output_dir}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='데이터셋 구조 변환')
    parser.add_argument('--source-dir', type=str, required=True,
                        help='원본 디렉토리 (train/, val/, test/ 포함)')
    parser.add_argument('--output-dir', type=str, required=True,
                        help='출력 디렉토리 (REAL/, FAKE/ 생성)')
    
    args = parser.parse_args()
    
    convert_dataset(args.source_dir, args.output_dir)



