"""
데이터셋 준비 (불균형 처리 포함)
Train 데이터를 train/val/test로 분할하고, 데이터 불균형을 고려
"""
import shutil
from pathlib import Path
from tqdm import tqdm
import random

def prepare_balanced_dataset(source_dir, output_dir, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, seed=42):
    """
    Train 데이터를 train/val/test로 분할하고 비디오 ID 추가
    Test 데이터는 Train에 합침 (FAKE가 없으므로)
    
    Args:
        source_dir: 원본 디렉토리
        output_dir: 출력 디렉토리
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
    
    # Test 데이터도 Train에 합침 (FAKE가 없으므로)
    test_real = list((source_dir / 'Dataset' / 'Test' / 'Real').glob('*.jpg'))
    
    all_real = train_real + test_real
    all_fake = train_fake
    
    print(f"원본 데이터:")
    print(f"  Train - REAL: {len(train_real)}, FAKE: {len(train_fake)}")
    print(f"  Test - REAL: {len(test_real)} (Train에 합침)")
    print(f"  전체 - REAL: {len(all_real)}, FAKE: {len(all_fake)}")
    print(f"  비율 - REAL: {len(all_real)/(len(all_real)+len(all_fake))*100:.1f}%, FAKE: {len(all_fake)/(len(all_real)+len(all_fake))*100:.1f}%")
    
    # 파일을 그룹화하여 가상의 비디오 ID 할당 (50개씩)
    def group_files(files, group_size=50):
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
    
    # 파일 복사
    def copy_with_video_id(groups, output_dir, label_name, split_name):
        count = 0
        for group_idx, group in enumerate(tqdm(groups, desc=f"{label_name} {split_name}")):
            video_id = f"video{split_name[0]}{group_idx:04d}"
            for frame_idx, img_path in enumerate(group):
                new_name = f"{video_id}_frame{frame_idx:04d}.jpg"
                shutil.copy2(img_path, output_dir / label_name / new_name)
                count += 1
        return count
    
    # 파일 복사
    real_train_count = copy_with_video_id(real_train_groups, output_dir, 'REAL', 'train')
    real_val_count = copy_with_video_id(real_val_groups, output_dir, 'REAL', 'val')
    real_test_count = copy_with_video_id(real_test_groups, output_dir, 'REAL', 'test')
    
    fake_train_count = copy_with_video_id(fake_train_groups, output_dir, 'FAKE', 'train')
    fake_val_count = copy_with_video_id(fake_val_groups, output_dir, 'FAKE', 'val')
    fake_test_count = copy_with_video_id(fake_test_groups, output_dir, 'FAKE', 'test')
    
    print(f"\n변환 완료!")
    print(f"출력 디렉토리: {output_dir}")
    print(f"\n데이터셋 구성:")
    print(f"  REAL - train: {real_train_count}, val: {real_val_count}, test: {real_test_count}")
    print(f"  FAKE - train: {fake_train_count}, val: {fake_val_count}, test: {fake_test_count}")
    print(f"  총: {real_train_count + real_val_count + real_test_count + fake_train_count + fake_val_count + fake_test_count}개")
    
    # 불균형 정보
    total_train = real_train_count + fake_train_count
    total_val = real_val_count + fake_val_count
    total_test = real_test_count + fake_test_count
    
    print(f"\n데이터 불균형:")
    print(f"  Train - REAL: {real_train_count/total_train*100:.1f}%, FAKE: {fake_train_count/total_train*100:.1f}%")
    print(f"  Val - REAL: {real_val_count/total_val*100:.1f}%, FAKE: {fake_val_count/total_val*100:.1f}%")
    print(f"  Test - REAL: {real_test_count/total_test*100:.1f}%, FAKE: {fake_test_count/total_test*100:.1f}%")
    
    print(f"\n⚠️ 주의: 데이터 불균형이 있습니다. 학습 시 class_weight를 사용하는 것을 권장합니다.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='데이터셋 준비 (불균형 처리)')
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
    
    prepare_balanced_dataset(
        args.source_dir,
        args.output_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
    )
    
    print(f"\n✓ 준비 완료!")
    print(f"\n학습 명령:")
    print(f"python train_mesonet_cpu_optimized.py --data-dir {args.output_dir} --epochs 30 --batch-size 8")



