"""
CPU 최적화 MesoNet-4 학습/평가/추론 전체 코드
- CPU ONLY 학습 (GPU 코드 없음)
- 영상 단위 데이터 분할 (프레임 단위 split 금지)
- 256x256 입력 크기
- EarlyStopping, Confusion Matrix, Threshold 튜닝 포함
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, Subset
from torchvision import transforms, datasets
from torchvision.transforms import functional as TF
import numpy as np
from pathlib import Path
import json
import re
from collections import defaultdict
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score
import argparse
import os
import time
from PIL import Image

# ============================================================================
# CPU 최적화 설정
# ============================================================================

# CPU 전용 설정
torch.set_num_threads(4)  # CPU 스레드 수 설정
device = torch.device("cpu")
print(f"디바이스: {device}")
print(f"CPU 스레드 수: {torch.get_num_threads()}")

# ============================================================================
# 데이터 전처리 및 증강
# ============================================================================

def get_train_transform():
    """학습용 전처리 및 증강"""
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),  # ±10도 회전
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # -1~1 정규화
    ])

def get_val_transform():
    """검증/테스트용 전처리 (증강 없음)"""
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])

# ============================================================================
# 영상 단위 데이터 분할 (중요!)
# ============================================================================

def extract_video_id(filename):
    """
    파일명에서 비디오 ID 추출
    예: "video001_frame001.jpg" -> "video001"
        "abc_123_0001.jpg" -> "abc_123"
    """
    # 일반적인 패턴: videoID_frameID.jpg
    match = re.match(r'^(.+?)_frame\d+', filename)
    if match:
        return match.group(1)
    
    # 다른 패턴: videoID_숫자.jpg
    match = re.match(r'^(.+?)_\d+\.', filename)
    if match:
        return match.group(1)
    
    # 기본: 확장자 제거 후 마지막 언더스코어까지
    name = Path(filename).stem
    if '_' in name:
        return '_'.join(name.split('_')[:-1])
    
    return name

def split_by_video(dataset_root, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, seed=42):
    """
    영상 단위로 데이터셋 분할
    같은 비디오에서 나온 프레임들은 모두 같은 split에 들어감
    
    Args:
        dataset_root: 데이터셋 루트 (REAL/, FAKE/ 폴더 포함)
        train_ratio: 학습 데이터 비율
        val_ratio: 검증 데이터 비율
        test_ratio: 테스트 데이터 비율
    
    Returns:
        train_files, val_files, test_files: 각 split의 파일 경로 리스트
    """
    np.random.seed(seed)
    
    dataset_root = Path(dataset_root)
    real_dir = dataset_root / "REAL"
    fake_dir = dataset_root / "FAKE"
    
    # 비디오 ID별로 파일 그룹화
    def group_by_video(directory, label):
        video_groups = defaultdict(list)
        for img_path in directory.glob("*.jpg"):
            video_id = extract_video_id(img_path.name)
            video_groups[video_id].append((str(img_path), label))
        return video_groups
    
    real_videos = group_by_video(real_dir, 0)  # 0 = REAL
    fake_videos = group_by_video(fake_dir, 1)  # 1 = FAKE
    
    print(f"REAL 비디오 수: {len(real_videos)}")
    print(f"FAKE 비디오 수: {len(fake_videos)}")
    
    # 비디오 ID 리스트
    all_video_ids = list(real_videos.keys()) + list(fake_videos.keys())
    np.random.shuffle(all_video_ids)
    
    # 비디오 단위로 split
    n_total = len(all_video_ids)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)
    
    train_video_ids = set(all_video_ids[:n_train])
    val_video_ids = set(all_video_ids[n_train:n_train+n_val])
    test_video_ids = set(all_video_ids[n_train+n_val:])
    
    # 각 split의 파일 수집
    train_files = []
    val_files = []
    test_files = []
    
    for video_id, files in real_videos.items():
        if video_id in train_video_ids:
            train_files.extend(files)
        elif video_id in val_video_ids:
            val_files.extend(files)
        else:
            test_files.extend(files)
    
    for video_id, files in fake_videos.items():
        if video_id in train_video_ids:
            train_files.extend(files)
        elif video_id in val_video_ids:
            val_files.extend(files)
        else:
            test_files.extend(files)
    
    print(f"\n데이터 분할 결과:")
    print(f"  Train: {len(train_files)}개 이미지 ({len(train_video_ids)}개 비디오)")
    print(f"  Val: {len(val_files)}개 이미지 ({len(val_video_ids)}개 비디오)")
    print(f"  Test: {len(test_files)}개 이미지 ({len(test_video_ids)}개 비디오)")
    
    return train_files, val_files, test_files

class VideoSplitDataset(Dataset):
    """영상 단위로 분할된 데이터셋"""
    
    def __init__(self, file_list, transform=None, face_crop=False):
        """
        Args:
            file_list: [(file_path, label), ...] 형태의 리스트
            transform: 이미지 변환
            face_crop: 얼굴 crop 사용 여부 (백엔드와 일치시키기 위해)
        """
        self.file_list = file_list
        self.transform = transform
        self.face_crop = face_crop
        if face_crop:
            import cv2
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
    
    def _crop_face(self, image: np.ndarray):
        """얼굴 영역 crop (백엔드와 동일한 로직)"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                # 가장 큰 얼굴 선택
                largest_face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = largest_face
                
                # 여유 공간 추가 (20%)
                margin = int(min(w, h) * 0.2)
                x = max(0, x - margin)
                y = max(0, y - margin)
                w = min(image.shape[1] - x, w + 2 * margin)
                h = min(image.shape[0] - y, h + 2 * margin)
                
                # 얼굴 영역 crop
                face_image = image[y:y+h, x:x+w]
                return face_image
            else:
                # 얼굴이 감지되지 않으면 중앙 crop
                h, w = image.shape[:2]
                size = min(h, w)
                y = (h - size) // 2
                x = (w - size) // 2
                return image[y:y+size, x:x+size]
        except Exception as e:
            print(f"얼굴 crop 오류: {e}, 원본 이미지 사용")
            return image
    
    def __len__(self):
        return len(self.file_list)
    
    def __getitem__(self, idx):
        img_path, label = self.file_list[idx]
        
        # 이미지 로드
        if self.face_crop:
            # 얼굴 crop을 위해 OpenCV로 로드
            import cv2
            image = cv2.imread(str(img_path))
            if image is None:
                raise ValueError(f"이미지를 로드할 수 없습니다: {img_path}")
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # 얼굴 crop
            image = self._crop_face(image)
            # PIL Image로 변환
            image = Image.fromarray(image)
        else:
            # 전체 이미지 사용
            image = Image.open(img_path).convert('RGB')
        
        # 변환 적용
        if self.transform:
            image = self.transform(image)
        
        return image, label

