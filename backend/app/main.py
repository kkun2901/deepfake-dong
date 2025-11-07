from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import analyze_video, submit_report, report_download, model_guide, analysis_server, community

# analyze_video_optimized는 이전 ensemble 모델용이므로 현재는 비활성화 (MesoNet 단독 모델 사용)
try:
    from app.api.endpoints import analyze_video_optimized
    OPTIMIZED_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ analyze_video_optimized를 로드할 수 없습니다 (PyTorch/torchvision 필요): {e}")
    print("   현재는 MesoNet 단독 모델만 사용합니다.")
    OPTIMIZED_AVAILABLE = False

app = FastAPI(
    title="Deepfake Detection API",
    version="1.0.0",
    description="Video & Audio-based Deepfake Detection with Report Generation",
)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서 접근 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 등록
app.include_router(analyze_video.router, prefix="/analyze-video", tags=["Analysis"])
app.include_router(analysis_server.router, prefix="/analysis-server", tags=["Analysis Server"])

# analyze_video_optimized는 조건부 등록 (PyTorch/torchvision이 설치된 경우만)
if OPTIMIZED_AVAILABLE:
    app.include_router(analyze_video_optimized.router, prefix="/analyze-video-optimized", tags=["Analysis (Optimized)"])

app.include_router(submit_report.router, prefix="/submit-report", tags=["Reports"])
app.include_router(report_download.router, prefix="/download-report", tags=["Reports"])
app.include_router(model_guide.router, prefix="/model-guide", tags=["Model Development"])
app.include_router(community.router, prefix="/community", tags=["Community"])

@app.get("/")
def root():
    return {"message": "Deepfake Detection API Running"}

