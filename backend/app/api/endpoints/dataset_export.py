from fastapi import APIRouter
from fastapi.responses import Response, JSONResponse
import os
import json
import csv
from io import StringIO
from typing import Dict, Any
from app.utils.helpers import get_analysis_result

router = APIRouter()

def create_dataset_jsonl(analysis_result: Dict[str, Any]) -> str:
    """
    분석 결과를 JSONL 형식으로 변환
    각 줄이 하나의 데이터 포인트 (프레임 또는 세그먼트)
    """
    lines = []
    timeline = analysis_result.get("timeline", [])
    
    for segment in timeline:
        result = segment.get("result", "UNKNOWN")
        confidence = segment.get("confidence", 0.0)
        start = segment.get("start", 0.0)
        end = segment.get("end", 0.0)
        
        # 프레임 정보 (raw_frame_results가 있는 경우)
        frames = segment.get("frames", [])
        if frames:
            for frame in frames:
                frame_data = {
                    "video_id": analysis_result.get("videoId", ""),
                    "time": frame.get("time", start),
                    "label": frame.get("ensemble_result", result),
                    "confidence": frame.get("confidence", confidence),
                    "fake_confidence": frame.get("fake_confidence", 0.0) if result == "FAKE" else 0.0,
                    "real_confidence": frame.get("real_confidence", 0.0) if result == "REAL" else 0.0,
                    "segment_id": segment.get("segment_id", 0),
                    "segment_start": start,
                    "segment_end": end,
                    "segment_label": result,
                }
                lines.append(json.dumps(frame_data, ensure_ascii=False))
        else:
            # 프레임 정보가 없으면 세그먼트 단위로
            segment_data = {
                "video_id": analysis_result.get("videoId", ""),
                "time_start": start,
                "time_end": end,
                "label": result,
                "confidence": confidence,
                "segment_id": segment.get("segment_id", 0),
                "frame_count": segment.get("frame_count", 0),
            }
            lines.append(json.dumps(segment_data, ensure_ascii=False))
    
    return "\n".join(lines)

def create_timeline_csv(analysis_result: Dict[str, Any]) -> str:
    """
    타임라인을 CSV 형식으로 변환
    """
    timeline = analysis_result.get("timeline", [])
    
    if not timeline:
        return "segment_id,start,end,result,confidence,frame_count\n"
    
    output = StringIO()
    writer = csv.writer(output)
    
    # 헤더
    writer.writerow(["segment_id", "start", "end", "result", "confidence", "frame_count", "duration"])
    
    # 데이터
    for segment in timeline:
        writer.writerow([
            segment.get("segment_id", ""),
            segment.get("start", 0.0),
            segment.get("end", 0.0),
            segment.get("result", ""),
            segment.get("confidence", 0.0),
            segment.get("frame_count", 0),
            segment.get("duration", 0.0),
        ])
    
    result = output.getvalue()
    output.close()
    # UTF-8 BOM 추가 (Excel 호환성)
    return '\ufeff' + result

def create_metadata_json(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    메타데이터 JSON 생성
    """
    video_info = analysis_result.get("video_info", {})
    summary = analysis_result.get("summary", {})
    video_analysis = analysis_result.get("video_analysis", {})
    
    metadata = {
        "video_id": analysis_result.get("videoId", ""),
        "video_name": analysis_result.get("video_name", ""),
        "user_id": analysis_result.get("user_id", ""),
        "analysis_timestamp": analysis_result.get("analysis_timestamp", ""),
        "video_info": {
            "duration": video_info.get("duration", 0.0),
            "fps": video_info.get("fps", 0.0),
            "frame_count": video_info.get("frame_count", 0),
            "frame_rate_used": video_info.get("frame_rate_used", 0.0),
        },
        "summary": {
            "overall_result": summary.get("overall_result", ""),
            "overall_confidence": summary.get("overall_confidence", 0.0),
            "total_segments": summary.get("total_segments", 0),
            "fake_segments": summary.get("fake_segments", 0),
            "real_segments": summary.get("real_segments", 0),
        },
        "video_analysis": {
            "overall_result": video_analysis.get("overall_result", ""),
            "overall_confidence": video_analysis.get("overall_confidence", 0.0),
            "total_frames": video_analysis.get("total_frames", 0),
            "fake_frames": video_analysis.get("fake_frames", 0),
            "real_frames": video_analysis.get("real_frames", 0),
        },
    }
    
    return metadata

@router.get("/{video_id}/jsonl", summary="Download Dataset JSONL")
async def download_dataset_jsonl(video_id: str):
    """
    데이터셋 JSONL 파일 다운로드
    """
    try:
        print(f"데이터셋 JSONL 다운로드 요청: {video_id}")
        
        analysis_result = get_analysis_result(video_id)
        if not analysis_result:
            return JSONResponse({"error": "분석 결과를 찾을 수 없습니다."}, status_code=404)
        
        dataset_jsonl = create_dataset_jsonl(analysis_result)
        
        return Response(
            content=dataset_jsonl,
            media_type="application/x-ndjson",
            headers={
                "Content-Disposition": f"attachment; filename=dataset_{video_id}.jsonl"
            }
        )
    except Exception as e:
        print(f"데이터셋 JSONL 생성 오류: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@router.get("/{video_id}/csv", summary="Download Timeline CSV")
async def download_timeline_csv(video_id: str):
    """
    타임라인 CSV 파일 다운로드
    """
    try:
        print(f"타임라인 CSV 다운로드 요청: {video_id}")
        
        analysis_result = get_analysis_result(video_id)
        if not analysis_result:
            return JSONResponse({"error": "분석 결과를 찾을 수 없습니다."}, status_code=404)
        
        timeline_csv = create_timeline_csv(analysis_result)
        
        return Response(
            content=timeline_csv,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=timeline_{video_id}.csv"
            }
        )
    except Exception as e:
        print(f"타임라인 CSV 생성 오류: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@router.get("/{video_id}/metadata", summary="Download Metadata JSON")
async def download_metadata_json(video_id: str):
    """
    메타데이터 JSON 파일 다운로드
    """
    try:
        print(f"메타데이터 JSON 다운로드 요청: {video_id}")
        
        analysis_result = get_analysis_result(video_id)
        if not analysis_result:
            return JSONResponse({"error": "분석 결과를 찾을 수 없습니다."}, status_code=404)
        
        metadata_json = create_metadata_json(analysis_result)
        metadata_str = json.dumps(metadata_json, ensure_ascii=False, indent=2)
        
        return Response(
            content=metadata_str,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=metadata_{video_id}.json"
            }
        )
    except Exception as e:
        print(f"메타데이터 JSON 생성 오류: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

