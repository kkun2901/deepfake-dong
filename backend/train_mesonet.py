"""
MesoNet 모델 튜닝 스크립트
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import cv2
import numpy as np
from pathlib import Path
import argparse
import time
from tqdm import tqdm
import os

from app.services.model_mesonet import Meso4
from app.core.config import IMAGE_SIZE, MESONET_WEIGHTS

class DeepFakeDataset(Dataset):
    """딥페이크 탐지 데이터셋"""
    
    def __init__(self, data_dir, transform=None, face_crop=True):
        """
        Args:
            data_dir: 데이터셋 루트 디렉토리 (real/, fake/ 폴더 포함)
            transform: 이미지 변환
            face_crop: 얼굴 crop 사용 여부
        """
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.face_crop = face_crop
        self.samples = []
        
        # real 이미지 수집
        real_dir = self.data_dir / "real"
        if real_dir.exists():
            for img_path in real_dir.glob("*.jpg") + real_dir.glob("*.png"):
                self.samples.append((str(img_path), 0))  # 0 = REAL
        
        # fake 이미지 수집
        fake_dir = self.data_dir / "fake"
        if fake_dir.exists():
            for img_path in fake_dir.glob("*.jpg") + fake_dir.glob("*.png"):
                self.samples.append((str(img_path), 1))  # 1 = FAKE
        
        print(f"데이터셋 로드 완료: {len(self.samples)}개 이미지")
        print(f"  - REAL: {sum(1 for _, label in self.samples if label == 0)}개")
        print(f"  - FAKE: {sum(1 for _, label in self.samples if label == 1)}개")
    
    def _crop_face(self, image: np.ndarray):
        """얼굴 영역 crop"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            if len(faces) > 0:
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_face
                margin = int(min(w, h) * 0.2)
                x = max(0, x - margin)
                y = max(0, y - margin)
                w = min(image.shape[1] - x, w + 2 * margin)
                h = min(image.shape[0] - y, h + 2 * margin)
                return image[y:y+h, x:x+w]
            else:
                h, w = image.shape[:2]
                size = min(h, w)
                y, x = (h - size) // 2, (w - size) // 2
                return image[y:y+size, x:x+size]
        except Exception as e:
            return image
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        
        # 이미지 로드
        image = cv2.imread(img_path)
        if image is None:
            raise ValueError(f"이미지를 로드할 수 없습니다: {img_path}")
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 얼굴 crop
        if self.face_crop:
            image = self._crop_face(image)
        
        # PIL Image로 변환
        pil_image = Image.fromarray(image)
        
        # 변환 적용
        if self.transform:
            image_tensor = self.transform(pil_image)
        else:
            image_tensor = transforms.ToTensor()(pil_image)
        
        return image_tensor, torch.tensor(label, dtype=torch.long)


def train_epoch(model, dataloader, criterion, optimizer, device, epoch):
    """한 에포크 학습"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(dataloader, desc=f"Epoch {epoch}")
    for images, labels in pbar:
        images = images.to(device)
        labels = labels.to(device)
        
        # Forward pass
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # 통계
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
        # 진행률 표시
        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'acc': f'{100 * correct / total:.2f}%'
        })
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100 * correct / total
    return epoch_loss, epoch_acc


def validate(model, dataloader, criterion, device):
    """검증"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Validation"):
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100 * correct / total
    return epoch_loss, epoch_acc


