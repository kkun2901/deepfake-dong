import React, { useEffect } from 'react';
import { NavigationContainer, useNavigationContainerRef } from '@react-navigation/native';
import { Platform, DeviceEventEmitter } from 'react-native';
import AppNavigator from './src/navigation/AppNavigator';
import { FloatingWidgetEvents } from './src/utils';

export default function App() {
  const navigationRef = useNavigationContainerRef();

  // 전역 녹화 완료 이벤트 리스너 (모든 화면에서 작동)
  useEffect(() => {
    if (!FloatingWidgetEvents || Platform.OS !== 'android') {
      console.log('[App] FloatingWidgetEvents가 없거나 Android가 아님');
      return;
    }

    console.log('[App] 녹화 완료 이벤트 리스너 등록 시작');
    
    const recordingListener = FloatingWidgetEvents.addListener(
      'onRecordingComplete',
      (event: { filePath: string; type: string; autoStop?: boolean }) => {
        console.log('[App] ====== 녹화 완료 이벤트 수신 ======');
        console.log('[App] 파일 경로:', event.filePath);
        console.log('[App] autoStop:', event.autoStop);
        console.log('[App] 이벤트 전체:', JSON.stringify(event));
      }
    );

    return () => {
      recordingListener.remove();
    };
  }, []);

  // 네이티브에서 화면 이동 요청 처리
  useEffect(() => {
    if (Platform.OS !== 'android') return;

    const navigateToUploadListener = DeviceEventEmitter.addListener(
      'navigateToUpload',
      (data: { action: string }) => {
        console.log('[App] navigateToUpload 이벤트 수신:', data);
        if (navigationRef.isReady()) {
          navigationRef.navigate('Upload' as never);
        } else {
          setTimeout(() => {
            if (navigationRef.isReady()) {
              navigationRef.navigate('Upload' as never);
            }
          }, 500);
        }
      }
    );

    const navigateToResultListener = DeviceEventEmitter.addListener(
      'navigateToResult',
      (data: { action: string; videoId?: string }) => {
        console.log('[App] navigateToResult 이벤트 수신:', data);
        if (navigationRef.isReady()) {
          navigationRef.navigate('Result' as never, {
            videoId: data.videoId,
          } as never);
        } else {
          setTimeout(() => {
            if (navigationRef.isReady()) {
              navigationRef.navigate('Result' as never, {
                videoId: data.videoId,
              } as never);
            }
          }, 500);
        }
      }
    );

    return () => {
      navigateToUploadListener.remove();
      navigateToResultListener.remove();
    };
  }, []);

  return (
    <NavigationContainer ref={navigationRef}>
      <AppNavigator />
    </NavigationContainer>
  );
}

