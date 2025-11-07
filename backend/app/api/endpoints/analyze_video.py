from fastapi import APIRouter, UploadFile, File, Form
import os, uuid
from datetime import datetime
from app.services.mesonet_backend import sample_frames, predict_frames, predict_image
from app.services.audio_processing import AudioProcessor
from app.utils.helpers import save_analysis_result, create_smart_timeline, create_analysis_summary, create_segment_analysis_details

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
        print(f"=== 영상 분석 시작: {video.filename} ===")
        
        # 임시 저장
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        video_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{video.filename}")
        with open(video_path, "wb") as buffer:
            buffer.write(await video.read())
        
        # MesoNet 프레임 샘플링 (10개)
        from app.core.config import FRAME_SAMPLES
        import cv2
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps if fps > 0 else 0
        cap.release()
        
        print(f"영상 길이: {duration:.1f}초, 프레임 샘플링: {FRAME_SAMPLES}개")
        
        # 프레임 샘플링 (MesoNet 백엔드 함수 사용)
        frames_with_timestamps = sample_frames(video_path, num_samples=FRAME_SAMPLES)
        
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
        
        print(f"프레임 샘플링 완료: {len(frames_with_timestamps)}개")

        # MesoNet으로 프레임 분석
        print(f"총 {len(frames_with_timestamps)}개 프레임을 MesoNet으로 분석합니다...")
        results = predict_frames(frames_with_timestamps)
        print(f"프레임 분석 완료: {len(results)}개 결과")

        # MesoNet 결과 집계
        fake_confidences = []
        real_confidences = []
        confidence_weights = []
        
        # 디버깅: 각 프레임의 결과 확인
        print(f"\n=== 프레임별 분석 결과 (MesoNet 단독) ===")
        for i, r in enumerate(results[:5]):  # 처음 5개만 출력
            print(f"프레임 {i+1}:")
            print(f"  - ensemble_result: {r.get('ensemble_result', 'N/A')}")
            print(f"  - fake_confidence: {r.get('fake_confidence', 'N/A')}")
            print(f"  - real_confidence: {r.get('real_confidence', 'N/A')}")
            print(f"  - confidence: {r.get('confidence', 'N/A')}")
        
        # 결과 수집
        for r in results:
            if "error" in r:
                print(f"프레임 분석 오류: {r['error']}")
                continue
            if "fake_confidence" in r:
                fake_confidences.append(r["fake_confidence"])
                if "confidence" in r:
                    confidence_weights.append(r["confidence"])
                else:
                    confidence_weights.append(1.0)
            if "real_confidence" in r:
                real_confidences.append(r["real_confidence"])
        
        print(f"\n=== 전체 통계 ===")
        print(f"총 프레임 수: {len(results)}")
        print(f"분석 성공 프레임 수: {len(fake_confidences)}")
        
        # 앙상블 결과 계산 (가중 평균)
        if fake_confidences and len(fake_confidences) > 0:
            if confidence_weights and len(confidence_weights) == len(fake_confidences):
                total_weight = sum(confidence_weights)
                if total_weight > 0:
                    fake_conf = sum(f * w for f, w in zip(fake_confidences, confidence_weights)) / total_weight
                else:
                    fake_conf = sum(fake_confidences) / len(fake_confidences)
            else:
                fake_conf = sum(fake_confidences) / len(fake_confidences)
            print(f"계산된 fake_conf (가중 평균): {fake_conf:.4f}")
        else:
            fake_conf = 0.0
            print(f"경고: 분석 결과가 없습니다! fake_conf = 0으로 설정")
        
        real_conf = 1.0 - fake_conf
        
        # 딥페이크 프레임 비율 계산
        fake_frames = len([r for r in results if r.get("ensemble_result") == "FAKE"])
        total_frames = len(results)
        fake_ratio = fake_frames / total_frames if total_frames > 0 else 0
        
        # 최종 판정: fake_confidence >= 0.5이면 FAKE
        if fake_conf >= 0.5:
            final_label = "FAKE"
        else:
            final_label = "REAL"
        
        print(f"최종 결과: {final_label} (FAKE confidence: {fake_conf:.4f}, FAKE 프레임 비율: {fake_ratio:.1%})")

        # 오디오 분석
        print("오디오 분석 시작...")
        audio_processor = AudioProcessor()
        audio_analysis = audio_processor.analyze_audio(video_path)
        print(f"오디오 분석 완료: {audio_analysis}")
        
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
            print("임시 영상 파일 정리 완료")
        except Exception as e:
            print(f"임시 파일 정리 실패: {e}")
        
        print(f"=== 분석 완료: {analysis_result['videoId']} ===")
        
        return analysis_result
        
    except Exception as e:
        print(f"분석 중 오류 발생: {e}")
        return {"error": str(e), "video_name": video.filename}