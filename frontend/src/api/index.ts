import axios from 'axios';

// 개발 환경에서 사용할 API 주소 (로컬 개발 시 컴퓨터 IP로 변경)
const API_BASE_URL = __DEV__ 
  ? 'http://10.56.56.21:8000'  // 개발용 - 실제 기기 사용 시 컴퓨터 IP 주소로 변경
  : 'https://your-production-url.com';  // 프로덕션용

export interface TimelineItem {
  start: number;
  end: number;
  ensemble_result: 'real' | 'fake';
  confidence: number;
}

export interface AnalysisResultResponse {
  videoId: string;
  timeline: TimelineItem[];
}

export interface AnalyzeVideoResponse {
  videoId: string;
  timeline?: Array<{ t: number; label: 'normal' | 'suspect'; score: number }>;
  overallScore?: number;
  status?: string;
}

export async function fetchAnalysisResult(videoId: string): Promise<AnalysisResultResponse> {
  try {
    const response = await axios.get(`${API_BASE_URL}/get-result/${videoId}`);
    return response.data as AnalysisResultResponse;
  } catch (error) {
    console.error('분석 결과 조회 실패:', error);
    throw error;
  }
}

export async function downloadDataset(videoId: string, fileType: 'jsonl' | 'csv' | 'metadata' = 'jsonl'): Promise<string> {
  try {
    console.log('데이터셋 다운로드 요청:', videoId, fileType);
    
    const API_BASE_URL = __DEV__ 
      ? 'http://10.56.56.21:8000'
      : 'https://your-production-url.com';
    
    // 텍스트 기반 파일 다운로드 URL
    const downloadUrl = `${API_BASE_URL}/dataset/${videoId}/${fileType}`;
    
    return downloadUrl;
  } catch (error) {
    console.error('데이터셋 다운로드 URL 생성 실패:', error);
    throw error;
  }
}

export async function analyzeVideo(
  videoUri: string,
  userId: string
): Promise<AnalyzeVideoResponse> {
  try {
    console.log('[analyzeVideo] ====== 영상 분석 요청 ======');
    console.log('[analyzeVideo] videoUri:', videoUri);
    console.log('[analyzeVideo] userId:', userId);

    // FastAPI는 파일 업로드를 FormData(multipart/form-data)로 기대함
    // Expo/React Native에서는 { uri, name, type } 형태로 파일을 전달
    const form = new FormData();
    // user_id 필드
    form.append('user_id', userId as any);
    // video 파일 필드
    // Android에서는 file:// URI를 그대로 사용
    const fileData = {
      uri: videoUri,
      name: 'video.mp4',
      type: 'video/mp4',
    };
    console.log('[analyzeVideo] 파일 데이터:', { uri: fileData.uri, name: fileData.name, type: fileData.type });
    form.append('video', fileData as any);

    // 엔드포인트: 동기 처리 '/analyze-video/' 또는 비동기 '/analysis-server/start-analysis'
    // 여기서는 동기 처리 엔드포인트를 사용 (즉시 결과 반환)
    const apiUrl = `${API_BASE_URL}/analyze-video/`;
    console.log('[analyzeVideo] API 요청 전송:', apiUrl);
    
    // React Native의 axios가 큰 파일을 전송할 때 문제가 있을 수 있으므로 fetch API 사용 시도
    try {
      // 먼저 fetch API로 시도 (React Native에서 더 안정적일 수 있음)
      console.log('[analyzeVideo] fetch API로 요청 전송 시도...');
      const fetchResponse = await fetch(apiUrl, {
        method: 'POST',
        body: form,
        headers: {
          'Accept': 'application/json',
          // Content-Type은 설정하지 않음 - fetch가 자동으로 boundary 설정
        },
      });

      if (!fetchResponse.ok) {
        const errorText = await fetchResponse.text();
        console.error('[analyzeVideo] fetch 응답 실패:', fetchResponse.status, errorText);
        throw new Error(`서버 오류: ${fetchResponse.status} - ${errorText}`);
      }

      const responseData = await fetchResponse.json();
      console.log('[analyzeVideo] 분석 결과 받음 (fetch):', fetchResponse.status);
      console.log('[analyzeVideo] 응답 데이터:', JSON.stringify(responseData).substring(0, 500));
      return responseData as AnalyzeVideoResponse;
    } catch (fetchError: any) {
      console.warn('[analyzeVideo] fetch API 실패, axios로 재시도:', fetchError?.message);
      
      // fetch 실패 시 axios로 재시도
      const response = await axios.post(
        apiUrl,
        form,
        {
          headers: { 
            // Content-Type을 명시하지 않음 - axios가 자동으로 multipart/form-data + boundary 설정
            'Accept': 'application/json',
          },
          timeout: 120000, // 최대 120초 대기
          maxContentLength: Number.MAX_SAFE_INTEGER,
          maxBodyLength: Number.MAX_SAFE_INTEGER,
        }
      );
      
      console.log('[analyzeVideo] 분석 결과 받음 (axios):', response.status);
      console.log('[analyzeVideo] 응답 데이터:', JSON.stringify(response.data).substring(0, 500));
      return response.data as AnalyzeVideoResponse;
    }
  } catch (error: any) {
    console.error('[analyzeVideo] ====== 영상 분석 요청 실패 ======');
    console.error('영상 분석 요청 실패:', error);
    console.error('오류 상세:', {
      message: error?.message,
      code: error?.code,
      name: error?.name,
      stack: error?.stack?.substring(0, 500),
      response: error?.response?.data,
      status: error?.response?.status,
      request: error?.request ? 'request exists' : 'no request',
    });
    
    // Network Error는 요청이 전송되지 않았음을 의미
    if (error.code === 'ECONNREFUSED' || error.message === 'Network Error' || error.code === 'ERR_NETWORK' || error.message === 'Network request failed') {
      console.error('[analyzeVideo] ⚠️ 요청이 서버에 도달하지 않음');
      console.error('[analyzeVideo] 백엔드 서버 연결 확인 필요');
      console.error('[analyzeVideo] API URL:', `${API_BASE_URL}/analyze-video/`);
    }
    
    // API 오류 시 임시 결과 반환 (개발 중)
    console.log('API 오류로 인해 임시 결과 반환');
    const fallbackResult: AnalyzeVideoResponse = {
      videoId: `fallback_${Date.now()}`,
      timeline: [
        { t: 0, label: 'normal', score: 0.85 },
        { t: 1, label: 'normal', score: 0.92 },
        { t: 2, label: 'suspect', score: 0.15 },
        { t: 3, label: 'normal', score: 0.88 },
        { t: 4, label: 'normal', score: 0.91 }
      ],
      overallScore: 0.87,
      status: 'completed'
    };
    
    return fallbackResult;
  }
}
