# 🔥 Firebase 관련 필요 사항 정리

## 현재 Firebase 사용 현황

### ✅ 현재 구현된 것

#### Backend
- ✅ **Firebase Admin SDK** 설정 완료
  - 위치: `backend/app/core/firebase.py`
  - 프로젝트: `deepfake-fc59d`
  - Service Account Key: `firebase-key.json`
- ✅ **Firebase Storage** 사용 중
  - 비디오 파일 저장
  - Bucket: `deepfake-fc59d.firebasestorage.app`
- ✅ **Firestore** 초기화 완료
  - `db = firestore.client()` 설정됨
  - 하지만 실제 사용은 제한적

#### Frontend
- ✅ **Firebase JS SDK** 설정 완료
  - 위치: `frontend/src/api/firebase.ts`
  - 프로젝트: `deepfake-fc59d`
- ✅ **Firebase Storage** 사용 중
  - 비디오 업로드 기능 (`uploadToFirebase.ts`)

### 🔄 PRD 요구사항 대비 부족한 것

## 1. Firebase Authentication (사용자 인증)

### 필요성
- PRD 요구사항: "회원가입 & 동의" 기능
- 현재 상태: 사용자 인증 없이 `user_id`만 사용 중
- 익명화 처리 및 개인정보 보호를 위해 필요

### 필요한 패키지

#### Frontend
```json
{
  "firebase": "^10.7.1"  // 이미 설치됨
}
```

#### Backend
```txt
firebase-admin>=6.4.0  // 이미 설치됨
```

### 구현 필요 사항

#### 1.1 Frontend - Firebase Auth 설정
```typescript
// frontend/src/api/firebase.ts 수정 필요
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

export const auth = getAuth(app);
export const firestore = getFirestore(app);
```

#### 1.2 인증 방법 옵션
- **익명 인증** (Anonymous Auth) - 추천
  - 사용자 정보 없이 익명 ID 생성
  - PRD의 "익명화 처리" 요구사항과 부합
- **이메일/비밀번호 인증**
- **소셜 로그인** (Google, Apple 등)

#### 1.3 구현 예시
```typescript
// frontend/src/services/authService.ts (새로 생성 필요)
import { signInAnonymously, onAuthStateChanged, User } from 'firebase/auth';
import { auth } from '../api/firebase';

export async function signInAnonymouslyUser(): Promise<User> {
  const userCredential = await signInAnonymously(auth);
  return userCredential.user;
}

export function onAuthStateChange(callback: (user: User | null) => void) {
  return onAuthStateChanged(auth, callback);
}
```

---

## 2. Firestore 데이터베이스 활용

### 필요성
- PRD 요구사항: "리워드 시스템", "사용자 메타데이터 관리"
- 현재 상태: Firestore 초기화만 되어 있고 실제 사용 안 함

### 필요한 Firestore 컬렉션 구조

#### 2.1 사용자 컬렉션 (`users`)
```typescript
// users/{userId}
{
  userId: string;              // Firebase Auth UID
  anonymousId: string;         // 익명화된 ID (AES256 암호화된 원본 ID)
  createdAt: Timestamp;
  lastActiveAt: Timestamp;
  totalPoints: number;         // 총 리워드 포인트
  totalContributions: number;  // 기여한 데이터 수
  badges: string[];            // 획득한 뱃지 목록
  consentAgreed: boolean;      // 개인정보 동의 여부
  consentDate: Timestamp;
}
```

#### 2.2 데이터 기여 컬렉션 (`contributions`)
```typescript
// contributions/{contributionId}
{
  contributionId: string;
  userId: string;              // 익명화된 ID
  videoUrl: string;            // Firebase Storage URL
  audioUrl?: string;
  metadata: {
    lighting: string;
    angle: string;
    device: string;
    timestamp: Timestamp;
    expression?: string;
    background?: string;
  };
  analysisResult: {
    isDeepfake: boolean;
    confidence: number;
    segments: any[];
  };
  rewardPoints: number;
  status: 'pending' | 'approved' | 'rejected';
  createdAt: Timestamp;
}
```

#### 2.3 리워드 이력 컬렉션 (`rewards`)
```typescript
// rewards/{rewardId}
{
  rewardId: string;
  userId: string;
  contributionId: string;
  points: number;
  badge?: string;
  reason: string;
  createdAt: Timestamp;
}
```

### 구현 필요 사항

#### Frontend - Firestore 사용
```typescript
// frontend/src/api/firebase.ts 수정
import { getFirestore, collection, doc, setDoc, getDoc, updateDoc } from 'firebase/firestore';

export const firestore = getFirestore(app);

// 사용 예시
export async function createUserProfile(userId: string, anonymousId: string) {
  const userRef = doc(firestore, 'users', userId);
  await setDoc(userRef, {
    userId,
    anonymousId,
    createdAt: new Date(),
    totalPoints: 0,
    totalContributions: 0,
    badges: [],
    consentAgreed: false,
  });
}
```

