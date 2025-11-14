// src/navigation/AppNavigator.tsx
import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import { createDrawerNavigator } from "@react-navigation/drawer";

import HomeScreen from "../screens/HomeScreen";
import RecordScreen from "../screens/RecordScreen";
import UploadScreen from "../screens/UploadScreen";
import ResultScreen from "../screens/ResultScreen";
import ReportScreen from "../screens/ReportScreen";
import MetricsScreen from "../screens/MetricsScreen";
import CameraSmokeTest from "../screens/CameraSmokeTest";
import WidgetControlScreen from "../screens/WidgetControlScreen";
import CommunityScreen from "../screens/CommunityScreen";
import CommunityWriteScreen from "../screens/CommunityWriteScreen";
import CommunityDetailScreen from "../screens/CommunityDetailScreen";

export type RootStackParamList = {
  Main: undefined;
  Home: undefined;
  Record: { recordedVideoPath?: string; showAnalysisProgress?: boolean } | undefined;
  Upload: undefined;
  Result:
    | {
        videoUri?: string;
        timeline?: Array<{ t: number; label: "suspect" | "normal"; score: number }>;
        videoId?: string;
      }
    | undefined;
  Report: { videoUri?: string } | undefined;
  Metrics: undefined;
  CameraSmoke: undefined;
  WidgetControl: undefined;
  Community: undefined;
  CommunityWrite: undefined;
  CommunityDetail: { postId: string };
};

const Stack = createStackNavigator<RootStackParamList>();
const Drawer = createDrawerNavigator();

// Drawer Navigator로 메인 화면 구성
function DrawerNavigator() {
  return (
    <Drawer.Navigator
      initialRouteName="Home"
      screenOptions={{
        headerShown: false,
        drawerStyle: {
          backgroundColor: '#1a1a1a',
          width: 280,
        },
        drawerActiveTintColor: '#FFFFFF',
        drawerInactiveTintColor: '#888888',
        drawerLabelStyle: {
          fontSize: 16,
          fontWeight: '500',
        },
      }}
    >
      <Drawer.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{
          drawerLabel: '홈',
        }}
      />
      <Drawer.Screen 
        name="Community" 
        component={CommunityScreen} 
        options={{
          drawerLabel: '커뮤니티',
        }}
      />
    </Drawer.Navigator>
  );
}

export default function AppNavigator() {
  return (
    <Stack.Navigator
      initialRouteName="Main" // Drawer Navigator를 메인으로 설정
      screenOptions={{ headerTitleAlign: "center" }}
    >
      <Stack.Screen name="Main" component={DrawerNavigator} options={{ headerShown: false }} />
      <Stack.Screen name="CameraSmoke" component={CameraSmokeTest} options={{ title: "카메라 테스트" }} />
      <Stack.Screen name="Record" component={RecordScreen} options={{ title: "녹화하기" }} />
      <Stack.Screen name="Upload" component={UploadScreen} options={{ title: "영상 업로드" }} />
      <Stack.Screen name="Result" component={ResultScreen} options={{ title: "분석 결과" }} />
      <Stack.Screen name="Report" component={ReportScreen} options={{ title: "신고하기" }} />
      <Stack.Screen name="Metrics" component={MetricsScreen} options={{ title: "지표" }} />
      <Stack.Screen name="WidgetControl" component={WidgetControlScreen} options={{ title: "위젯 제어" }} />
      <Stack.Screen name="CommunityWrite" component={CommunityWriteScreen} options={{ title: "글 작성" }} />
      <Stack.Screen name="CommunityDetail" component={CommunityDetailScreen} options={{ title: "게시글" }} />
    </Stack.Navigator>
  );
}
