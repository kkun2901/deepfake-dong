import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  SafeAreaView,
  StatusBar,
  Image,
  ImageBackground,
  ImageStyle,
  Alert,
  Platform,
  Modal,
  ActivityIndicator,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { useNavigation } from '@react-navigation/native';
import { DrawerActions } from '@react-navigation/native';
import { RootStackParamList } from '../navigation/AppNavigator';
import { FloatingWidget, FloatingWidgetEvents } from '../utils';

type Nav = StackNavigationProp<RootStackParamList, 'Home'>;

export default function HomeScreen() {
  const navigation = useNavigation<Nav>();
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<{
    percentage: number;
    result: 'FAKE' | 'REAL';
  } | null>(null);

  useEffect(() => {
    if (Platform.OS !== 'android' || !FloatingWidgetEvents) {
      return;
    }

    // 분석 시작 이벤트 리스너
    const analyzingListener = FloatingWidgetEvents.addListener(
      'onAnalyzing',
      () => {
        console.log('[HomeScreen] 분석 시작 이벤트 수신');
        setAnalyzing(true);
        setAnalysisResult(null);
      }
    );

    // 분석 완료 이벤트 리스너
    const resultListener = FloatingWidgetEvents.addListener(
      'onAnalysisResult',
      (data: { result: string; deepfakePercentage: number; audioPercentage: number; videoId: string | null }) => {
        console.log('[HomeScreen] 분석 완료 이벤트 수신:', data);
        setAnalyzing(false);
        setAnalysisResult({
          percentage: data.deepfakePercentage,
          result: data.result === 'FAKE' ? 'FAKE' : 'REAL',
        });
      }
    );

    return () => {
      analyzingListener.remove();
      resultListener.remove();
    };
  }, []);

  return (
    <ImageBackground 
      source={require('../assets/home-background.png')}
      style={styles.backgroundImage}
      resizeMode="cover"
    >
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#000000" />
        
        <View style={styles.header}>
        <View style={styles.profileIcon}>
          <Text style={styles.profileIconText}>U</Text>
        </View>
        <TouchableOpacity 
          style={styles.menuButton}
          onPress={() => navigation.dispatch(DrawerActions.openDrawer())}
        >
          <View style={styles.menuIcon}>
            <View style={styles.menuLine} />
            <View style={styles.menuLine} />
            <View style={styles.menuLine} />
          </View>
        </TouchableOpacity>
      </View>

      <View style={styles.content}>
        {/* 배경 이미지에 로고가 포함되어 있으므로 주석 처리 */}
        {/* <View style={styles.logoContainer}>
          <Image 
            source={require('../assets/normal.logo.home.png')}
            style={styles.logoImage as ImageStyle}
            resizeMode="contain"
          />
        </View> */}

        {/* 배경 이미지에 스포트라이트가 포함되어 있으므로 주석 처리 */}
        {/* <View style={styles.spotlightContainer}>
          <View style={styles.spotlightTriangle} />
          <View style={styles.spotlightBeam} />
        </View> */}

        <TouchableOpacity 
          style={styles.switchButtonContainer}
          onPress={async () => {
            if (Platform.OS !== 'android') {
              Alert.alert('알림', 'Android 전용 기능입니다.');
              return;
            }
            try {
              console.log('[HomeScreen] 위젯 시작 시도...');
              
              // 네이티브 모듈 확인
              const { NativeModules } = require('react-native');
              const allModules = Object.keys(NativeModules);
              const hasExpoGo = !!(NativeModules as any)?.ExpoGo;
              const widgetModule = (NativeModules as any)?.FloatingWidgetModule;
              
              if (hasExpoGo) {
                console.error('[HomeScreen] Expo Go를 사용 중입니다. 위젯 기능을 사용할 수 없습니다.');
                Alert.alert(
                  'Expo Go 사용 중', 
                  '위젯 기능은 Expo Go에서 사용할 수 없습니다.\n\n' +
                  '다음 중 하나를 선택하세요:\n\n' +
                  '1. 네이티브 빌드:\n' +
                  '   npm run android\n\n' +
                  '2. Dev Client:\n' +
                  '   npx expo start --dev-client\n\n' +
                  'Expo Go는 커스텀 네이티브 모듈을 지원하지 않습니다.'
                );
                return;
              }
              
              if (!widgetModule) {
                console.error('[HomeScreen] FloatingWidgetModule이 로드되지 않았습니다.');
                console.error('[HomeScreen] 사용 가능한 모듈:', allModules.slice(0, 10));
                Alert.alert(
                  '위젯 모듈 없음', 
                  'FloatingWidgetModule이 구현되지 않았습니다.\n\n' +
                  '위젯 기능을 사용하려면:\n\n' +
                  '1. FloatingWidgetModule을 Android 네이티브 코드로 구현해야 합니다.\n\n' +
                  '2. 구현 후 앱을 다시 빌드하세요:\n' +
                  '   npm run android\n\n' +
                  '현재는 위젯 기능을 사용할 수 없습니다.\n' +
                  '다른 기능(영상 업로드, 커뮤니티)은 정상 작동합니다.'
                );
                return;
              }
              
              // 오버레이 권한 확인 및 요청
              const hasOverlayPermission = await FloatingWidget.checkOverlayPermission();
              
              if (!hasOverlayPermission) {
                const granted = await FloatingWidget.requestOverlayPermission();
                if (!granted) {
                  Alert.alert(
                    '권한 필요',
                    '플로팅 위젯을 사용하려면 "다른 앱 위에 표시" 권한이 필요합니다.\n\n' +
                    '설정에서 권한을 허용한 후 다시 시도해주세요.'
                  );
                  return;
                }
              }
              
              // 서비스 시작
              try {
                await FloatingWidget.startService();
                console.log('[HomeScreen] 서비스 시작 완료');
                Alert.alert(
                  '서비스 시작', 
                  '플로팅 위젯이 화면에 표시됩니다.\n\n' +
                  '위젯을 클릭하여 다음 기능을 사용할 수 있습니다:\n' +
                  '- 녹화: 화면 녹화 시작/중지\n' +
                  '- 캡처: 화면 캡처\n' +
                  '- 종료: 서비스 종료'
                );
              } catch (serviceError) {
                console.error('[HomeScreen] 서비스 시작 오류:', serviceError);
                Alert.alert('오류', `서비스를 시작할 수 없습니다: ${serviceError}`);
              }
            } catch (e) {
              console.error('[HomeScreen] start widget error:', e);
              Alert.alert('오류', `위젯 시작 중 오류가 발생했습니다: ${String(e)}`);
            }
          }}
          activeOpacity={0.8}
        >
          <View style={styles.switchButtonBackground}>
            <Text style={styles.switchButtonText}>직접 녹화</Text>
          </View>
        </TouchableOpacity>

        {/* 업로드하여 탐지 버튼 */}
        <TouchableOpacity 
          style={styles.switchButtonContainer}
          onPress={() => navigation.navigate('Upload')}
          activeOpacity={0.8}
        >
          <View style={styles.uploadButtonBackground}>
            <Text style={styles.uploadButtonText}>영상으로 탐지</Text>
          </View>
        </TouchableOpacity>
      </View>

      {/* 분석 결과 Modal */}
      <Modal
        visible={analyzing || analysisResult !== null}
        transparent={true}
        animationType="fade"
        onRequestClose={() => {
          setAnalyzing(false);
          setAnalysisResult(null);
        }}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {analyzing ? (
              <>
                <ActivityIndicator size="large" color="#2563eb" />
                <Text style={styles.modalTitle}>분석 중</Text>
                <Text style={styles.modalSubtitle}>영상을 분석하고 있습니다.</Text>
                <Text style={styles.modalSubtitle}>잠시만 기다려주세요...</Text>
              </>
            ) : analysisResult !== null ? (
              <>
                <Text style={styles.modalTitle}>분석 완료</Text>
                <Text style={styles.modalResultPercentage}>{analysisResult.percentage}%</Text>
                <Text style={styles.modalResultLabel}>딥페이크 확률</Text>
                <Text style={styles.modalResultText}>
                  이 영상은 {analysisResult.result === 'FAKE' ? '가짜' : '진짜'}입니다
                </Text>
                <TouchableOpacity
                  style={styles.modalButton}
                  onPress={() => {
                    setAnalysisResult(null);
                    setAnalyzing(false);
                  }}
                  activeOpacity={0.8}
                >
                  <View style={styles.modalButtonBackground}>
                    <Text style={styles.modalButtonText}>확인</Text>
                  </View>
                </TouchableOpacity>
              </>
            ) : null}
          </View>
        </View>
      </Modal>
    </SafeAreaView>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  backgroundImage: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  container: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 10,
  },
  profileIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#333333',
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileIconText: {
    fontSize: 20,
  },
  menuButton: {
    padding: 5,
  },
  menuIcon: {
    width: 24,
    height: 18,
    justifyContent: 'space-between',
  },
  menuLine: {
    height: 3,
    width: 24,
    backgroundColor: '#FFFFFF',
    borderRadius: 2,
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  mainMessage: {
    fontSize: 24,
    fontWeight: '700',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 40,
    lineHeight: 34,
  },
  logoContainer: {
    width: 200,
    height: 200,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 30,
    zIndex: 3,
  },
  logoImage: {
    width: '100%',
    height: '100%',
  } as ImageStyle,
  spotlightContainer: {
    position: 'absolute',
    top: '45%',
    width: '100%',
    alignItems: 'center',
    zIndex: 1,
  },
  spotlightTriangle: {
    width: 0,
    height: 0,
    borderLeftWidth: 100,
    borderRightWidth: 100,
    borderTopWidth: 50,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    borderTopColor: 'rgba(85, 107, 47, 0.3)', // 올리브 그린 (#556B2F) with 30% opacity
    marginBottom: -1,
  },
  spotlightBeam: {
    width: 320,
    height: 450,
    backgroundColor: 'rgba(85, 107, 47, 0.3)', // 올리브 그린 (#556B2F) with 30% opacity
    transform: [{ perspective: 1000 }, { rotateX: '10deg' }],
    borderBottomLeftRadius: 160,
    borderBottomRightRadius: 160,
  },
  switchButtonContainer: {
    marginTop: 50,
    zIndex: 2,
    width: '80%',
    maxWidth: 400,
  },
  switchButtonBackground: {
    width: '100%',
    height: 70,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 18,
    backgroundColor: '#2563eb', // 파란색
    borderWidth: 2,
    borderColor: '#FFFFFF', // 흰색 윤곽선
    borderRadius: 10,
  },
  switchButtonText: {
    color: '#FFFFFF', // 하얀색 텍스트
    fontSize: 24,
    fontWeight: '800',
    letterSpacing: 2,
  },
  uploadButtonBackground: {
    width: '100%',
    height: 70,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 18,
    backgroundColor: '#000000', // 검은색
    borderWidth: 2,
    borderColor: '#FFFFFF', // 흰색 윤곽선
    borderRadius: 10,
  },
  uploadButtonText: {
    color: '#FFFFFF', // 하얀색 텍스트
    fontSize: 24,
    fontWeight: '800',
    letterSpacing: 2,
  },
  signupButtonContainer: {
    marginTop: 15,
    zIndex: 2,
    width: '80%',
    maxWidth: 400,
  },
  signupButtonBackground: {
    width: '100%',
    height: 70,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 18,
    backgroundColor: '#FFD700', // 노란색 배경
    borderRadius: 10,
  },
  signupButtonText: {
    color: '#000000', // 노란색 배경에 검은 글씨
    fontSize: 20,
    fontWeight: '800',
  },
  faceContainer: {
    position: 'absolute',
    bottom: 40, // 사람 이미지를 더 아래로 이동
    width: '100%',
    height: 150,
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 2,
  },
  faceImage: {
    width: 150,
    height: 150,
  } as ImageStyle,
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#1f2937',
    borderRadius: 20,
    padding: 32,
    alignItems: 'center',
    minWidth: 300,
    maxWidth: '80%',
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 20,
    marginBottom: 12,
  },
  modalSubtitle: {
    fontSize: 16,
    color: '#9ca3af',
    textAlign: 'center',
    marginBottom: 8,
  },
  modalResultPercentage: {
    fontSize: 64,
    fontWeight: 'bold',
    color: '#2563eb',
    marginTop: 20,
    marginBottom: 8,
  },
  modalResultLabel: {
    fontSize: 18,
    color: '#9ca3af',
    marginBottom: 16,
  },
  modalResultText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 32,
    textAlign: 'center',
  },
  modalButton: {
    width: '100%',
    height: 50,
  },
  modalButtonBackground: {
    width: '100%',
    height: 50,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#2563eb',
    borderRadius: 10,
  },
  modalButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
  },
});
