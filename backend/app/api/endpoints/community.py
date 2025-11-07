from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import uuid
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.core.firebase import db, bucket
import firebase_admin
from firebase_admin import firestore
from firebase_admin import storage

# ThreadPoolExecutor for Firestore operations
_executor = ThreadPoolExecutor(max_workers=5)

router = APIRouter()

# 커뮤니티 게시글 컬렉션 이름
COMMUNITY_COLLECTION = "community_posts"


@router.post("/upload", summary="커뮤니티 파일 업로드")
async def upload_community_file(
    file: Optional[UploadFile] = File(None),
    file_type: Optional[str] = Form("text"),
    user_id: str = Form(...),
    title: Optional[str] = Form(""),
    description: Optional[str] = Form(""),
    metadata: Optional[str] = Form(None),  # JSON 문자열로 메타데이터 전송 (선택적)
):
    """
    커뮤니티에 파일 업로드 (사진, 영상, 데이터셋, 텍스트만)
    한글 제목 및 본문 지원
    metadata 필드가 있으면 JSON으로 파싱하여 title, description, file_type 사용
    """
    try:
        # metadata가 있으면 JSON 파싱하여 사용 (React Native FormData 처리 문제 해결)
        if metadata:
            try:
                import json
                metadata_dict = json.loads(metadata)
                title = metadata_dict.get("title", title or "")
                description = metadata_dict.get("description", description or "")
                file_type = metadata_dict.get("file_type", file_type or "text")
                print(f"[community/upload] metadata에서 파싱: title={title}, description 길이={len(description)}, file_type={file_type}")
            except Exception as e:
                print(f"[community/upload] metadata 파싱 실패, 기본값 사용: {e}")
        
        # 파일명에서 메타데이터 파싱 (파일명 형식: metadata|originalname)
        if file and file.filename:
            try:
                import json
                import urllib.parse
                filename_parts = file.filename.split('|', 1)
                if len(filename_parts) == 2:
                    # 파일명에 메타데이터가 인코딩되어 있음
                    encoded_metadata = filename_parts[0]
                    original_filename = filename_parts[1]
                    decoded_metadata = urllib.parse.unquote(encoded_metadata)
                    metadata_dict = json.loads(decoded_metadata)
                    title = metadata_dict.get("title", title or "")
                    description = metadata_dict.get("description", description or "")
                    file_type = metadata_dict.get("file_type", file_type or "text")
                    # 원본 파일명 복원
                    file.filename = original_filename
                    print(f"[community/upload] 파일명에서 메타데이터 파싱: title={title}, description 길이={len(description)}, file_type={file_type}, original_filename={original_filename}")
            except Exception as e:
                print(f"[community/upload] 파일명에서 메타데이터 파싱 실패 (정상일 수 있음): {e}")
        
        print(f"[community/upload] ====== 파일 업로드 요청 받음 ======")
        print(f"[community/upload] 제목: {title}, 본문 길이: {len(description)}")
        print(f"[community/upload] user_id: {user_id}, file_type: {file_type}")
        print(f"[community/upload] file is None: {file is None}")
        # 파일 타입 검증 (모든 파일 타입 허용)
        valid_file_types = ["image", "video", "dataset", "file", "text"]
        if file_type not in valid_file_types:
            file_type = "file"  # 기본값으로 설정
        
        file_url = None
        file_name = None
        file_content = None
        file_size = 0
        
        # 파일이 있는 경우에만 업로드
        if file is not None:
            try:
                # 파일 정보 확인
                print(f"파일 업로드 시작 - filename: {file.filename}, content_type: {file.content_type}")
                
                if hasattr(file, 'filename') and file.filename:
                    # 파일 읽기 (청크 단위로 읽어서 메모리 효율성 향상)
                    file_content = await file.read()
                    file_size = len(file_content) if file_content else 0
                    
                    print(f"파일 크기: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)")
                    
                    # 파일 크기 제한 체크 (500MB)
                    max_file_size = 500 * 1024 * 1024  # 500MB
                    if file_size > max_file_size:
                        raise HTTPException(status_code=413, detail=f"파일 크기가 너무 큽니다. 최대 {max_file_size / 1024 / 1024}MB까지 허용됩니다.")
                    
                    # 파일명 생성 (UUID 사용)
                    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
                    unique_filename = f"{uuid.uuid4()}{file_extension}"
                    file_name = file.filename
                    
                    # Firebase Storage 경로 설정
                    storage_path = f"community/{file_type}/{unique_filename}"
                    
                    print(f"Firebase Storage 업로드 시작: {storage_path}")
                    
                    # Firebase Storage에 업로드
                    blob = bucket.blob(storage_path)
                    blob.upload_from_string(file_content, content_type=file.content_type or 'application/octet-stream')
                    blob.make_public()
                    file_url = blob.public_url
                    
                    print(f"Firebase Storage 업로드 완료: {file_url}")
            except HTTPException:
                raise
            except Exception as file_error:
                print(f"파일 업로드 오류: {file_error}")
                import traceback
                traceback.print_exc()
                # 파일 업로드 실패해도 텍스트 글은 작성 가능
                file_url = None
                file_name = None
        
        # 게시글 데이터 생성
        post_id = str(uuid.uuid4())
        post_data = {
            "id": post_id,
            "title": title,
            "description": description,
            "file_type": file_type,
            "file_url": file_url,
            "file_name": file_name,
            "file_size": file_size,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        # Firestore에 저장 (타임아웃 처리)
        try:
            def save_to_firestore():
                db.collection(COMMUNITY_COLLECTION).document(post_id).set(post_data)
            
            # 10초 타임아웃으로 실행
            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(_executor, save_to_firestore),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            print(f"Firestore 저장 타임아웃 (10초 초과)")
            raise HTTPException(status_code=503, detail="데이터베이스 연결 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.")
        except Exception as firestore_error:
            print(f"Firestore 저장 오류: {firestore_error}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"데이터 저장 실패: {str(firestore_error)}")
        
        return post_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"커뮤니티 파일 업로드 오류: {e}")
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")


@router.get("/posts", summary="커뮤니티 게시글 목록 조회")
async def get_community_posts(
    limit: int = Query(50, ge=1, le=100, description="조회할 게시글 수"),
    offset: int = Query(0, ge=0, description="건너뛸 게시글 수"),
    file_type: Optional[str] = Query(None, description="파일 타입 필터 (image, video, dataset)"),
):
    """
    커뮤니티 게시글 목록 조회
    """
    try:
        # Firestore 쿼리 생성 (타임아웃 처리)
        query = db.collection(COMMUNITY_COLLECTION)
        
        # 파일 타입 필터 적용 (모든 파일 타입 지원)
        if file_type:
            query = query.where("file_type", "==", file_type)
        
        # 최신순 정렬 및 페이지네이션 (타임아웃 처리)
        posts = []
        try:
            # 타임아웃 설정 (10초)
            def fetch_posts():
                docs = query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit + offset).stream()
                result = []
                for i, doc in enumerate(docs):
                    if i >= offset:
                        post_data = doc.to_dict()
                        result.append(post_data)
                return result
            
            # 10초 타임아웃으로 실행
            loop = asyncio.get_event_loop()
            posts = await asyncio.wait_for(
                loop.run_in_executor(_executor, fetch_posts),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            print(f"Firestore 쿼리 타임아웃 (10초 초과)")
            # 타임아웃 시 빈 리스트 반환
            return []
        except Exception as query_error:
            print(f"Firestore 쿼리 오류: {query_error}")
            import traceback
            traceback.print_exc()
            # Firestore 연결 실패 시 빈 리스트 반환
            return []
        
        return posts
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"커뮤니티 게시글 조회 오류: {e}")
        import traceback
        traceback.print_exc()
        # 오류 발생 시 빈 리스트 반환 (서버 오류로 앱이 멈추지 않도록)
        return []