#### Backend - Firestore 사용
```python
# backend/app/services/user_service.py (새로 생성 필요)
from app.core.firebase import db

def create_user_profile(user_id: str, anonymous_id: str):
    user_ref = db.collection('users').document(user_id)
    user_ref.set({
        'userId': user_id,
        'anonymousId': anonymous_id,
        'createdAt': firestore.SERVER_TIMESTAMP,
        'totalPoints': 0,
        'totalContributions': 0,
        'badges': [],
        'consentAgreed': False,
    })

def add_reward_points(user_id: str, points: int, reason: str):
    user_ref = db.collection('users').document(user_id)
    user_ref.update({
        'totalPoints': firestore.Increment(points),
        'totalContributions': firestore.Increment(1),
    })
    
    # 리워드 이력 추가
    reward_ref = db.collection('rewards').document()
    reward_ref.set({
        'userId': user_id,
        'points': points,
        'reason': reason,
        'createdAt': firestore.SERVER_TIMESTAMP,
    })
```

---

## 3. Firebase Storage 보안 규칙 개선

### 현재 상태
- 개발용 규칙: 모든 읽기/쓰기 허용 (`allow read, write: if true;`)
- ⚠️ 프로덕션에서는 보안 위험

### 필요한 보안 규칙

#### 3.1 Storage 규칙 (프로덕션용)
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // 사용자 인증된 경우만 업로드 가능
    match /videos/{userId}/{videoId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
    
    // 공개 읽기, 인증된 사용자만 쓰기
    match /public/{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

#### 3.2 Firestore 규칙 (프로덕션용)
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 사용자는 자신의 프로필만 읽기/쓰기 가능
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // 기여 데이터는 본인 것만 읽기 가능, 쓰기는 인증된 사용자 모두 가능
    match /contributions/{contributionId} {
      allow read: if request.auth != null && 
                     resource.data.userId == request.auth.uid;
      allow create: if request.auth != null;
      allow update, delete: if false; // 관리자만 수정 가능
    }
    
    // 리워드 이력은 본인 것만 읽기 가능
    match /rewards/{rewardId} {
      allow read: if request.auth != null && 
                     resource.data.userId == request.auth.uid;
      allow write: if false; // 서버에서만 생성
    }
  }
}
```

---

## 4. 익명화 처리 (Anonymization)

### 필요성
- PRD 요구사항: "사용자 ID와 데이터 분리 저장, AES 암호화"
- 현재 상태: `user_id`를 그대로 사용 중

### 구현 방안

#### 4.1 익명 ID 생성
```typescript
// frontend/src/utils/anonymization.ts (새로 생성 필요)
import { v4 as uuidv4 } from 'uuid';
import CryptoJS from 'crypto-js';

const SECRET_KEY = process.env.ANONYMIZATION_SECRET_KEY || 'default-secret-key';

export function generateAnonymousId(userId: string): string {
  // AES256 암호화
  const encrypted = CryptoJS.AES.encrypt(userId, SECRET_KEY).toString();
  // Base64 인코딩하여 안전한 문자열로 변환
  return btoa(encrypted).replace(/[+/=]/g, '');
}

export function decryptAnonymousId(anonymousId: string): string {
  try {
    const decrypted = atob(anonymousId);
    const bytes = CryptoJS.AES.decrypt(decrypted, SECRET_KEY);
    return bytes.toString(CryptoJS.enc.Utf8);
  } catch (error) {
    throw new Error('Invalid anonymous ID');
  }
}
```

#### 4.2 필요한 패키지
```bash
# Frontend
npm install crypto-js uuid
npm install --save-dev @types/crypto-js @types/uuid

# Backend
pip install pycryptodome
```

---

## 5. 리워드 시스템 구현

### 필요성
- PRD 요구사항: "데이터 기여도에 따른 리워드 제공"
- 현재 상태: 미구현

### 구현 필요 사항

#### 5.1 리워드 계산 로직
```python
# backend/app/services/reward_service.py (새로 생성 필요)
def calculate_reward_points(metadata: dict, analysis_result: dict) -> int:
    """
    메타데이터와 분석 결과를 기반으로 리워드 포인트 계산
    """
    base_points = 10
    
    # 메타데이터 다양성 보너스
    bonus = 0
    if metadata.get('lighting') in ['low', 'natural']:
        bonus += 5  # 현실적인 조명 환경
    if metadata.get('angle') in ['left_side', 'right_side']:
        bonus += 5  # 다양한 각도
    if metadata.get('expression') != 'neutral':
        bonus += 3  # 다양한 표정
    
    # 분석 결과 품질 보너스
    if analysis_result.get('confidence', 0) > 0.9:
        bonus += 5  # 고품질 데이터
    
    return base_points + bonus
