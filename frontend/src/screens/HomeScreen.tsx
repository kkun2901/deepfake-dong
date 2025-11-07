import React from 'react';
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
  PermissionsAndroid,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { useNavigation } from '@react-navigation/native';
import { DrawerActions } from '@react-navigation/native';
import { RootStackParamList } from '../navigation/AppNavigator';
import { FloatingWidget } from '../utils';

type Nav = StackNavigationProp<RootStackParamList, 'Home'>;

export default function HomeScreen() {
  const navigation = useNavigation<Nav>();

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
          <Text style={styles.profileIconText}>👤</Text>
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
              
              // Android 13+ 알림 권한 요청
              if (Platform.OS === 'android' && Platform.Version >= 33) {
                try {
                  // React Native 0.74+에서는 'android.permission.POST_NOTIFICATIONS' 문자열 사용
                  const POST_NOTIFICATIONS = 'android.permission.POST_NOTIFICATIONS';
                  
                  const hasPermission = await PermissionsAndroid.check(POST_NOTIFICATIONS);
                  
                  if (!hasPermission) {
                    const granted = await PermissionsAndroid.request(
                      POST_NOTIFICATIONS,
                      {
                        title: '알림 권한',
                        message: '딥페이크 탐지 서비스를 사용하려면 알림 권한이 필요합니다.',
                        buttonNeutral: '나중에',
                        buttonNegative: '취소',
                        buttonPositive: '허용',
                      }
                    );
                    
                    if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
                      Alert.alert(
                        '권한 필요',
                        '알림 권한이 필요합니다. 설정에서 권한을 허용해주세요.'
                      );
                      return;
                    }
                  }
                } catch (err) {
                  console.warn('[HomeScreen] 알림 권한 요청 오류:', err);
                }
              }
              
              // 서비스 시작
              try {
                await FloatingWidget.startService();
                console.log('[HomeScreen] 서비스 시작 완료');
                Alert.alert(
                  '서비스 시작', 
                  '알림창에 딥페이크 탐지 서비스가 표시됩니다.\n\n' +
                  '알림창에서 다음 기능을 사용할 수 있습니다:\n' +
                  '- 비디오: 화면 녹화 시작/중지\n' +
                  '- 녹화 종료 시 자동으로 분석됩니다'
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
          <ImageBackground 
            source={require('../assets/login.bar.background.png')}
            style={styles.switchButtonBackground}
            resizeMode="stretch"
          >
            <Text style={styles.switchButtonText}>SWITCH ON!</Text>
          </ImageBackground>
        </TouchableOpacity>

        {/* 업로드하여 탐지 버튼 */}
        <TouchableOpacity 
          style={styles.switchButtonContainer}
          onPress={() => navigation.navigate('Upload')}
          activeOpacity={0.8}
        >
          <ImageBackground 
            source={require('../assets/login.bar.background.png')}
            style={styles.switchButtonBackground}
            resizeMode="stretch"
          >
            <Text style={styles.switchButtonText}>영상으로 탐지</Text>
          </ImageBackground>
        </TouchableOpacity>
      </View>
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
  },
  switchButtonText: {
    color: '#000000', // 흰색 배경에 검은 글씨
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
});
