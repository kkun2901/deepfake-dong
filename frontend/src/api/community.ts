import axios from 'axios';

const API_BASE_URL = __DEV__ 
  ? 'http://10.56.56.21:8000'
  : 'https://your-production-url.com';

export interface CommunityPost {
  id: string;
  title: string;
  description: string;
  file_type: 'image' | 'video' | 'dataset' | 'file' | 'text';
  file_url?: string;
  file_name?: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface UploadCommunityFileRequest {
  file: {
    uri: string;
    name: string;
    type: string;
  };
  file_type: 'image' | 'video' | 'dataset';
  user_id: string;
  title: string;
  description: string;
}

/**
 * 커뮤니티에 파일 업로드
 * React Native의 axios가 여러 텍스트 필드가 포함된 FormData를 처리하지 못하는 문제 해결
 * 해결책: analyzeVideo와 유사하게 최소한의 필드만 사용
 * - user_id (필수)
 * - metadata (JSON 문자열로 모든 메타데이터 포함)
 * - file (파일이 있는 경우만)
 */
export async function uploadCommunityFile(formData: FormData): Promise<CommunityPost> {
  try {
    console.log('[uploadCommunityFile] ====== 파일 업로드 요청 시작 ======');
    const apiUrl = `${API_BASE_URL}/community/upload`;
    console.log('[uploadCommunityFile] API URL:', apiUrl);
    console.log('[uploadCommunityFile] FormData 필드: user_id + file (analyzeVideo와 완전히 동일한 방식)');
    
    // analyzeVideo와 완전히 동일한 방식: fetch API를 먼저 사용
    try {
      // 먼저 fetch API로 시도 (React Native에서 더 안정적일 수 있음)
      console.log('[uploadCommunityFile] fetch API로 요청 전송 시도...');
      const fetchResponse = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
          // Content-Type은 설정하지 않음 - fetch가 자동으로 boundary 설정
        },
      });

      if (!fetchResponse.ok) {
        const errorText = await fetchResponse.text();
        console.error('[uploadCommunityFile] fetch 응답 실패:', fetchResponse.status, errorText);
        throw new Error(`서버 오류: ${fetchResponse.status} - ${errorText}`);
      }

      const responseData = await fetchResponse.json();
      console.log('[uploadCommunityFile] 응답 받음 (fetch):', fetchResponse.status);
      console.log('[uploadCommunityFile] 응답 데이터:', JSON.stringify(responseData).substring(0, 500));
      console.log('[uploadCommunityFile] 업로드 성공');
      return responseData;
    } catch (fetchError: any) {
      console.warn('[uploadCommunityFile] fetch API 실패, axios로 재시도:', fetchError?.message);
      
      // fetch 실패 시 axios로 재시도
      const response = await axios.post(
        apiUrl,
        formData,
        {
          headers: { 
            // Content-Type을 명시하지 않음 - axios가 자동으로 multipart/form-data + boundary 설정
            'Accept': 'application/json',
          },
          timeout: 300000, // 5분 타임아웃
          maxContentLength: Number.MAX_SAFE_INTEGER,
          maxBodyLength: Number.MAX_SAFE_INTEGER,
        }
      );
      
      console.log('[uploadCommunityFile] 응답 받음 (axios):', response.status);
      console.log('[uploadCommunityFile] 응답 데이터:', JSON.stringify(response.data).substring(0, 500));
      console.log('[uploadCommunityFile] 업로드 성공');
      return response.data;
    }
  } catch (error: any) {
    console.error('[uploadCommunityFile] ====== 파일 업로드 실패 ======');
    console.error('커뮤니티 파일 업로드 실패:', error);
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
      console.error('[uploadCommunityFile] ⚠️ 요청이 서버에 도달하지 않음');
      console.error('[uploadCommunityFile] 백엔드 서버 연결 확인 필요');
      console.error('[uploadCommunityFile] API URL:', `${API_BASE_URL}/community/upload`);
      throw new Error('백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.');
    }
    
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      throw new Error('파일 업로드 시간이 초과되었습니다. 파일 크기를 확인하세요.');
    }
    
    throw error;
  }
}

/**
 * 커뮤니티 게시글 목록 조회
 */
export async function getCommunityPosts(limit: number = 50, offset: number = 0): Promise<CommunityPost[]> {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/community/posts`,
      {
        params: {
          limit,
          offset,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('커뮤니티 게시글 조회 실패:', error);
    throw error;
  }
}

/**
 * 특정 게시글 조회
 */
export async function getCommunityPost(postId: string): Promise<CommunityPost> {
  try {
    const response = await axios.get(`${API_BASE_URL}/community/posts/${postId}`);
    return response.data;
  } catch (error) {
    console.error('게시글 조회 실패:', error);
    throw error;
  }
}

/**
 * 게시글 삭제
 */
export async function deleteCommunityPost(postId: string): Promise<void> {
  try {
    await axios.delete(`${API_BASE_URL}/community/posts/${postId}`);
  } catch (error) {
    console.error('게시글 삭제 실패:', error);
    throw error;
  }
}

