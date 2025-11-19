"""
dataset_1.8gb 데이터셋을 CPU 학습 코드 형식으로 변환
파일명에 비디오 ID가 없으므로 가상의 비디오 ID를 추가
"""
import shutil
from pathlib import Path
from tqdm import tqdm
import random

def prepare_dataset(source_dir, output_dir, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, seed=42):
    """
    Train/Test 구조를 REAL/FAKE 구조로 변환하고 비디오 ID 추가
    
    Args:
        source_dir: 원본 디렉토리 (Dataset/Train/, Dataset/Test/ 포함)
        output_dir: 출력 디렉토리 (REAL/, FAKE/ 생성)
        train_ratio: 학습 데이터 비율
        val_ratio: 검증 데이터 비율
        test_ratio: 테스트 데이터 비율
    """
    random.seed(seed)
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    
    # 출력 디렉토리 생성
    (output_dir / 'REAL').mkdir(parents=True, exist_ok=True)
    (output_dir / 'FAKE').mkdir(parents=True, exist_ok=True)
    
    # Train 데이터 수집
    train_real = list((source_dir / 'Dataset' / 'Train' / 'Real').glob('*.jpg'))
    train_fake = list((source_dir / 'Dataset' / 'Train' / 'Fake').glob('*.jpg'))
    
    # Test 데이터 수집
    test_real = list((source_dir / 'Dataset' / 'Test' / 'Real').glob('*.jpg'))
    test_fake = list((source_dir / 'Dataset' / 'Test' / 'Fake').glob('*.jpg'))
    
    print(f"원본 데이터:")
    print(f"  Train - REAL: {len(train_real)}, FAKE: {len(train_fake)}")
    print(f"  Test - REAL: {len(test_real)}, FAKE: {len(test_fake)}")
    
    # 모든 파일을 합치고 비디오 ID 할당
    # 파일명에 비디오 ID가 없으므로, 파일을 그룹화하여 가상의 비디오 ID 할당
    all_real = train_real + test_real
    all_fake = train_fake + test_fake
    
    # 파일을 그룹화 (예: 50개씩 하나의 비디오로 간주)
    def group_files(files, group_size=50):
        """파일들을 그룹화하여 가상의 비디오 ID 할당"""
        groups = []
        for i in range(0, len(files), group_size):
            groups.append(files[i:i+group_size])
        return groups
    
    real_groups = group_files(all_real, group_size=50)
    fake_groups = group_files(all_fake, group_size=50)
    
    print(f"\n가상 비디오 그룹:")
    print(f"  REAL: {len(real_groups)}개 그룹")
    print(f"  FAKE: {len(fake_groups)}개 그룹")
    
    # 비디오 그룹 단위로 train/val/test 분할
    random.shuffle(real_groups)
    random.shuffle(fake_groups)
    
    n_real_train = int(len(real_groups) * train_ratio)
    n_real_val = int(len(real_groups) * val_ratio)
    
    real_train_groups = real_groups[:n_real_train]
    real_val_groups = real_groups[n_real_train:n_real_train+n_real_val]
    real_test_groups = real_groups[n_real_train+n_real_val:]
    
    n_fake_train = int(len(fake_groups) * train_ratio)
    n_fake_val = int(len(fake_groups) * val_ratio)
    
    fake_train_groups = fake_groups[:n_fake_train]
    fake_val_groups = fake_groups[n_fake_train:n_fake_train+n_fake_val]
    fake_test_groups = fake_groups[n_fake_train+n_fake_val:]
    
    # 파일 복사 (비디오 ID 추가)
    def copy_with_video_id(groups, output_dir, label_name, split_name):
        """그룹의 파일들을 비디오 ID와 함께 복사"""
        count = 0
        for group_idx, group in enumerate(tqdm(groups, desc=f"{label_name} {split_name}")):
            video_id = f"video{split_name[0]}{group_idx:04d}"  # videoT0001, videoV0001 등
            for frame_idx, img_path in enumerate(group):
                new_name = f"{video_id}_frame{frame_idx:04d}.jpg"
                shutil.copy2(img_path, output_dir / label_name / new_name)
                count += 1
        return count
    
    # REAL 파일 복사
    real_train_count = copy_with_video_id(real_train_groups, output_dir, 'REAL', 'train')
    real_val_count = copy_with_video_id(real_val_groups, output_dir, 'REAL', 'val')
    real_test_count = copy_with_video_id(real_test_groups, output_dir, 'REAL', 'test')
    
    # FAKE 파일 복사
    fake_train_count = copy_with_video_id(fake_train_groups, output_dir, 'FAKE', 'train')
    fake_val_count = copy_with_video_id(fake_val_groups, output_dir, 'FAKE', 'val')
    fake_test_count = copy_with_video_id(fake_test_groups, output_dir, 'FAKE', 'test')
    
    print(f"\n변환 완료!")
    print(f"출력 디렉토리: {output_dir}")
    print(f"\n데이터셋 구성:")
    print(f"  REAL - train: {real_train_count}, val: {real_val_count}, test: {real_test_count}")
    print(f"  FAKE - train: {fake_train_count}, val: {fake_val_count}, test: {fake_test_count}")
    print(f"  총: {real_train_count + real_val_count + real_test_count + fake_train_count + fake_val_count + fake_test_count}개")
    
    print(f"\n⚠️ 주의: 원본 파일명에 비디오 ID가 없어 가상의 비디오 ID를 할당했습니다.")
    print(f"  파일명 형식: videoT0001_frame0001.jpg (T=train, V=val, S=test)")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='데이터셋 준비')
    parser.add_argument('--source-dir', type=str, default='dataset_1.8gb',
                        help='원본 디렉토리')
    parser.add_argument('--output-dir', type=str, default='dataset_ready',
                        help='출력 디렉토리')
    parser.add_argument('--train-ratio', type=float, default=0.7,
                        help='학습 데이터 비율')
    parser.add_argument('--val-ratio', type=float, default=0.15,
                        help='검증 데이터 비율')
    parser.add_argument('--test-ratio', type=float, default=0.15,
                        help='테스트 데이터 비율')
    
    args = parser.parse_args()
    
    prepare_dataset(
        args.source_dir,
        args.output_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
    )
    
    print(f"\n✓ 준비 완료!")
    print(f"\n학습 명령:")
    print(f"python train_mesonet_cpu_optimized.py --data-dir {args.output_dir} --epochs 30 --batch-size 8")



