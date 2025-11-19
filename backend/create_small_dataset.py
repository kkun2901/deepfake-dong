"""
작은 데이터셋 생성 스크립트
대형 데이터셋에서 샘플링하여 1~2GB 크기의 작은 데이터셋 생성
"""
import argparse
import random
import shutil
from pathlib import Path
from tqdm import tqdm
import os

def create_small_dataset(source_dir, output_dir, target_size_mb=1500, train_ratio=0.8):
    """
    소스 데이터셋에서 작은 데이터셋 생성
    
    Args:
        source_dir: 원본 데이터셋 디렉토리 (real/, fake/ 폴더 포함)
        output_dir: 출력 디렉토리
        target_size_mb: 목표 크기 (MB, 기본: 1500MB = 1.5GB)
        train_ratio: 학습 데이터 비율 (기본: 0.8)
    """
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    
    # 출력 디렉토리 생성
    train_real_dir = output_dir / "train" / "real"
    train_fake_dir = output_dir / "train" / "fake"
    val_real_dir = output_dir / "val" / "real"
    val_fake_dir = output_dir / "val" / "fake"
    
    for dir_path in [train_real_dir, train_fake_dir, val_real_dir, val_fake_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # 이미지 파일 수집
    real_images = list((source_dir / "real").glob("*.jpg")) + \
                  list((source_dir / "real").glob("*.png"))
    fake_images = list((source_dir / "fake").glob("*.jpg")) + \
                  list((source_dir / "fake").glob("*.png"))
    
    if not real_images and not fake_images:
        # train/val 구조인 경우
        train_real = list((source_dir / "train" / "real").glob("*.jpg")) + \
                     list((source_dir / "train" / "real").glob("*.png"))
        train_fake = list((source_dir / "train" / "fake").glob("*.jpg")) + \
                     list((source_dir / "train" / "fake").glob("*.png"))
        val_real = list((source_dir / "val" / "real").glob("*.jpg")) + \
                   list((source_dir / "val" / "real").glob("*.png"))
        val_fake = list((source_dir / "val" / "fake").glob("*.jpg")) + \
                   list((source_dir / "val" / "fake").glob("*.png"))
        
        real_images = train_real + val_real
        fake_images = train_fake + val_fake
    
    print(f"원본 데이터셋:")
    print(f"  - REAL: {len(real_images)}개")
    print(f"  - FAKE: {len(fake_images)}개")
    
    # 파일 크기 계산 함수
    def get_file_size_mb(file_path):
        return file_path.stat().st_size / (1024 * 1024)
    
    # 샘플링하여 목표 크기 맞추기
    random.shuffle(real_images)
    random.shuffle(fake_images)
    
    total_size_mb = 0
    selected_real = []
    selected_fake = []
    
    # REAL 이미지 샘플링 (목표의 50%)
    target_real_size = target_size_mb * 0.5
    for img in real_images:
        if total_size_mb >= target_real_size:
            break
        size = get_file_size_mb(img)
        selected_real.append(img)
        total_size_mb += size
    
    # FAKE 이미지 샘플링 (나머지 50%)
    target_fake_size = target_size_mb * 0.5
    fake_size = 0
    for img in fake_images:
        if fake_size >= target_fake_size:
            break
        size = get_file_size_mb(img)
        selected_fake.append(img)
        fake_size += size
    
    total_size_mb += fake_size
    
    print(f"\n샘플링된 데이터셋:")
    print(f"  - REAL: {len(selected_real)}개")
    print(f"  - FAKE: {len(selected_fake)}개")
    print(f"  - 예상 크기: {total_size_mb:.2f}MB ({total_size_mb/1024:.2f}GB)")
    
    # train/val 분할
    random.shuffle(selected_real)
    random.shuffle(selected_fake)
    
    n_real_train = int(len(selected_real) * train_ratio)
    n_fake_train = int(len(selected_fake) * train_ratio)
    
    real_train = selected_real[:n_real_train]
    real_val = selected_real[n_real_train:]
    fake_train = selected_fake[:n_fake_train]
    fake_val = selected_fake[n_fake_train:]
    
    # 파일 복사
    print("\n파일 복사 중...")
    
    for img in tqdm(real_train, desc="REAL train"):
        shutil.copy2(img, train_real_dir / img.name)
    
    for img in tqdm(real_val, desc="REAL val"):
        shutil.copy2(img, val_real_dir / img.name)
    
    for img in tqdm(fake_train, desc="FAKE train"):
        shutil.copy2(img, train_fake_dir / img.name)
    
    for img in tqdm(fake_val, desc="FAKE val"):
        shutil.copy2(img, val_fake_dir / img.name)
    
    print(f"\n✓ 작은 데이터셋 생성 완료!")
    print(f"출력 디렉토리: {output_dir}")
    print(f"\n데이터셋 구성:")
    print(f"  Train - REAL: {len(real_train)}개, FAKE: {len(fake_train)}개")
    print(f"  Val   - REAL: {len(real_val)}개, FAKE: {len(fake_val)}개")
    print(f"\n학습 명령:")
    print(f"python train_mesonet.py --data-dir {output_dir}/train --val-dir {output_dir}/val")


def create_mini_dataset_from_videos(video_dir_real, video_dir_fake, output_dir, 
                                    max_videos_per_class=10, frames_per_video=20):
    """
    비디오에서 최소한의 데이터셋 생성 (테스트용)
    
    Args:
        video_dir_real: REAL 비디오 디렉토리
        video_dir_fake: FAKE 비디오 디렉토리
        output_dir: 출력 디렉토리
        max_videos_per_class: 클래스당 최대 비디오 수
        frames_per_video: 비디오당 추출할 프레임 수
    """
    import cv2
    
    video_dir_real = Path(video_dir_real)
    video_dir_fake = Path(video_dir_fake)
    output_dir = Path(output_dir)
    
    # 출력 디렉토리 생성
    train_real_dir = output_dir / "train" / "real"
    train_fake_dir = output_dir / "train" / "fake"
    val_real_dir = output_dir / "val" / "real"
    val_fake_dir = output_dir / "val" / "fake"
    
    for dir_path in [train_real_dir, train_fake_dir, val_real_dir, val_fake_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    def extract_frames(video_path, output_dir, max_frames):
        """비디오에서 프레임 추출"""
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return 0
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        interval = max(1, total_frames // max_frames)
        
        frame_count = 0
        saved = 0
        video_name = video_path.stem
        
        while saved < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % interval == 0:
                output_path = output_dir / f"{video_name}_{saved:04d}.jpg"
                cv2.imwrite(str(output_path), frame)
                saved += 1
            
            frame_count += 1
        
        cap.release()
        return saved
    
    # REAL 비디오 처리
    real_videos = list(video_dir_real.glob("*.mp4"))[:max_videos_per_class]
    fake_videos = list(video_dir_fake.glob("*.mp4"))[:max_videos_per_class]
    
    print(f"비디오 처리:")
    print(f"  - REAL: {len(real_videos)}개")
    print(f"  - FAKE: {len(fake_videos)}개")
    
    # REAL 프레임 추출
    real_frames = []
    for video in tqdm(real_videos, desc="REAL 비디오"):
        frames = extract_frames(video, train_real_dir, frames_per_video)
        real_frames.extend(list(train_real_dir.glob(f"{video.stem}_*.jpg")))
    
    # FAKE 프레임 추출
    fake_frames = []
    for video in tqdm(fake_videos, desc="FAKE 비디오"):
        frames = extract_frames(video, train_fake_dir, frames_per_video)
        fake_frames.extend(list(train_fake_dir.glob(f"{video.stem}_*.jpg")))
    
    # train/val 분할 (80/20)
    random.shuffle(real_frames)
    random.shuffle(fake_frames)
    
    n_real_val = len(real_frames) // 5
    n_fake_val = len(fake_frames) // 5
    
    for img in real_frames[:n_real_val]:
        img.rename(val_real_dir / img.name)
    
    for img in fake_frames[:n_fake_val]:
        img.rename(val_fake_dir / img.name)
    
    print(f"\n✓ 미니 데이터셋 생성 완료!")
    print(f"출력 디렉토리: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='작은 데이터셋 생성')
    parser.add_argument('--source-dir', type=str,
                        help='원본 데이터셋 디렉토리 (real/, fake/ 또는 train/, val/ 포함)')
    parser.add_argument('--output-dir', type=str, default='dataset_small',
                        help='출력 디렉토리 (기본: dataset_small)')
    parser.add_argument('--target-size-mb', type=int, default=1500,
                        help='목표 크기 (MB, 기본: 1500 = 1.5GB)')
    parser.add_argument('--train-ratio', type=float, default=0.8,
                        help='학습 데이터 비율 (기본: 0.8)')
    
    # 비디오에서 직접 생성
    parser.add_argument('--from-videos', action='store_true',
                        help='비디오에서 직접 미니 데이터셋 생성')
    parser.add_argument('--video-dir-real', type=str,
                        help='REAL 비디오 디렉토리')
    parser.add_argument('--video-dir-fake', type=str,
                        help='FAKE 비디오 디렉토리')
    parser.add_argument('--max-videos', type=int, default=10,
                        help='클래스당 최대 비디오 수 (기본: 10)')
    parser.add_argument('--frames-per-video', type=int, default=20,
                        help='비디오당 프레임 수 (기본: 20)')
    
    args = parser.parse_args()
    
    if args.from_videos:
        if not args.video_dir_real or not args.video_dir_fake:
            print("❌ --video-dir-real과 --video-dir-fake가 필요합니다")
            return
        
        create_mini_dataset_from_videos(
            args.video_dir_real,
            args.video_dir_fake,
            args.output_dir,
            max_videos_per_class=args.max_videos,
            frames_per_video=args.frames_per_video
        )
    else:
        if not args.source_dir:
            print("❌ --source-dir가 필요합니다")
            return
        
        create_small_dataset(
            args.source_dir,
            args.output_dir,
            target_size_mb=args.target_size_mb,
            train_ratio=args.train_ratio
        )


if __name__ == "__main__":
    main()



