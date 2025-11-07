import React, { useEffect, useRef } from 'react';
import { NavigationContainer, useNavigationContainerRef } from '@react-navigation/native';
import { Alert, AppState, Platform } from 'react-native';
import AppNavigator from './src/navigation/AppNavigator';
import { FloatingWidgetEvents } from './src/utils';

export default function App() {
  const navigationRef = useNavigationContainerRef();
  const pendingEventRef = useRef<{ filePath: string; autoStop: boolean } | null>(null);

  // 전역 녹화 완료 이벤트 리스너 (모든 화면에서 작동)
  useEffect(() => {
    if (!FloatingWidgetEvents || Platform.OS !== 'android') {
      console.log('[App] FloatingWidgetEvents가 없거나 Android가 아님');
      return;
    }

    console.log('[App] 녹화 완료 이벤트 리스너 등록 시작');
    
    const showAnalysisAlert = (event: { filePath: string; type: string; autoStop?: boolean }) => {
      const message = event.autoStop
        ? '영상 길이가 15초에 도달하여 자동으로 종료되었습니다.\n분석하시겠습니까?'
        : '녹화가 완료되었습니다. 분석하시겠습니까?';
      
      Alert.alert(
        event.autoStop ? '녹화 자동 종료' : '녹화 완료',
        message,
        [
          {
            text: '취소',
            style: 'cancel',
            onPress: () => {
              // 취소 시 pendingEventRef 초기화하여 재표시 방지
              pendingEventRef.current = null;
              console.log('[App] 사용자가 분석 취소');
            },
          },
          {
            text: '분석하기',
            onPress: () => {
              const navigateToRecord = () => {
                if (navigationRef.isReady()) {
                  navigationRef.navigate('Record' as never, {
                    recordedVideoPath: event.filePath,
                    showAnalysisProgress: true,
                  } as never);
                  // 네비게이션 후 pendingEventRef 초기화
                  pendingEventRef.current = null;
                } else {
                  setTimeout(navigateToRecord, 200);
                }
              };
              navigateToRecord();
            },
          },
        ],
        { cancelable: false }
      );
    };
    
    const recordingListener = FloatingWidgetEvents.addListener(
      'onRecordingComplete',
      (event: { filePath: string; type: string; autoStop?: boolean }) => {
        console.log('[App] ====== 녹화 완료 이벤트 수신 ======');
        console.log('[App] 파일 경로:', event.filePath);
        console.log('[App] autoStop:', event.autoStop);
        console.log('[App] 이벤트 전체:', JSON.stringify(event));
        console.log('[App] 현재 AppState:', AppState.currentState);
        
        // 이벤트 정보를 임시 저장
        pendingEventRef.current = {
          filePath: event.filePath,
          autoStop: event.autoStop || false,
        };
        
        // 항상 이벤트를 저장하고, AppState 변경 감지로 처리
        console.log('[App] 이벤트 저장 완료, AppState 감지 대기');
      }
    );

    // AppState 변경 감지 - 앱이 활성화될 때 대기 중인 이벤트 처리
    const appStateSubscription = AppState.addEventListener('change', (nextAppState) => {
      console.log('[App] AppState 변경:', nextAppState, 'pendingEvent:', !!pendingEventRef.current);
      if (nextAppState === 'active' && pendingEventRef.current) {
        console.log('[App] 앱이 활성화됨, 대기 중인 이벤트 처리');
        // React Native와 Navigation이 완전히 준비될 때까지 대기
        setTimeout(() => {
          if (pendingEventRef.current && navigationRef.isReady()) {
            showAnalysisAlert({
              filePath: pendingEventRef.current.filePath,
              type: 'recording',
              autoStop: pendingEventRef.current.autoStop,
            });
            // pendingEventRef는 Alert에서 처리됨
          } else if (pendingEventRef.current) {
            // Navigation이 아직 준비되지 않았으면 다시 시도
            console.log('[App] Navigation이 아직 준비되지 않음, 재시도...');
            setTimeout(() => {
              if (pendingEventRef.current && navigationRef.isReady()) {
                showAnalysisAlert({
                  filePath: pendingEventRef.current.filePath,
                  type: 'recording',
                  autoStop: pendingEventRef.current.autoStop,
                });
              }
            }, 1000);
          }
        }, 1500);
      }
    });

    return () => {
      recordingListener.remove();
      appStateSubscription.remove();
    };
  }, []);

  return (
    <NavigationContainer ref={navigationRef}>
      <AppNavigator />
    </NavigationContainer>
  );
}

