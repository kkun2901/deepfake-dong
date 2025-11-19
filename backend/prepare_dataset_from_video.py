"""
비디오 데이터셋에서 이미지 프레임 추출 및 데이터셋 준비 스크립트
DFDC, FaceForensics++ 등 비디오 데이터셋을 MesoNet 학습용 이미지로 변환
"""
import cv2
import os
import argparse
from pathlib import Path
from tqdm import tqdm
import json
import random

def extract_frames_from_video(video_path, output_dir, label, frame_interval=10, max_frames=None):
    """
    비디오에서 프레임 추출
    
    Args:
        video_path: 비디오 파일 경로
        output_dir: 출력 디렉토리
        label: 레이블 (0=REAL, 1=FAKE)
        frame_interval: N프레임마다 추출 (기본: 10)
        max_frames: 최대 추출 프레임 수 (None이면 제한 없음)
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"⚠ 비디오를 열 수 없습니다: {video_path}")
        return 0
    
    frame_count = 0
    saved_count = 0
    video_name = video_path.stem
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # frame_interval마다 프레임 저장
        if frame_count % frame_interval == 0:
            if max_frames and saved_count >= max_frames:
                break
            
            output_path = output_dir / f"{video_name}_{frame_count:06d}.jpg"
            cv2.imwrite(str(output_path), frame)
            saved_count += 1
        
        frame_count += 1
    
    cap.release()
    return saved_count


def process_video_dataset(video_dir, output_dir, label, frame_interval=10, max_frames_per_video=50):
    """
    비디오 디렉토리에서 모든 비디오 처리
    
    Args:
        video_dir: 비디오 파일들이 있는 디렉토리
        output_dir: 출력 디렉토리
        label: 레이블 (0=REAL, 1=FAKE)
        frame_interval: N프레임마다 추출
        max_frames_per_video: 비디오당 최대 프레임 수
    """
    video_dir = Path(video_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 지원하는 비디오 확장자
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    
    # 비디오 파일 찾기
    video_files = []
    for ext in video_extensions:
        video_files.extend(list(video_dir.glob(f"*{ext}")))
        video_files.extend(list(video_dir.glob(f"*{ext.upper()}")))
    
    if not video_files:
        print(f"⚠ 비디오 파일을 찾을 수 없습니다: {video_dir}")
        return 0
    
    print(f"📹 {len(video_files)}개 비디오 파일 발견")
    
    total_frames = 0
    for video_path in tqdm(video_files, desc="비디오 처리"):
        frames = extract_frames_from_video(
            video_path, output_dir, label, 
            frame_interval=frame_interval,
            max_frames=max_frames_per_video
        )
        total_frames += frames
    
    print(f"✓ 총 {total_frames}개 프레임 추출 완료: {output_dir}")
    return total_frames


def split_dataset(data_dir, train_ratio=0.8, val_ratio=0.2):
    """
    데이터셋을 train/val로 분할
    
    Args:
        data_dir: 데이터셋 루트 디렉토리 (real/, fake/ 폴더 포함)
        train_ratio: 학습 데이터 비율
        val_ratio: 검증 데이터 비율
    """
    data_dir = Path(data_dir)
    
    for label_dir in ['real', 'fake']:
        source_dir = data_dir / label_dir
        if not source_dir.exists():
            continue
        
        # 모든 이미지 파일 찾기
        image_files = list(source_dir.glob("*.jpg")) + list(source_dir.glob("*.png"))
        random.shuffle(image_files)
        
        # 분할
        n_total = len(image_files)
        n_train = int(n_total * train_ratio)
        
        train_files = image_files[:n_train]
        val_files = image_files[n_train:]
        
        # train/val 디렉토리 생성
        train_dir = data_dir / "train" / label_dir
        val_dir = data_dir / "val" / label_dir
        train_dir.mkdir(parents=True, exist_ok=True)
        val_dir.mkdir(parents=True, exist_ok=True)
        
        # 파일 이동
        for img_file in tqdm(train_files, desc=f"{label_dir} train 이동"):
            img_file.rename(train_dir / img_file.name)
        
        for img_file in tqdm(val_files, desc=f"{label_dir} val 이동"):
            img_file.rename(val_dir / img_file.name)
        
        print(f"✓ {label_dir}: train={len(train_files)}, val={len(val_files)}")


def main():
    parser = argparse.ArgumentParser(description='비디오 데이터셋에서 이미지 프레임 추출')
    parser.add_argument('--video-dir', type=str, required=True,
                        help='비디오 파일들이 있는 디렉토리')
    parser.add_argument('--output-dir', type=str, required=True,
                        help='출력 디렉토리')
    parser.add_argument('--label', type=int, required=True, choices=[0, 1],
                        help='레이블 (0=REAL, 1=FAKE)')
    parser.add_argument('--frame-interval', type=int, default=10,
                        help='N프레임마다 추출 (기본: 10)')
    parser.add_argument('--max-frames-per-video', type=int, default=50,
                        help='비디오당 최대 프레임 수 (기본: 50)')
    parser.add_argument('--split', action='store_true',
                        help='데이터셋을 train/val로 자동 분할')
    parser.add_argument('--train-ratio', type=float, default=0.8,
                        help='학습 데이터 비율 (기본: 0.8)')
    
    args = parser.parse_args()
    
    # 프레임 추출
    if args.label == 0:
        label_name = "real"
    else:
        label_name = "fake"
    
    print("=" * 60)
    print(f"비디오에서 프레임 추출: {label_name}")
    print("=" * 60)
    
    total_frames = process_video_dataset(
        args.video_dir,
        args.output_dir,
        args.label,
        frame_interval=args.frame_interval,
        max_frames_per_video=args.max_frames_per_video
    )
    
    # 데이터셋 분할
    if args.split:
        print("\n" + "=" * 60)
        print("데이터셋 train/val 분할")
        print("=" * 60)
        
        # real과 fake 모두 처리하기 위해 상위 디렉토리 사용
        parent_dir = Path(args.output_dir).parent
        split_dataset(parent_dir, train_ratio=args.train_ratio)
        
        print("\n✓ 데이터셋 준비 완료!")
        print(f"다음 명령으로 학습을 시작하세요:")
        print(f"python train_mesonet.py --data-dir {parent_dir}/train --val-dir {parent_dir}/val")


if __name__ == "__main__":
    main()