@router.get("/posts/{post_id}", summary="특정 게시글 조회")
async def get_community_post(post_id: str):
    """
    특정 게시글 조회
    """
    try:
        # Firestore에서 게시글 조회 (타임아웃 처리)
        try:
            def fetch_post():
                return db.collection(COMMUNITY_COLLECTION).document(post_id).get()
            
            # 10초 타임아웃으로 실행
            loop = asyncio.get_event_loop()
            doc = await asyncio.wait_for(
                loop.run_in_executor(_executor, fetch_post),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            print(f"Firestore 조회 타임아웃 (10초 초과)")
            raise HTTPException(status_code=503, detail="데이터베이스 연결 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.")
        except Exception as query_error:
            print(f"Firestore 조회 오류: {query_error}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=503, detail=f"데이터베이스 연결 실패: {str(query_error)}")
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        
        return doc.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"게시글 조회 오류: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"게시글 조회 실패: {str(e)}")


@router.delete("/posts/{post_id}", summary="게시글 삭제")
async def delete_community_post(post_id: str, user_id: str = Query(..., description="사용자 ID")):
    """
    게시글 삭제 (작성자만 삭제 가능)
    """
    try:
        doc_ref = db.collection(COMMUNITY_COLLECTION).document(post_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        
        post_data = doc.to_dict()
        
        # 작성자 확인
        if post_data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="게시글을 삭제할 권한이 없습니다.")
        
        # Firebase Storage에서 파일 삭제
        file_url = post_data.get("file_url")
        if file_url:
            try:
                # URL에서 파일 경로 추출
                # 예: https://storage.googleapis.com/bucket/path/to/file
                # 또는 https://firebasestorage.googleapis.com/v0/b/bucket/o/path%2Fto%2Ffile
                if "firebasestorage.googleapis.com" in file_url:
                    # Firebase Storage URL 파싱
                    import urllib.parse
                    path_part = file_url.split("/o/")[-1].split("?")[0]
                    file_path = urllib.parse.unquote(path_part)
                    blob = bucket.blob(file_path)
                    blob.delete()
            except Exception as e:
                print(f"파일 삭제 오류 (무시): {e}")
        
        # Firestore에서 게시글 삭제
        doc_ref.delete()
        
        return {"message": "게시글이 삭제되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"게시글 삭제 오류: {e}")
        raise HTTPException(status_code=500, detail=f"게시글 삭제 실패: {str(e)}")

