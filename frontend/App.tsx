import React, { useEffect, useRef } from 'react';
import { NavigationContainer, NavigationContainerRef } from '@react-navigation/native';
import { DeviceEventEmitter, Platform } from 'react-native';
import AppNavigator, { RootStackParamList } from './src/navigation/AppNavigator';

export default function App() {
  const navigationRef = useRef<NavigationContainerRef<RootStackParamList>>(null);
  const pendingPathRef = useRef<string | null>(null);

  useEffect(() => {
    if (Platform.OS !== 'android') {
      return;
    }

    const subscription = DeviceEventEmitter.addListener(
      'onRecordingComplete',
      (event: { filePath?: string; type?: string; autoStop?: boolean }) => {
        const rawPath = event?.filePath;
        console.log('[App] ====== 녹화 완료 이벤트 수신 ======');
        console.log('[App] event:', event);

        if (!rawPath) {
          console.warn('[App] filePath 가 비어있어서 무시합니다.');
          return;
        }

        // Android native 모듈에서 넘어온 경로를 file:// URI 형태로 통일
        const videoUri = rawPath.startsWith('file://')
          ? rawPath
          : rawPath.startsWith('/')
          ? `file://${rawPath}`
          : `file:///${rawPath}`;

        const navigateToRecord = () => {
          if (!navigationRef.current) {
            pendingPathRef.current = videoUri;
            return;
          }

          navigationRef.current.navigate('Record', {
            recordedVideoPath: videoUri,
            showAnalysisProgress: true,
          });
        };

        if (navigationRef.current && navigationRef.current.isReady()) {
          navigateToRecord();
        } else {
          console.log('[App] Navigation 준비 전 - 경로 저장');
          pendingPathRef.current = videoUri;
        }
      }
    );

    return () => {
      subscription.remove();
    };
  }, []);

  const handleNavReady = () => {
    if (pendingPathRef.current && navigationRef.current) {
      navigationRef.current.navigate('Record', {
        recordedVideoPath: pendingPathRef.current,
        showAnalysisProgress: true,
      });
      pendingPathRef.current = null;
    }
  };

  return (
    <NavigationContainer ref={navigationRef} onReady={handleNavReady}>
      <AppNavigator />
    </NavigationContainer>
  );
}

