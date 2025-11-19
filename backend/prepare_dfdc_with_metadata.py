"""
DFDC Preview Dataset에서 메타데이터를 사용하여 REAL/FAKE 자동 분류 및 프레임 추출
"""
import json
import cv2
import argparse
from pathlib import Path
from tqdm import tqdm
import random

def extract_frames_with_metadata(video_dir, metadata_path, output_dir, 
                                  frame_interval=15, max_frames_per_video=40,
                                  train_ratio=0.8):
    """
    메타데이터를 사용하여 REAL/FAKE 자동 분류 및 프레임 추출
    
    Args:
        video_dir: 비디오 파일들이 있는 디렉토리
        metadata_path: metadata.json 파일 경로
        output_dir: 출력 디렉토리
        frame_interval: N프레임마다 추출 (사용 안 함, max_frames_per_video로 대체)
        max_frames_per_video: 비디오당 최대 프레임 수
        train_ratio: 학습 데이터 비율
    """
    # 메타데이터 로드
    print(f"메타데이터 로드: {metadata_path}")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    video_dir = Path(video_dir)
    output_dir = Path(output_dir)
    
    # 출력 디렉토리 생성
    train_real = output_dir / "train" / "real"
    train_fake = output_dir / "train" / "fake"
    val_real = output_dir / "val" / "real"
    val_fake = output_dir / "val" / "fake"
    
    for dir_path in [train_real, train_fake, val_real, val_fake]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # 비디오 파일 찾기
    video_files = list(video_dir.glob("*.mp4"))
    print(f"비디오 파일: {len(video_files)}개 발견")
    
    # REAL과 FAKE 비디오 분류
    real_videos = []
    fake_videos = []
    
    for video_path in video_files:
        video_name = video_path.stem
        
        if video_name not in metadata:
            print(f"⚠ 메타데이터에 없는 비디오: {video_name}")
            continue
        
        label = metadata[video_name].get('label', 'REAL')
        if label == 'REAL':
            real_videos.append(video_path)
        else:
            fake_videos.append(video_path)
    
    print(f"REAL 비디오: {len(real_videos)}개")
    print(f"FAKE 비디오: {len(fake_videos)}개")
    
    # train/val 분할
    random.shuffle(real_videos)
    random.shuffle(fake_videos)
    
    n_real_train = int(len(real_videos) * train_ratio)
    n_fake_train = int(len(fake_videos) * train_ratio)
    
    real_train = real_videos[:n_real_train]
    real_val = real_videos[n_real_train:]
    fake_train = fake_videos[:n_fake_train]
    fake_val = fake_videos[n_fake_train:]
    
    print(f"\n분할:")
    print(f"  REAL - train: {len(real_train)}, val: {len(real_val)}")
    print(f"  FAKE - train: {len(fake_train)}, val: {len(fake_val)}")
    
    # 프레임 추출 함수
    def extract_frames(video_path, output_dir, max_frames):
        """비디오에서 프레임 추출"""
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return 0
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames == 0:
            cap.release()
            return 0
        
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
    
    # REAL train 프레임 추출
    print("\n[1/4] REAL train 프레임 추출 중...")
    total_real_train = 0
    for video in tqdm(real_train, desc="REAL train"):
        frames = extract_frames(video, train_real, max_frames_per_video)
        total_real_train += frames
    
    # REAL val 프레임 추출
    print("\n[2/4] REAL val 프레임 추출 중...")
    total_real_val = 0
    for video in tqdm(real_val, desc="REAL val"):
        frames = extract_frames(video, val_real, max_frames_per_video)
        total_real_val += frames
    
    # FAKE train 프레임 추출
    print("\n[3/4] FAKE train 프레임 추출 중...")
    total_fake_train = 0
    for video in tqdm(fake_train, desc="FAKE train"):
        frames = extract_frames(video, train_fake, max_frames_per_video)
        total_fake_train += frames
    
    # FAKE val 프레임 추출
    print("\n[4/4] FAKE val 프레임 추출 중...")
    total_fake_val = 0
    for video in tqdm(fake_val, desc="FAKE val"):
        frames = extract_frames(video, val_fake, max_frames_per_video)
        total_fake_val += frames
    
    print("\n" + "=" * 60)
    print("프레임 추출 완료!")
    print("=" * 60)
    print(f"REAL train: {total_real_train}개 프레임")
    print(f"REAL val: {total_real_val}개 프레임")
    print(f"FAKE train: {total_fake_train}개 프레임")
    print(f"FAKE val: {total_fake_val}개 프레임")
    print(f"총: {total_real_train + total_real_val + total_fake_train + total_fake_val}개 프레임")
    print(f"출력 디렉토리: {output_dir}")
    print("=" * 60)
    
    # 크기 확인 (대략적)
    try:
        import os
        total_size = 0
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                filepath = os.path.join(root, file)
                total_size += os.path.getsize(filepath)
        
        size_mb = total_size / (1024 * 1024)
        size_gb = size_mb / 1024
        print(f"\n데이터셋 크기: {size_mb:.2f}MB ({size_gb:.2f}GB)")
    except:
        pass


def main():
    parser = argparse.ArgumentParser(description='DFDC Preview Dataset 프레임 추출 (메타데이터 기반)')
    parser.add_argument('--video-dir', type=str, required=True,
                        help='비디오 파일들이 있는 디렉토리')
    parser.add_argument('--metadata', type=str, required=True,
                        help='metadata.json 파일 경로')
    parser.add_argument('--output-dir', type=str, default='dataset_2gb',
                        help='출력 디렉토리 (기본: dataset_2gb)')
    parser.add_argument('--max-frames-per-video', type=int, default=40,
                        help='비디오당 최대 프레임 수 (기본: 40)')
    parser.add_argument('--train-ratio', type=float, default=0.8,
                        help='학습 데이터 비율 (기본: 0.8)')
    parser.add_argument('--seed', type=int, default=42,
                        help='랜덤 시드 (기본: 42)')
    
    args = parser.parse_args()
    
    # 랜덤 시드 설정
    random.seed(args.seed)
    
    extract_frames_with_metadata(
        video_dir=args.video_dir,
        metadata_path=args.metadata,
        output_dir=args.output_dir,
        max_frames_per_video=args.max_frames_per_video,
        train_ratio=args.train_ratio
    )
    
    print("\n✓ 데이터셋 준비 완료!")
    print(f"\n학습 명령:")
    print(f"python train_mesonet.py --data-dir {args.output_dir}/train --val-dir {args.output_dir}/val --epochs 20 --batch-size 32")


if __name__ == "__main__":
    main()



