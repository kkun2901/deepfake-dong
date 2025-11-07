import axios from 'axios';

const API_BASE_URL = __DEV__ 
  ? 'http://10.56.56.21:8000'
  : 'https://your-production-url.com';

/**
 * 백엔드 서버 연결 상태 확인
 */
export async function checkServerConnection(): Promise<boolean> {
  try {
    console.log('[checkServer] 서버 연결 시도:', API_BASE_URL);
    const response = await axios.get(`${API_BASE_URL}/`, {
      timeout: 5000,
    });
    console.log('[checkServer] 서버 연결 성공:', response.status);
    return response.status === 200;
  } catch (error: any) {
    console.error('[checkServer] 서버 연결 확인 실패:', {
      message: error?.message,
      code: error?.code,
      response: error?.response?.status,
      url: API_BASE_URL,
      isNetworkError: error?.message === 'Network Error',
    });
    
    if (error?.message === 'Network Error') {
      console.error('[checkServer] 네트워크 오류: 백엔드 서버가 실행 중인지 확인하세요.');
      console.error('[checkServer] 백엔드 서버 실행 방법: cd backend && .\\run_server.bat');
    }
    
    return false;
  }
}


