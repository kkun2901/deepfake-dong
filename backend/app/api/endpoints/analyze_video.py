from fastapi import APIRouter, UploadFile, File, Form
import os, uuid
from datetime import datetime
import cv2
import numpy as np
from app.services.model_mesonet import MesoNetBackend
from app.services.audio_processing import AudioProcessor
from app.utils.helpers import save_analysis_result, create_smart_timeline, create_analysis_summary, create_segment_analysis_details
from app.core.config import FRAME_SAMPLES, USE_FACE_CROP

router = APIRouter()

@router.post("/", summary="Analyze Video")
async def analyze_video(user_id: str = Form(...), video: UploadFile = File(...)):
    """
    영상 업로드 및 딥페이크 분석
    
    Args:
        user_id: 사용자 ID
        video: 분석할 영상 파일
    
    Returns:
        분석 결과 (완전한 분석 후 반환)
    """
    try:
        # 임시 저장
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        video_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{video.filename}")
        with open(video_path, "wb") as buffer:
            buffer.write(await video.read())
        
        # MesoNet 프레임 샘플링 (10개)
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps if fps > 0 else 0
        
        # 프레임 샘플링 (품질 향상을 위해 더 많은 프레임 추출)
        # 화면 녹화 영상의 경우 UI 오버레이로 인해 얼굴 감지가 어려울 수 있으므로 더 많은 프레임 샘플링
        frames_with_timestamps = []
        if frame_count > 0:
            # 짧은 영상의 경우 더 많은 프레임 샘플링
            # 영상 길이에 따라 샘플 수 조정
            if duration < 5.0:  # 5초 미만
                num_samples = min(FRAME_SAMPLES * 3, int(frame_count))  # 3배 (2배 -> 3배로 증가)
            elif duration < 10.0:  # 10초 미만
                num_samples = int(FRAME_SAMPLES * 2)  # 2배 (1.5배 -> 2배로 증가)
            else:
                num_samples = int(FRAME_SAMPLES * 1.5)  # 1.5배 (기본값도 증가)
            
            # 균등하게 샘플링 (더 정확한 분포)
            if num_samples == 1:
                indices = [0]
            else:
                indices = [int(i * (frame_count - 1) / max(1, num_samples - 1)) for i in range(num_samples)]
            
            for i in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    timestamp = i / fps if fps > 0 else 0
                    # 임시 파일로 저장 (JPEG 품질 95로 높임)
                    frame_path = os.path.join(temp_dir, f"frame_{i}_{uuid.uuid4().hex[:8]}.jpg")
                    cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    frames_with_timestamps.append((frame_path, timestamp))
                if len(frames_with_timestamps) >= num_samples:
                    break
        cap.release()
        
        if not frames_with_timestamps:
            return {
                "error": "프레임을 추출할 수 없습니다.",
                "video_name": video.filename,
                "videoId": str(uuid.uuid4()),
                "user_id": user_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "summary": {
                    "overall_result": "REAL",
                    "overall_confidence": 0.0,
                    "analysis_method": "frame_extraction_failed",
                    "message": "프레임 추출 실패"
                },
                "video_analysis": {
                    "overall_result": "REAL",
                    "overall_confidence": 0.0,
                    "total_frames": 0,
                    "fake_frames": 0,
                    "real_frames": 0
                },
                "audio_analysis": {"error": "프레임 추출 실패로 오디오 분석 생략"},
                "timeline": []
            }


        # MesoNet으로 프레임 분석 (PyTorch 버전)
        backend = MesoNetBackend()
        if not backend.load_model():
            raise Exception("MesoNet 모델 로딩 실패")
        
        results = []
        no_face_count = 0
        for frame_path, timestamp in frames_with_timestamps:
            try:
                result = backend.predict(frame_path, face_crop=USE_FACE_CROP)
                if "error" not in result:
                    # 얼굴이 감지되지 않은 프레임 체크
                    face_detected = result.get("face_detected", True)
                    if not face_detected:
                        no_face_count += 1
                    
                    results.append({
                        "ensemble_result": result["label"],
                        "confidence": result["score"],
                        "fake_confidence": result["fake_prob"],
                        "real_confidence": result["real_prob"],
                        "time": timestamp,
                        "face_detected": face_detected,
                        "meta": {"model": "MesoNet", "ensemble": False}
                    })
                else:
                    results.append({
                        "error": result["error"],
                        "ensemble_result": "REAL",
                        "confidence": 0.0,
                        "fake_confidence": 0.0,
                        "real_confidence": 1.0,
                        "face_detected": False,
                        "time": timestamp
                    })
                # 임시 프레임 파일 삭제
                try:
                    os.remove(frame_path)
                except:
                    pass
            except Exception as e:
                results.append({
                    "error": str(e),
                    "ensemble_result": "REAL",
                    "confidence": 0.0,
                    "fake_confidence": 0.0,
                    "real_confidence": 1.0,
                    "face_detected": False,
                    "time": timestamp
                })
        
        if no_face_count > 0:
            print(f"[알림] 얼굴 미감지 프레임: {no_face_count}개 (제외됨)")
        
        # MesoNet 결과 집계
        fake_confidences = []
        real_confidences = []
        confidence_weights = []
        
        # 프레임별 확률 출력
        print(f"\n[프레임별 분석 결과]")
        for i, r in enumerate(results):
            face_status = "✓" if r.get("face_detected", True) else "✗"
            result_label = r.get("ensemble_result", "N/A")
            fake_conf = r.get("fake_confidence", 0.0)
            time_sec = r.get("time", 0.0)
            print(f"  프레임 {i+1} ({time_sec:.1f}초) [{face_status}]: {result_label} ({fake_conf:.1%})")
        
        # 결과 수집 (얼굴이 감지된 프레임만 포함)
        valid_results = [r for r in results if r.get("face_detected", True) and "error" not in r]
        for r in valid_results:
            if "fake_confidence" in r:
                fake_confidences.append(r["fake_confidence"])
                if "confidence" in r:
                    confidence_weights.append(r["confidence"])
                else:
                    confidence_weights.append(1.0)
            if "real_confidence" in r:
                real_confidences.append(r["real_confidence"])
        
        
        # 얼굴이 감지된 프레임이 없으면 오류 반환
        if len(valid_results) == 0:
            return {
                "status": "error",
                "message": "영상에서 얼굴이 감지되지 않았습니다. 얼굴이 포함된 영상을 업로드해주세요.",
                "total_frames": len(results),
                "valid_frames": 0
            }
        
        # 딥페이크 프레임 비율 계산 (얼굴이 감지된 프레임 기준)
        fake_frames = len([r for r in valid_results if r.get("ensemble_result") == "FAKE"])
        total_frames = len(valid_results)  # 얼굴이 감지된 프레임만 카운트
        fake_ratio = fake_frames / total_frames if total_frames > 0 else 0
        
        # 개선된 계산 방식: FAKE 프레임 비율과 확률을 모두 고려
        # 딥페이크 영상에서 일부 프레임만 FAKE로 나올 수 있지만,
        # FAKE 프레임들의 확률이 높다면 전체 영상도 높은 확률로 반영되어야 함
        # 얼굴이 감지된 프레임만 사용
        fake_frame_confidences = [r["fake_confidence"] for r in valid_results 
                                 if r.get("ensemble_result") == "FAKE" and "fake_confidence" in r]
        
        if fake_confidences and len(fake_confidences) > 0:
            # 전체 단순 평균
            overall_avg = sum(fake_confidences) / len(fake_confidences)
            
            if fake_frame_confidences:
                # FAKE 프레임들의 평균
                avg_fake_conf = sum(fake_frame_confidences) / len(fake_frame_confidences)
                
                # 최종 계산: FAKE 프레임 비율을 더 강하게 반영
                if fake_ratio >= 0.5:
                    weight = 0.5 + fake_ratio * 0.5  # 0.5~1.0 범위
                    fake_conf = avg_fake_conf * weight + overall_avg * (1 - weight)
                else:
                    fake_conf = overall_avg
            else:
                fake_conf = overall_avg
        else:
            fake_conf = 0.0
        
        real_conf = 1.0 - fake_conf
        
        # 최종 판정: fake_confidence >= 0.5이면 FAKE
        if fake_conf >= 0.5:
            final_label = "FAKE"
        else:
            final_label = "REAL"
        
        print(f"\n[최종 결과]")
        print(f"  모델: MesoNet-4 (튜닝된 PyTorch 모델)")
        print(f"  판정: {final_label}")
        print(f"  FAKE 확률: {fake_conf:.1%}")
        print(f"  FAKE 프레임 비율: {fake_ratio:.0%} ({fake_frames}/{total_frames})")

        # 오디오 분석 (로그 없이)
        audio_processor = AudioProcessor()
        audio_analysis = audio_processor.analyze_audio(video_path)
        
        # 스마트 타임라인 생성
        timeline = create_smart_timeline(results, min_segment_duration=2.0)
        
        # 분석 요약 생성 (보정된 confidence 사용)
        video_analysis = {
            "overall_result": final_label,
            "overall_confidence": round(fake_conf, 4),  # 보정된 딥페이크 확률
            "total_frames": len(results),
            "fake_frames": len([r for r in results if r.get("ensemble_result") == "FAKE"]),
            "real_frames": len([r for r in results if r.get("ensemble_result") == "REAL"])
        }
        
        # 디버깅: 최종 결과 확인
        print(f"\n=== 최종 결과 ===")
        print(f"final_label: {final_label}")
        print(f"fake_conf: {fake_conf:.4f}")
        print(f"fake_ratio: {fake_ratio:.4f}")
        print(f"video_analysis.overall_confidence: {video_analysis['overall_confidence']:.4f}")
        
        summary = create_analysis_summary(video_analysis, audio_analysis, timeline)
        
        # 구간별 상세 분석
        detailed_segments = []
        for segment in timeline:
            segment_details = create_segment_analysis_details(segment, video_analysis, audio_analysis)
            detailed_segments.append({
                **segment,
                "details": segment_details
            })
        
        # 최종 결과 구성
        analysis_result = {
            "videoId": str(uuid.uuid4()),
            "video_name": video.filename,
            "user_id": user_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "video_info": {
                "duration": duration,
                "fps": fps,
                "frame_count": frame_count,
                "frame_rate_used": None,
                "frames_analyzed": len(results)
            },
            "summary": summary,
            "timeline": detailed_segments,
            "video_analysis": video_analysis,
            "audio_analysis": audio_analysis,
            "raw_frame_results": results  # 디버깅용
        }
        
        # 결과 저장
        save_analysis_result(analysis_result["videoId"], analysis_result)
        
        # 임시 파일 정리
        try:
            os.remove(video_path)
        except:
            pass
        
        return analysis_result
        
    except Exception as e:
        print(f"분석 중 오류 발생: {e}")
        return {"error": str(e), "video_name": video.filename}