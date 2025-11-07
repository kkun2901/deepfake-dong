from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch

# GPU 사용 여부 확인
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 모델 로딩을 지연시키기 위해 None으로 초기화
processor1 = None
model1 = None
processor2 = None
model2 = None

def load_models():
    """모델들을 필요할 때만 로딩 (메모리 효율적)"""
    global processor1, model1, processor2, model2
    
    if processor1 is None:
        print("딥페이크 탐지 모델들을 로딩 중...")
        try:
            # 메모리 효율적인 로딩
            processor1 = AutoImageProcessor.from_pretrained("prithivMLmods/Deep-Fake-Detector-v2-Model")
            model1 = AutoModelForImageClassification.from_pretrained(
                "prithivMLmods/Deep-Fake-Detector-v2-Model",
                torch_dtype=torch.float16 if device.type == "cuda" else torch.float32,
                low_cpu_mem_usage=True  # CPU 메모리 사용량 최적화
            ).to(device)
            
            # CPU에서는 하나의 모델만 사용 (메모리 절약)
            if device.type == "cpu":
                print("CPU 환경: 하나의 모델만 사용하여 메모리 절약")
                processor2 = processor1
                model2 = model1
            else:
                processor2 = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
                model2 = AutoModelForImageClassification.from_pretrained(
                    "google/vit-base-patch16-224-in21k",
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True
                ).to(device)
            
            print("모델 로딩 완료!")
        except Exception as e:
            print(f"모델 로딩 실패: {e}")
            # 기본값 설정
            processor1 = processor2 = None
            model1 = model2 = None

def map_label(label: str):
    lower = label.lower()
    if "fake" in lower: return "FAKE"
    elif "real" in lower: return "REAL"
    elif label in ["0", "LABEL_0"]: return "REAL"
    elif label in ["1", "LABEL_1"]: return "FAKE"
    return "REAL"

def predict_image(image_path: str):
    # 모델이 로드되지 않았다면 먼저 로드
    load_models()
    
    image = Image.open(image_path).convert("RGB")

    # 모델1
    inputs1 = processor1(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs1 = model1(**inputs1)
        probs1 = torch.nn.functional.softmax(outputs1.logits, dim=-1)
        conf1, pred1 = torch.max(probs1, dim=1)
    label1 = map_label(model1.config.id2label[pred1.item()])

    # 모델1의 FAKE/REAL 확률 추출
    fake_prob1 = 0.0
    real_prob1 = 0.0
    for idx, class_label in model1.config.id2label.items():
        mapped = map_label(class_label)
        prob = probs1[0][idx].item()
        if mapped == "FAKE":
            fake_prob1 += prob
        elif mapped == "REAL":
            real_prob1 += prob

    # 모델2
    inputs2 = processor2(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs2 = model2(**inputs2)
        probs2 = torch.nn.functional.softmax(outputs2.logits, dim=-1)
        conf2, pred2 = torch.max(probs2, dim=1)
    label2 = map_label(model2.config.id2label[pred2.item()])

    # 모델2의 FAKE/REAL 확률 추출
    fake_prob2 = 0.0
    real_prob2 = 0.0
    for idx, class_label in model2.config.id2label.items():
        mapped = map_label(class_label)
        prob = probs2[0][idx].item()
        if mapped == "FAKE":
            fake_prob2 += prob
        elif mapped == "REAL":
            real_prob2 += prob

    # 디버깅: 각 모델의 확률 확인 (처음 몇 번만 출력)
    import random
    if random.random() < 0.1:  # 10% 확률로만 출력 (너무 많은 로그 방지)
        print(f"[predict_image] 모델1 - fake_prob1: {fake_prob1:.4f}, real_prob1: {real_prob1:.4f}, label1: {label1}")
        print(f"[predict_image] 모델2 - fake_prob2: {fake_prob2:.4f}, real_prob2: {real_prob2:.4f}, label2: {label2}")
    
    # 앙상블: 두 모델의 FAKE/REAL 확률 가중 평균 (confidence 기반)
    # 각 모델의 confidence를 가중치로 사용하여 더 정확한 모델에 더 높은 가중치 부여
    weight1 = conf1.item()
    weight2 = conf2.item()
    total_weight = weight1 + weight2
    
    if total_weight > 0:
        fake_confidence = (fake_prob1 * weight1 + fake_prob2 * weight2) / total_weight
        real_confidence = (real_prob1 * weight1 + real_prob2 * weight2) / total_weight
    else:
        fake_confidence = (fake_prob1 + fake_prob2) / 2.0
        real_confidence = (real_prob1 + real_prob2) / 2.0
    
    # 디버깅: 계산된 fake_confidence 확인
    if random.random() < 0.1:  # 10% 확률로만 출력
        print(f"[predict_image] 계산된 fake_confidence: {fake_confidence:.4f}, real_confidence: {real_confidence:.4f}")

    # 앙상블 로직 개선: 더 공격적인 FAKE 탐지 (실제 딥페이크를 더 잘 탐지)
    # fake_confidence가 0.3 이상이면 FAKE로 판정 (더 낮은 임계값)
    if fake_confidence >= 0.3 or (label1 == "FAKE" and label2 == "FAKE"):
        final_label = "FAKE"
    elif fake_confidence >= 0.25 and (label1 == "FAKE" or label2 == "FAKE"):  # 한 모델만 FAKE이지만 confidence가 어느 정도 있으면 FAKE
        final_label = "FAKE"
    elif fake_confidence >= 0.2 and label1 == "FAKE":  # 한 모델만 FAKE이지만 낮은 confidence도 허용
        final_label = "FAKE"
    elif fake_confidence >= 0.2 and label2 == "FAKE":
        final_label = "FAKE"
    else:
        final_label = "REAL"
    
    avg_confidence = round((conf1.item() + conf2.item()) / 2, 4)

    return {
        "model1": {"label": label1, "confidence": round(conf1.item(), 4)},
        "model2": {"label": label2, "confidence": round(conf2.item(), 4)},
        "ensemble_result": final_label,
        "confidence": avg_confidence,
        "fake_confidence": round(fake_confidence, 4),
        "real_confidence": round(real_confidence, 4)
    }