# ============================================================================
# MesoNet-4 모델 (256x256 입력용)
# ============================================================================

class Meso4(nn.Module):
    """MesoNet-4 모델 (256x256 입력)"""
    
    def __init__(self, num_classes=2, dropout_rate=0.4):
        super(Meso4, self).__init__()
        
        # 첫 번째 블록
        self.conv1 = nn.Conv2d(3, 8, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(8)
        self.conv2 = nn.Conv2d(8, 8, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm2d(8)
        self.pool1 = nn.MaxPool2d(2, 2)  # 256 -> 128
        self.drop1 = nn.Dropout2d(dropout_rate)
        
        # 두 번째 블록
        self.conv3 = nn.Conv2d(8, 16, kernel_size=5, padding=2)
        self.bn3 = nn.BatchNorm2d(16)
        self.conv4 = nn.Conv2d(16, 16, kernel_size=5, padding=2)
        self.bn4 = nn.BatchNorm2d(16)
        self.pool2 = nn.MaxPool2d(2, 2)  # 128 -> 64
        self.drop2 = nn.Dropout2d(dropout_rate)
        
        # 세 번째 블록
        self.conv5 = nn.Conv2d(16, 16, kernel_size=5, padding=2)
        self.bn5 = nn.BatchNorm2d(16)
        self.conv6 = nn.Conv2d(16, 16, kernel_size=5, padding=2)
        self.bn6 = nn.BatchNorm2d(16)
        self.pool3 = nn.MaxPool2d(2, 2)  # 64 -> 32
        self.drop3 = nn.Dropout2d(dropout_rate)
        
        # Fully Connected
        # 256x256 -> 32x32 after 3 pools
        self.fc1 = nn.Linear(16 * 32 * 32, 16)
        self.bn7 = nn.BatchNorm1d(16)
        self.drop4 = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(16, num_classes)
    
    def forward(self, x):
        # 첫 번째 블록
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool1(x)
        x = self.drop1(x)
        
        # 두 번째 블록
        x = F.relu(self.bn3(self.conv3(x)))
        x = F.relu(self.bn4(self.conv4(x)))
        x = self.pool2(x)
        x = self.drop2(x)
        
        # 세 번째 블록
        x = F.relu(self.bn5(self.conv5(x)))
        x = F.relu(self.bn6(self.conv6(x)))
        x = self.pool3(x)
        x = self.drop3(x)
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        # Fully Connected
        x = F.relu(self.bn7(self.fc1(x)))
        x = self.drop4(x)
        x = self.fc2(x)
        
        return x

# ============================================================================
# 학습 함수
# ============================================================================

def train_epoch(model, dataloader, criterion, optimizer, device):
    """한 에포크 학습"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(dataloader, desc="Train")
    for images, labels in pbar:
        images = images.to(device)
        labels = labels.to(device)
        
        # Forward
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward
        loss.backward()
        optimizer.step()
        
        # 통계
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'acc': f'{100*correct/total:.2f}%'
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
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Val"):
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    epoch_loss = running_loss / len(dataloader)
    epoch_acc = 100 * correct / total
    return epoch_loss, epoch_acc, all_preds, all_labels

class EarlyStopping:
    """Early Stopping 클래스"""
    
    def __init__(self, patience=5, min_delta=0, mode='min'):
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.counter = 0
        self.best_score = None
        self.early_stop = False
    
    def __call__(self, score):
        if self.best_score is None:
            self.best_score = score
        elif self.mode == 'min':
            if score < self.best_score - self.min_delta:
                self.best_score = score
                self.counter = 0
            else:
                self.counter += 1
        else:  # mode == 'max'
            if score > self.best_score + self.min_delta:
                self.best_score = score
                self.counter = 0
            else:
                self.counter += 1
        
        if self.counter >= self.patience:
            self.early_stop = True
        
        return self.early_stop

def train_model(model, train_loader, val_loader, epochs=30, lr=1e-3, 
                patience=5, save_path='best_model.pt', class_weights=None):
    """모델 학습"""
    
    # 데이터 불균형 처리: class_weight 사용
    if class_weights is not None:
        criterion = nn.CrossEntropyLoss(weight=class_weights.to(device))
        print(f"✓ Class weights 적용: {class_weights}")
    else:
        criterion = nn.CrossEntropyLoss()
    
    optimizer = optim.Adam(model.parameters(), lr=lr)
    early_stopping = EarlyStopping(patience=patience, mode='min')
    
    train_losses = []
    train_accs = []
    val_losses = []
    val_accs = []
    best_val_loss = float('inf')
    
    print("\n" + "="*60)
    print("학습 시작")
    print("="*60)
    
    for epoch in range(1, epochs + 1):
        print(f"\nEpoch {epoch}/{epochs}")
        print("-" * 60)
        
        # 학습
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        train_losses.append(train_loss)
        train_accs.append(train_acc)
        
        # 검증
        val_loss, val_acc, val_preds, val_labels = validate(model, val_loader, criterion, device)
        val_losses.append(val_loss)
        val_accs.append(val_acc)
        
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # 최고 모델 저장
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_acc': val_acc,
            }, save_path)
            print(f"✓ 최고 모델 저장: {save_path}")
        
        # Early Stopping
        if early_stopping(val_loss):
            print(f"\nEarly Stopping! (patience={patience})")
            break
    
    print("\n" + "="*60)
    print("학습 완료!")
    print("="*60)
    
    return {
        'train_losses': train_losses,
        'train_accs': train_accs,
        'val_losses': val_losses,
        'val_accs': val_accs
    }

# ============================================================================
# 평가 함수
# ============================================================================

def plot_confusion_matrix(y_true, y_pred, class_names=['REAL', 'FAKE'], save_path='confusion_matrix.png'):
    """Confusion Matrix 시각화"""
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Confusion Matrix 저장: {save_path}")
    plt.close()
    
    # 정확도 출력
    accuracy = accuracy_score(y_true, y_pred)
    print(f"\n정확도: {accuracy*100:.2f}%")
    print(f"\nConfusion Matrix:")
    print(f"              REAL  FAKE")
    print(f"REAL (실제)   {cm[0][0]:4d}  {cm[0][1]:4d}")
    print(f"FAKE (실제)   {cm[1][0]:4d}  {cm[1][1]:4d}")

def evaluate_model(model, test_loader, device, save_cm=True):
    """모델 평가"""
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="Test"):
            images = images.to(device)
            labels = labels.to(device)
            
            outputs = model(images)
            probs = F.softmax(outputs, dim=1)
            _, predicted = torch.max(outputs, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs[:, 1].cpu().numpy())  # FAKE 확률
    
    # Confusion Matrix
    if save_cm:
        plot_confusion_matrix(all_labels, all_preds)
    
    accuracy = accuracy_score(all_labels, all_preds)
    print(f"\n테스트 정확도: {accuracy*100:.2f}%")
    
    return all_labels, all_preds, all_probs

# ============================================================================
# 추론 함수
# ============================================================================

def predict_image(model, image_path, device, transform=None):
    """
    단일 이미지 예측
    
    Returns:
        fake_prob: FAKE일 확률 (0~1)
        label: 'REAL' or 'FAKE'
    """
    if transform is None:
        transform = get_val_transform()
    
    model.eval()
    
    # 이미지 로드 및 전처리
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    # 예측
    with torch.no_grad():
        output = model(image_tensor)
        probs = F.softmax(output, dim=1)
        fake_prob = probs[0][1].item()  # FAKE 확률
        label = 'FAKE' if fake_prob > 0.5 else 'REAL'
    
    return fake_prob, label

def predict_folder(model, folder_path, device, transform=None):
    """
    폴더 내 모든 이미지 예측
    
    Returns:
        results: [(file_path, fake_prob, label), ...]
    """
    folder_path = Path(folder_path)
    image_files = list(folder_path.glob("*.jpg")) + list(folder_path.glob("*.png"))
    
    results = []
    for img_path in tqdm(image_files, desc="Predicting"):
        fake_prob, label = predict_image(model, img_path, device, transform)
        results.append((str(img_path), fake_prob, label))
    
    return results

# ============================================================================
# Threshold 튜닝 함수
# ============================================================================

def tune_threshold(predictions):
    """
    여러 프레임의 예측값으로부터 threshold 계산
    
    Args:
        predictions: P(fake) 값들의 리스트 [0.3, 0.7, 0.5, ...]
    
    Returns:
        mean: 평균값
        std: 표준편차
        recommended_threshold: 권장 threshold
    """
    predictions = np.array(predictions)
    
    mean = np.mean(predictions)
    std = np.std(predictions)
    
    # 권장 threshold: 평균 + 표준편차 (보수적 접근)
    # 또는 평균만 사용 (일반적)
    recommended_threshold = mean
    
    print(f"\nThreshold 튜닝 결과:")
    print(f"  평균 (mean): {mean:.4f}")
    print(f"  표준편차 (std): {std:.4f}")
    print(f"  권장 threshold: {recommended_threshold:.4f}")
    print(f"  (보수적 threshold: {mean + std:.4f})")
    print(f"  (공격적 threshold: {mean - std:.4f})")
    
    return mean, std, recommended_threshold

# ============================================================================
# 메인 함수
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='CPU 최적화 MesoNet-4 학습')
    parser.add_argument('--data-dir', type=str, required=True,
                        help='데이터셋 디렉토리 (REAL/, FAKE/ 폴더 포함)')
    parser.add_argument('--epochs', type=int, default=30,
                        help='학습 에포크 수 (기본: 30)')
    parser.add_argument('--batch-size', type=int, default=8,
                        help='배치 크기 (기본: 8)')
    parser.add_argument('--lr', type=float, default=1e-3,
                        help='학습률 (기본: 1e-3)')
    parser.add_argument('--patience', type=int, default=5,
                        help='Early stopping patience (기본: 5)')
    parser.add_argument('--dropout', type=float, default=0.4,
                        help='Dropout 비율 (기본: 0.4)')
    parser.add_argument('--train-ratio', type=float, default=0.7,
                        help='학습 데이터 비율 (기본: 0.7)')
    parser.add_argument('--val-ratio', type=float, default=0.15,
                        help='검증 데이터 비율 (기본: 0.15)')
    parser.add_argument('--test-ratio', type=float, default=0.15,
                        help='테스트 데이터 비율 (기본: 0.15)')
    parser.add_argument('--save-model', type=str, default='best_model.pt',
                        help='모델 저장 경로 (기본: best_model.pt)')
    parser.add_argument('--mode', type=str, choices=['train', 'eval', 'predict', 'tune'],
                        default='train', help='실행 모드')
    parser.add_argument('--model-path', type=str, default='best_model.pt',
                        help='평가/추론용 모델 경로')
    parser.add_argument('--predict-path', type=str,
                        help='예측할 이미지/폴더 경로')
    
    args = parser.parse_args()
    
    # 데이터셋 분할 (영상 단위)
    print("="*60)
    print("데이터셋 분할 (영상 단위)")
    print("="*60)
    train_files, val_files, test_files = split_by_video(
        args.data_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
    )
    
    # 데이터셋 생성
    train_dataset = VideoSplitDataset(train_files, transform=get_train_transform())
    val_dataset = VideoSplitDataset(val_files, transform=get_val_transform())
    test_dataset = VideoSplitDataset(test_files, transform=get_val_transform())
    
    # DataLoader 생성 (num_workers=0 for CPU)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, 
                              shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, 
                            shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, 
                             shuffle=False, num_workers=0)
    
    # 모델 생성
    model = Meso4(num_classes=2, dropout_rate=args.dropout).to(device)
    
    # 파라미터 수 출력
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n모델 파라미터 수: {total_params:,} (학습 가능: {trainable_params:,})")
    
    # 데이터 불균형 처리: class_weight 계산
    if args.mode == 'train':
        real_count = sum(1 for _, label in train_files if label == 0)
        fake_count = sum(1 for _, label in train_files if label == 1)
        total_count = real_count + fake_count
        
        # class_weight 계산 (적은 클래스에 더 높은 가중치)
        weight_real = total_count / (2.0 * real_count) if real_count > 0 else 1.0
        weight_fake = total_count / (2.0 * fake_count) if fake_count > 0 else 1.0
        class_weights = torch.tensor([weight_real, weight_fake], dtype=torch.float32)
        
        print(f"\n데이터 불균형 처리:")
        print(f"  REAL: {real_count}개, FAKE: {fake_count}개")
        print(f"  Class weights: REAL={weight_real:.3f}, FAKE={weight_fake:.3f}")
        
        # 학습
        history = train_model(
            model, train_loader, val_loader,
            epochs=args.epochs,
            lr=args.lr,
            patience=args.patience,
            save_path=args.save_model,
            class_weights=class_weights
        )
        
        # 최고 모델 로드하여 테스트
        print("\n" + "="*60)
        print("테스트 평가")
        print("="*60)
        checkpoint = torch.load(args.save_model, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        evaluate_model(model, test_loader, device)
    
    elif args.mode == 'eval':
        # 평가만
        checkpoint = torch.load(args.model_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        evaluate_model(model, test_loader, device)
    
    elif args.mode == 'predict':
        # 추론
        checkpoint = torch.load(args.model_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        
        predict_path = Path(args.predict_path)
        if predict_path.is_file():
            # 단일 이미지
            fake_prob, label = predict_image(model, predict_path, device)
            print(f"\n파일: {predict_path}")
            print(f"FAKE 확률: {fake_prob:.4f}")
            print(f"예측: {label}")
        else:
            # 폴더
            results = predict_folder(model, predict_path, device)
            print(f"\n예측 결과:")
            for file_path, fake_prob, label in results[:10]:  # 처음 10개만 출력
                print(f"  {Path(file_path).name}: {fake_prob:.4f} -> {label}")
            print(f"\n총 {len(results)}개 파일 예측 완료")
    
    elif args.mode == 'tune':
        # Threshold 튜닝
        checkpoint = torch.load(args.model_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        
        # 테스트 데이터로 예측
        all_probs = []
        with torch.no_grad():
            for images, _ in tqdm(test_loader, desc="Predicting for threshold"):
                images = images.to(device)
                outputs = model(images)
                probs = F.softmax(outputs, dim=1)
                all_probs.extend(probs[:, 1].cpu().numpy())
        
        tune_threshold(all_probs)

if __name__ == "__main__":
    main()

