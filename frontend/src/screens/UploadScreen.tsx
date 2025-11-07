import React, { useState } from 'react';
import { View, Text, Button, Alert, StyleSheet, ActivityIndicator, Modal, TouchableOpacity, ImageBackground } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/AppNavigator';
import { analyzeVideo } from '../api';
import { Linking } from 'react-native';
import { FloatingWidget } from '../utils';

type Nav = StackNavigationProp<RootStackParamList, 'Upload'>;

export default function UploadScreen() {
  const navigation = useNavigation<Nav>();
  const [videoUri, setVideoUri] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<{ percentage: number; timeline: any; videoId?: string } | null>(null);

  
  const ensureMediaPermission = async () => {
    const perm = await ImagePicker.getMediaLibraryPermissionsAsync();
    if (perm.granted) return true;
    const ask = await ImagePicker.requestMediaLibraryPermissionsAsync();
    return ask.granted;
  };

  
  const pickVideo = async () => {
    const ok = await ensureMediaPermission();
    if (!ok) {
      Alert.alert('권한 필요', '갤러리 접근 권한이 필요합니다.');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Videos,
      allowsEditing: false,
      quality: 1,
    });

    if (!result.canceled && result.assets?.[0]?.uri) {
      setVideoUri(result.assets[0].uri);
    }
  };

  
  const handleAnalyze = async () => {
    if (!videoUri) {
      Alert.alert('영상이 선택되지 않았습니다.');
      return;
    }

    try {
      setBusy(true);
      setAnalyzing(true);
      setAnalysisResult(null);
      
      // 알림창을 "분석 중" 상태로 업데이트
      try {
        await FloatingWidget.updateAnalyzing();
        console.log("[UploadScreen] 알림창을 분석 중 상태로 업데이트");
      } catch (e) {
        console.error("[UploadScreen] 알림 상태 업데이트 실패:", e);
      }
      
      // Firebase 업로드를 생략하고, 디바이스 로컬 URI를 그대로 백엔드로 전송
      const res: any = await analyzeVideo(videoUri, 'user123');
      const timeline = Array.isArray(res?.timeline) ? res.timeline : undefined;
      console.log("분석 결과:", res);
      console.log("타임라인:", timeline);
      
      // 딥페이크 확률 계산
      // 백엔드에서 이미 계산된 overall_confidence를 우선 사용 (FAKE confidence로 계산됨)
      let deepfakePercentage = 0;
      
      // 1순위: video_analysis.overall_confidence (백엔드에서 FAKE confidence로 계산)
      if (res?.video_analysis?.overall_confidence !== undefined) {
        deepfakePercentage = Math.round(res.video_analysis.overall_confidence * 100);
      }
      // 2순위: summary.overall_confidence (FAKE일 때)
      else if (res?.summary?.overall_result === 'FAKE' && res?.summary?.overall_confidence !== undefined) {
        deepfakePercentage = Math.round(res.summary.overall_confidence * 100);
      }
      // 3순위: timeline 기반 계산 (FAKE 세그먼트의 fake_confidence 사용)
      else if (timeline && timeline.length > 0) {
        const fakeSegments = timeline.filter((item: any) => item.result === 'FAKE' || item.result === 'fake');
        
        if (fakeSegments.length > 0) {
          // FAKE 세그먼트의 details.video.fake_confidence 우선 사용
          let totalFakeConf = 0;
          let count = 0;
          
          fakeSegments.forEach((segment: any) => {
            if (segment.details?.video?.fake_confidence !== undefined) {
              totalFakeConf += segment.details.video.fake_confidence;
              count++;
            } else if (segment.confidence !== undefined) {
              // fallback: segment confidence 사용 (FAKE 세그먼트의 confidence는 FAKE confidence로 가정)
              totalFakeConf += segment.confidence;
              count++;
            }
          });
          
          if (count > 0) {
            const avgFakeConfidence = totalFakeConf / count;
            deepfakePercentage = Math.round(avgFakeConfidence * 100);
          } else {
            // FAKE 세그먼트가 있지만 confidence 정보가 없는 경우, FAKE 비율로 계산
            const fakeRatio = fakeSegments.length / timeline.length;
            deepfakePercentage = Math.round(fakeRatio * 100);
          }
        } else {
          // FAKE 세그먼트가 없는 경우 (REAL로 판정)
          deepfakePercentage = 0;
        }
      }
      
      console.log("[UploadScreen] 계산된 딥페이크 확률:", deepfakePercentage + "%");
      
      // 오디오 확률 계산
      let audioPercentage = 0;
      if (res?.audio_analysis?.fake_confidence !== undefined) {
        audioPercentage = Math.round(res.audio_analysis.fake_confidence * 100);
      } else if (res?.summary?.audio_confidence !== undefined) {
        audioPercentage = Math.round(res.summary.audio_confidence * 100);
      }
      
      // 분석 결과 (FAKE 또는 REAL)
      const result = res?.summary?.overall_result || res?.video_analysis?.overall_result || (deepfakePercentage > 50 ? "FAKE" : "REAL");
      
      // 알림창 업데이트 (분석 완료 상태)
      try {
        await FloatingWidget.updateAnalysisResult(
          result,
          deepfakePercentage,
          audioPercentage,
          res?.videoId || null
        );
        console.log("[UploadScreen] 알림창 업데이트 완료");
      } catch (e) {
        console.error("[UploadScreen] 알림창 업데이트 실패:", e);
      }
      
      // 분석 완료 - 결과를 Modal로 표시
      setAnalysisResult({ percentage: deepfakePercentage, timeline, videoId: res?.videoId });
      setAnalyzing(false);
      setBusy(false);
    } catch (error: any) {
      console.error(error);
      setAnalyzing(false);
      setAnalysisResult(null);
      
      // 백엔드에서 얼굴이 감지되지 않았다는 에러 메시지 처리
      const errorMessage = error?.response?.data?.error || error?.message || error?.toString() || "알 수 없는 오류";
      if (errorMessage.includes("얼굴이 감지되지") || errorMessage.includes("face")) {
        Alert.alert(
          "얼굴 감지 실패",
          "영상에서 얼굴이 감지되지 않았습니다.\n사람 얼굴이 포함된 영상을 업로드해주세요."
        );
      } else {
        Alert.alert('업로드 또는 분석 실패', errorMessage);
      }
      setBusy(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* 분석 중/완료 Modal */}
      <Modal
        visible={analyzing || analysisResult !== null}
        transparent={true}
        animationType="fade"
        onRequestClose={() => {
          if (analysisResult !== null) {
            setAnalysisResult(null);
            setBusy(false);
          }
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
                <Text style={styles.modalResultLabel}>AI 영상 확률</Text>
                <View style={styles.modalButtonContainer}>
                  <TouchableOpacity
                    style={styles.modalButtonClose}
                    onPress={() => {
                      setAnalysisResult(null);
                      setBusy(false);
                    }}
                    activeOpacity={0.8}
                  >
                    <View style={styles.modalButtonCloseBackground}>
                      <Text style={styles.modalButtonCloseText}>닫기</Text>
                    </View>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={styles.modalButtonDownload}
                    onPress={async () => {
                      try {
                        if (!analysisResult?.videoId) {
                          Alert.alert("오류", "비디오 ID를 찾을 수 없습니다.");
                          return;
                        }
                        
                        setBusy(true);
                        
                        // JSONL, CSV, Metadata 파일 모두 다운로드
                        const fileTypes: Array<{type: 'jsonl' | 'csv' | 'metadata', name: string}> = [
                          { type: 'jsonl', name: '데이터셋 JSONL' },
                          { type: 'csv', name: '타임라인 CSV' },
                          { type: 'metadata', name: '메타데이터 JSON' }
                        ];
                        
                        for (const file of fileTypes) {
                          try {
                            const downloadUrl = await downloadDataset(analysisResult.videoId, file.type);
                            const supported = await Linking.canOpenURL(downloadUrl);
                            if (supported) {
                              await Linking.openURL(downloadUrl);
                              // 각 파일 사이에 약간의 딜레이
                              await new Promise(resolve => setTimeout(resolve, 500));
                            }
                          } catch (error: any) {
                            console.error(`${file.name} 다운로드 오류:`, error);
                          }
                        }
                        
                        Alert.alert("다운로드 시작", "데이터셋 파일 다운로드가 시작되었습니다.\n(JSONL, CSV, JSON)");
                        
                        setAnalysisResult(null);
                        setBusy(false);
                      } catch (error: any) {
                        console.error("데이터셋 다운로드 오류:", error);
                        Alert.alert("오류", `데이터셋 다운로드 실패: ${error?.message || "알 수 없는 오류"}`);
                        setBusy(false);
                      }
                    }}
                    activeOpacity={0.8}
                    disabled={busy}
                  >
                    <View style={styles.modalButtonDownloadBackground}>
                      <Text style={styles.modalButtonDownloadText}>데이터셋 다운로드</Text>
                    </View>
                  </TouchableOpacity>
                </View>
              </>
            ) : null}
          </View>
        </View>
      </Modal>

      <Button title="🎞 영상 선택" onPress={pickVideo} />
      {videoUri && <Text style={styles.text}>선택된 영상: {videoUri}</Text>}

      <View style={{ height: 16 }} />

      <Button
        title={busy ? '처리 중…' : '분석 요청'}
        onPress={handleAnalyze}
        disabled={!videoUri || busy}
        color="#111827"
      />

      {busy && !analyzing && analysisResult === null && (
        <View style={styles.overlay}>
          <ActivityIndicator size="large" />
          <Text style={styles.dim}>업로드 및 분석 중…</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20, backgroundColor: '#000' },
  text: { marginVertical: 10, color: '#9ca3af' },
  overlay: { marginTop: 20, alignItems: 'center' },
  dim: { marginTop: 6, color: '#9ca3af' },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.8)",
    justifyContent: "center",
    alignItems: "center",
  },
  modalContent: {
    backgroundColor: "#1f2937",
    borderRadius: 20,
    padding: 32,
    alignItems: "center",
    minWidth: 300,
    maxWidth: "80%",
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#fff",
    marginTop: 20,
    marginBottom: 12,
  },
  modalSubtitle: {
    fontSize: 16,
    color: "#9ca3af",
    textAlign: "center",
    marginBottom: 8,
  },
  modalResultPercentage: {
    fontSize: 64,
    fontWeight: "bold",
    color: "#2563eb",
    marginTop: 20,
    marginBottom: 8,
  },
  modalResultLabel: {
    fontSize: 18,
    color: "#9ca3af",
    marginBottom: 32,
  },
  modalButtonContainer: {
    flexDirection: "row",
    gap: 12,
    width: "100%",
    alignItems: "center",
  },
  modalButton: {
    flex: 1,
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: "center",
  },
  modalButtonCancel: {
    backgroundColor: "#374151",
  },
  modalButtonConfirm: {
    backgroundColor: "#2563eb",
  },
  modalButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "700",
  },
  modalButtonClose: {
    flex: 1,
    height: 70,
  },
  modalButtonCloseBackground: {
    width: "100%",
    height: 70,
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 18,
    backgroundColor: "#374151", // 회색 배경
    borderRadius: 10,
  },
  modalButtonCloseText: {
    color: "#000000",
    fontSize: 24,
    fontWeight: "800",
    letterSpacing: 2,
  },
  modalButtonDownload: {
    flex: 1,
    height: 70,
  },
  modalButtonDownloadBackground: {
    width: "100%",
    height: 70,
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 18,
    backgroundColor: "#2563eb", // 파란색 배경
    borderRadius: 10,
  },
  modalButtonDownloadText: {
    color: "#000000",
    fontSize: 24,
    fontWeight: "800",
    letterSpacing: 2,
  },
});