```

#### 5.2 뱃지 시스템
```python
BADGES = {
    'first_contribution': {'name': '첫 기여', 'required_contributions': 1},
    'bronze_contributor': {'name': '동메달 기여자', 'required_contributions': 10},
    'silver_contributor': {'name': '은메달 기여자', 'required_contributions': 50},
    'gold_contributor': {'name': '금메달 기여자', 'required_contributions': 100},
    'quality_master': {'name': '품질 마스터', 'required_avg_confidence': 0.95},
}

def check_and_award_badges(user_id: str):
    """사용자의 기여도를 확인하고 뱃지 부여"""
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        return
    
    user_data = user_doc.to_dict()
    total_contributions = user_data.get('totalContributions', 0)
    current_badges = user_data.get('badges', [])
    
    new_badges = []
    for badge_id, badge_info in BADGES.items():
        if badge_id not in current_badges:
            if 'required_contributions' in badge_info:
                if total_contributions >= badge_info['required_contributions']:
                    new_badges.append(badge_id)
    
    if new_badges:
        user_ref.update({
            'badges': firestore.ArrayUnion(new_badges)
        })
```

---

## 6. 필요한 패키지 설치

### Frontend
```bash
cd frontend
npm install crypto-js uuid
npm install --save-dev @types/crypto-js @types/uuid
```

### Backend
```bash
cd backend
pip install pycryptodome
```

---

## 7. Firebase Console 설정 필요 사항

### 7.1 Authentication 활성화
1. Firebase Console → Authentication → Sign-in method
2. **익명 인증 (Anonymous)** 활성화
3. (선택) 이메일/비밀번호 인증 활성화
4. (선택) Google 로그인 활성화

### 7.2 Firestore Database 생성
1. Firebase Console → Firestore Database
2. 데이터베이스 생성 (프로덕션 모드 또는 테스트 모드)
3. 보안 규칙 설정 (위의 3.2 참고)

### 7.3 Storage 보안 규칙 설정
1. Firebase Console → Storage → Rules
2. 보안 규칙 업데이트 (위의 3.1 참고)

### 7.4 환경 변수 설정
```bash
# .env 파일 생성 (프론트엔드)
ANONYMIZATION_SECRET_KEY=your-secret-key-here

# .env 파일 생성 (백엔드)
ANONYMIZATION_SECRET_KEY=your-secret-key-here
```

---

## 8. 구현 우선순위

### Phase 1: 기본 인증 시스템 (필수)
1. ✅ Firebase Authentication 설정 (익명 인증)
2. ✅ Firestore 사용자 프로필 생성
3. ✅ 익명화 ID 생성 및 저장

### Phase 2: 리워드 시스템 (핵심)
1. ✅ 리워드 포인트 계산 로직
2. ✅ Firestore 리워드 이력 저장
3. ✅ 뱃지 시스템 구현

### Phase 3: 보안 강화 (중요)
1. ✅ Storage 보안 규칙 설정
2. ✅ Firestore 보안 규칙 설정
3. ✅ AES256 암호화 구현

### Phase 4: 고급 기능 (선택)
1. ⏳ 사용자 대시보드 (리워드/뱃지 조회)
2. ⏳ 리더보드 기능
3. ⏳ 통계 및 분석

---

## 9. 체크리스트

### 설정
- [ ] Firebase Console에서 Authentication 활성화
- [ ] Firebase Console에서 Firestore Database 생성
- [ ] Storage 보안 규칙 설정
- [ ] Firestore 보안 규칙 설정
- [ ] 환경 변수 설정 (.env 파일)

### 패키지 설치
- [ ] Frontend: `crypto-js`, `uuid` 설치
- [ ] Backend: `pycryptodome` 설치

### 코드 구현
- [ ] Frontend: Firebase Auth 설정
- [ ] Frontend: Firestore 클라이언트 설정
- [ ] Frontend: 익명화 유틸리티 함수
- [ ] Frontend: 사용자 프로필 생성 로직
- [ ] Backend: 사용자 서비스 함수
- [ ] Backend: 리워드 서비스 함수
- [ ] Backend: 뱃지 시스템 함수

### 테스트
- [ ] 익명 인증 테스트
- [ ] 사용자 프로필 생성 테스트
- [ ] 리워드 포인트 계산 테스트
- [ ] 뱃지 부여 테스트
- [ ] 보안 규칙 테스트

---

## 📝 참고 자료

- [Firebase Authentication 문서](https://firebase.google.com/docs/auth)
- [Firestore 문서](https://firebase.google.com/docs/firestore)
- [Firebase Storage 보안 규칙](https://firebase.google.com/docs/storage/security)
- [Firestore 보안 규칙](https://firebase.google.com/docs/firestore/security/get-started)