def main():
    parser = argparse.ArgumentParser(description='MesoNet 모델 튜닝')
    parser.add_argument('--data-dir', type=str, required=True,
                        help='데이터셋 디렉토리 (real/, fake/ 폴더 포함)')
    parser.add_argument('--val-dir', type=str, default=None,
                        help='검증 데이터셋 디렉토리 (선택사항)')
    parser.add_argument('--epochs', type=int, default=20,
                        help='학습 에포크 수 (기본: 20)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='배치 크기 (기본: 32)')
    parser.add_argument('--lr', type=float, default=0.001,
                        help='학습률 (기본: 0.001)')
    parser.add_argument('--resume', type=str, default=None,
                        help='이전 체크포인트 경로 (선택사항)')
    parser.add_argument('--output-dir', type=str, default='weights',
                        help='모델 저장 디렉토리 (기본: weights)')
    parser.add_argument('--face-crop', action='store_true', default=True,
                        help='얼굴 crop 사용 (기본: True)')
    parser.add_argument('--no-face-crop', dest='face_crop', action='store_false',
                        help='얼굴 crop 사용 안 함')
    parser.add_argument('--gpu', action='store_true',
                        help='GPU 사용 (CUDA 사용 가능 시)')
    
    args = parser.parse_args()
    
    # 디바이스 설정
    device = torch.device("cuda" if args.gpu and torch.cuda.is_available() else "cpu")
    print(f"디바이스: {device}")
    
    # 출력 디렉토리 생성
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # 데이터 변환
    transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])
    
    # 데이터셋 로드
    train_dataset = DeepFakeDataset(args.data_dir, transform=transform, face_crop=args.face_crop)
    train_loader = DataLoader(
        train_dataset, 
        batch_size=args.batch_size, 
        shuffle=True, 
        num_workers=4,
        pin_memory=True if device.type == 'cuda' else False
    )
    
    val_loader = None
    if args.val_dir:
        val_dataset = DeepFakeDataset(args.val_dir, transform=val_transform, face_crop=args.face_crop)
        val_loader = DataLoader(
            val_dataset,
            batch_size=args.batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True if device.type == 'cuda' else False
        )
    
    # 모델 생성
    model = Meso4(num_classes=2)
    
    # 사전 훈련된 가중치 로드 (있는 경우)
    if args.resume:
        print(f"체크포인트 로드: {args.resume}")
        checkpoint = torch.load(args.resume, map_location=device)
        if isinstance(checkpoint, dict):
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            elif 'model' in checkpoint:
                state_dict = checkpoint['model']
            else:
                state_dict = checkpoint
        else:
            state_dict = checkpoint
        
        cleaned = {k.replace('module.', '').replace('model.', ''): v 
                  for k, v in state_dict.items()}
        model.load_state_dict(cleaned, strict=False)
        print("✓ 체크포인트 로드 완료")
    elif Path(MESONET_WEIGHTS).exists():
        print(f"사전 훈련된 가중치 로드: {MESONET_WEIGHTS}")
        checkpoint = torch.load(MESONET_WEIGHTS, map_location=device)
        if isinstance(checkpoint, dict):
            state_dict = checkpoint.get('state_dict', checkpoint.get('model', checkpoint))
        else:
            state_dict = checkpoint
        cleaned = {k.replace('module.', '').replace('model.', ''): v 
                  for k, v in state_dict.items()}
        model.load_state_dict(cleaned, strict=False)
        print("✓ 사전 훈련된 가중치 로드 완료")
    
    model = model.to(device)
    
    # 손실 함수 및 옵티마이저
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=3, verbose=True
    )
    
    # 학습 시작
    print("\n" + "=" * 60)
    print("MesoNet 모델 학습 시작")
    print("=" * 60)
    print(f"에포크: {args.epochs}")
    print(f"배치 크기: {args.batch_size}")
    print(f"학습률: {args.lr}")
    print(f"얼굴 crop: {args.face_crop}")
    print("=" * 60 + "\n")
    
    best_val_acc = 0.0
    train_losses = []
    train_accs = []
    val_losses = []
    val_accs = []
    
    for epoch in range(1, args.epochs + 1):
        # 학습
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )
        train_losses.append(train_loss)
        train_accs.append(train_acc)
        
        # 검증
        if val_loader:
            val_loss, val_acc = validate(model, val_loader, criterion, device)
            val_losses.append(val_loss)
            val_accs.append(val_acc)
            scheduler.step(val_loss)
            
            print(f"\nEpoch {epoch}/{args.epochs}:")
            print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
            print(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
            
            # 최고 성능 모델 저장
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_model_path = output_dir / "mesonet_best.pth"
                torch.save({
                    'epoch': epoch,
                    'state_dict': model.state_dict(),
                    'train_acc': train_acc,
                    'val_acc': val_acc,
                    'train_loss': train_loss,
                    'val_loss': val_loss,
                }, best_model_path)
                print(f"  ✓ 최고 성능 모델 저장: {best_model_path}")
        else:
            scheduler.step(train_loss)
            print(f"\nEpoch {epoch}/{args.epochs}:")
            print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        
        # 주기적 체크포인트 저장
        if epoch % 5 == 0:
            checkpoint_path = output_dir / f"mesonet_epoch_{epoch}.pth"
            torch.save({
                'epoch': epoch,
                'state_dict': model.state_dict(),
                'train_acc': train_acc,
                'val_acc': val_acc if val_loader else train_acc,
                'train_loss': train_loss,
                'val_loss': val_loss if val_loader else train_loss,
                'optimizer': optimizer.state_dict(),
            }, checkpoint_path)
            print(f"  ✓ 체크포인트 저장: {checkpoint_path}")
        
        print()
    
    # 최종 모델 저장
    final_model_path = output_dir / "mesonet_final.pth"
    torch.save({
        'epoch': args.epochs,
        'state_dict': model.state_dict(),
        'train_acc': train_accs[-1],
        'val_acc': val_accs[-1] if val_accs else train_accs[-1],
        'train_loss': train_losses[-1],
        'val_loss': val_losses[-1] if val_losses else train_losses[-1],
    }, final_model_path)
    print(f"✓ 최종 모델 저장: {final_model_path}")
    
    print("\n" + "=" * 60)
    print("학습 완료!")
    print("=" * 60)
    if val_loader:
        print(f"최고 검증 정확도: {best_val_acc:.2f}%")
    print(f"최종 모델: {final_model_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()



