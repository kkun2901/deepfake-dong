import React, { useCallback, useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert, Platform, AppState } from "react-native";
import { FloatingWidget, FloatingWidgetEvents } from "../utils";
import { useNavigation, useFocusEffect } from "@react-navigation/native";
import { StackNavigationProp } from "@react-navigation/stack";
import type { RootStackParamList } from "../navigation/AppNavigator";

type Nav = StackNavigationProp<RootStackParamList, "WidgetControl">;

export default function WidgetControlScreen() {
  const navigation = useNavigation<Nav>();
  const [hasOverlay, setHasOverlay] = useState(false);
  const [serviceOn, setServiceOn] = useState(false);
  const [recording, setRecording] = useState(false);

  const refreshPerm = useCallback(async () => {
    const ok = await FloatingWidget.checkOverlayPermission();
    setHasOverlay(ok);
  }, []);

  useEffect(() => {
    if (Platform.OS === "android") {
      refreshPerm();
    }
  }, [refreshPerm]);

  // 앱이 포커스를 받을 때마다 권한 상태 다시 확인 (설정에서 돌아올 때)
  useFocusEffect(
    useCallback(() => {
      if (Platform.OS === "android") {
        refreshPerm();
      }
    }, [refreshPerm])
  );

  // 앱 상태 변경 시 권한 확인 (설정 화면에서 돌아올 때)
  useEffect(() => {
    const subscription = AppState.addEventListener("change", (nextAppState) => {
      if (nextAppState === "active" && Platform.OS === "android") {
        // 앱이 다시 활성화될 때 권한 상태 확인
        setTimeout(() => {
          refreshPerm();
        }, 500);
      }
    });

    return () => {
      subscription.remove();
    };
  }, [refreshPerm]);

  // 이벤트 리스너 등록 (위젯 화면 상태 업데이트용)
  // 전역 이벤트 처리는 App.tsx에서 수행
  useEffect(() => {
    if (!FloatingWidgetEvents) return;

    const recordingListener = FloatingWidgetEvents.addListener(
      "onRecordingComplete",
      (event: { filePath: string; type: string; autoStop?: boolean }) => {
        console.log("[WidgetControl] 녹화 완료:", event.filePath);
        setRecording(false);
        // 상태만 업데이트 (팝업은 App.tsx에서 처리)
      }
    );

    const captureListener = FloatingWidgetEvents.addListener(
      "onCaptureComplete",
      (event: { filePath: string; type: string }) => {
        console.log("캡처 완료:", event.filePath);
        Alert.alert("캡처 완료", `이미지가 저장되었습니다.\n${event.filePath}`);
      }
    );

    return () => {
      recordingListener.remove();
      captureListener.remove();
    };
  }, [navigation]);

  const onPressSwitch = async () => {
    // 먼저 권한 상태를 다시 확인
    const hasPermission = await FloatingWidget.checkOverlayPermission();
    setHasOverlay(hasPermission);
    
    if (!hasPermission) {
      // 권한이 없으면 요청
      const granted = await FloatingWidget.requestOverlayPermission();
      // 설정에서 돌아온 후 권한을 다시 확인
      setTimeout(async () => {
        const recheck = await FloatingWidget.checkOverlayPermission();
        setHasOverlay(recheck);
        if (recheck) {
          // 권한이 허용되었으면 서비스 시작
          await FloatingWidget.startService();
          setServiceOn(true);
          Alert.alert("위젯 시작", "홈으로 이동하면 플로팅 버튼이 표시됩니다.");
        } else {
          Alert.alert("권한 필요", "다른 앱 위에 표시 권한이 필요합니다.\n설정에서 권한을 허용한 후 다시 시도해주세요.");
        }
      }, 1000);
      return;
    }
    
    // 권한이 있으면 바로 서비스 시작
    await FloatingWidget.startService();
    setServiceOn(true);
    Alert.alert("위젯 시작", "홈으로 이동하면 플로팅 버튼이 표시됩니다.");
  };

  const onStopService = async () => {
    await FloatingWidget.stopService();
    setServiceOn(false);
  };

  const onStartRec = async () => {
    await FloatingWidget.startRecording();
    setRecording(true);
  };

  const onStopRec = async () => {
    const res = await FloatingWidget.stopRecording();
    setRecording(false);
    if (res?.filePath) {
      Alert.alert("녹화 완료", "업로드 또는 재촬영을 선택하세요.");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>플로팅 위젯 제어</Text>
      <Text style={styles.subtitle}>다른 앱 위에 떠 있는 버블을 제어합니다.</Text>

      <View style={styles.row}>
        <TouchableOpacity style={[styles.btn, styles.primary]} onPress={onPressSwitch}>
          <Text style={styles.btnText}>Switch on!</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.btn, styles.secondary]} onPress={onStopService}>
          <Text style={styles.btnText}>위젯 종료</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.row}>
        {!recording ? (
          <TouchableOpacity style={[styles.btn, styles.warn]} onPress={onStartRec}>
            <Text style={styles.btnText}>녹화 시작</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity style={[styles.btn, styles.danger]} onPress={onStopRec}>
            <Text style={styles.btnText}>녹화 종료</Text>
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.hintBox}>
        <Text style={styles.hint}>- Switch on!을 누르면 홈 화면으로 나가 위젯을 확인하세요.</Text>
        <Text style={styles.hint}>- 위젯 버블을 눌러 메뉴(녹화/캡쳐/종료)를 토글합니다.</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000", padding: 20 },
  title: { color: "#fff", fontSize: 24, fontWeight: "bold", marginBottom: 8 },
  subtitle: { color: "#9ca3af", marginBottom: 24 },
  row: { flexDirection: "row", gap: 12, marginBottom: 12 },
  btn: { paddingVertical: 12, paddingHorizontal: 16, borderRadius: 12, alignItems: "center" },
  primary: { backgroundColor: "#2563eb" },
  secondary: { backgroundColor: "#374151" },
  warn: { backgroundColor: "#10b981" },
  danger: { backgroundColor: "#dc2626" },
  btnText: { color: "#fff", fontWeight: "700" },
  hintBox: { marginTop: 24, backgroundColor: "#111827", borderRadius: 12, padding: 12 },
  hint: { color: "#9ca3af", marginBottom: 6 },
});






