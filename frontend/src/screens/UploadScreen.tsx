import React, { useState, useEffect } from 'react';
import { View, Text, Alert, StyleSheet, Modal, TouchableOpacity } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { SvgXml } from 'react-native-svg';
import { analyzeVideo } from '../api';

const LOADING_SVGS = [
  `<svg width="54" height="54" viewBox="0 0 54 54" fill="none" xmlns="http://www.w3.org/2000/svg"><g opacity="0.2"><circle cx="26.9671" cy="26.9671" r="26.9671" fill="black"/><path d="M53.9341 26.9671C53.9341 30.5085 53.2366 34.0152 51.8814 37.287C50.5261 40.5588 48.5398 43.5316 46.0356 46.0357C43.5315 48.5398 40.5587 50.5262 37.2869 51.8814C34.0151 53.2366 30.5084 53.9342 26.9671 53.9342L26.9671 26.9671L53.9341 26.9671Z" fill="#FFC628"/><circle cx="26.3251" cy="26.4159" r="13.7222" fill="white"/><circle cx="31.6947" cy="31.7854" r="8.35263" fill="black"/></g></svg>`,
  `<svg width="74" height="74" viewBox="0 0 74 74" fill="none" xmlns="http://www.w3.org/2000/svg"><g opacity="0.4"><circle cx="36.8377" cy="36.8377" r="26.9671" transform="rotate(-30 36.8377 36.8377)" fill="black"/><path d="M60.1918 23.3542C61.9625 26.4211 63.1118 29.8068 63.574 33.3178C64.0363 36.8289 63.8024 40.3966 62.8859 43.8173C61.9693 47.238 60.3879 50.4447 58.2321 53.2542C56.0762 56.0638 53.3881 58.4212 50.3212 60.1919L36.8377 36.8377L60.1918 23.3542Z" fill="#FFC628"/><circle cx="36.0062" cy="36.6813" r="13.7222" transform="rotate(-30 36.0062 36.6813)" fill="white"/><circle cx="43.3411" cy="38.6467" r="8.35263" transform="rotate(-30 43.3411 38.6467)" fill="black"/></g></svg>`,
  `<svg width="74" height="74" viewBox="0 0 74 74" fill="none" xmlns="http://www.w3.org/2000/svg"><g opacity="0.6"><circle cx="36.8377" cy="36.8377" r="26.9671" transform="rotate(-60 36.8377 36.8377)" fill="black"/><path d="M50.3212 13.4835C53.3881 15.2542 56.0762 17.6116 58.2321 20.4212C60.3879 23.2307 61.9693 26.4374 62.8859 29.8581C63.8024 33.2788 64.0363 36.8465 63.574 40.3576C63.1118 43.8687 61.9625 47.2543 60.1918 50.3212L36.8377 36.8377L50.3212 13.4835Z" fill="#FFC628"/><circle cx="36.0394" cy="37.118" r="13.7222" transform="rotate(-60 36.0394 37.118)" fill="white"/><circle cx="43.3743" cy="35.1526" r="8.35263" transform="rotate(-60 43.3743 35.1526)" fill="black"/></g></svg>`,
  `<svg width="54" height="54" viewBox="0 0 54 54" fill="none" xmlns="http://www.w3.org/2000/svg"><g opacity="0.9"><circle cx="26.9671" cy="26.9671" r="26.9671" transform="matrix(0 -1 1 0 0 53.9341)" fill="black"/><path d="M26.9671 0C30.5084 0 34.0151 0.697525 37.2869 2.05275C40.5587 3.40797 43.5315 5.39434 46.0356 7.89847C48.5398 10.4026 50.5261 13.3754 51.8814 16.6472C53.2366 19.919 53.9341 23.4257 53.9341 26.9671L26.9671 26.9671L26.9671 0Z" fill="#FFC628"/><circle cx="26.4159" cy="27.609" r="13.7222" transform="rotate(-90 26.4159 27.609)" fill="white"/><circle cx="31.7854" cy="22.2394" r="8.35263" transform="rotate(-90 31.7854 22.2394)" fill="black"/></g></svg>`
];

const LOADING_SIZES = [54, 74, 74, 54];

export default function UploadScreen() {
  const [videoUri, setVideoUri] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [confirmVisible, setConfirmVisible] = useState(false);
  const [overlayVisible, setOverlayVisible] = useState(false);
  const [overlayMode, setOverlayMode] = useState<'loading' | 'result'>('loading');
  const [overlayPercentage, setOverlayPercentage] = useState(0);
  const [overlayResult, setOverlayResult] = useState<'FAKE' | 'REAL'>('REAL');
  const [loadingFrame, setLoadingFrame] = useState(0);

  useEffect(() => {
    pickVideo();
  }, []);

  useEffect(() => {
    if (overlayVisible && overlayMode === 'loading') {
      const timer = setInterval(() => {
        setLoadingFrame((prev) => (prev + 1) % LOADING_SVGS.length);
      }, 250);
      return () => clearInterval(timer);
    }
  }, [overlayVisible, overlayMode]);

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
      setConfirmVisible(true);
    }
  };

  const handleAnalyze = async () => {
    if (!videoUri) {
      Alert.alert('영상이 선택되지 않았습니다.');
      return;
    }

    try {
      setBusy(true);
      setConfirmVisible(false);
      setOverlayMode('loading');
      setOverlayVisible(true);
      setLoadingFrame(0);

      const res: any = await analyzeVideo(videoUri, 'user123');
      const timeline = Array.isArray(res?.timeline) ? res.timeline : undefined;

      let deepfakePercentage = 0;
      if (res?.video_analysis?.overall_confidence !== undefined) {
        deepfakePercentage = Math.round(res.video_analysis.overall_confidence * 100);
      } else if (res?.summary?.overall_result === 'FAKE' && res?.summary?.overall_confidence !== undefined) {
        deepfakePercentage = Math.round(res.summary.overall_confidence * 100);
      } else if (timeline && timeline.length > 0) {
        const fakeSegments = timeline.filter((item: any) => item.result === 'FAKE' || item.result === 'fake');
        if (fakeSegments.length > 0) {
          let totalFakeConf = 0;
          let count = 0;
          fakeSegments.forEach((segment: any) => {
            if (segment.details?.video?.fake_confidence !== undefined) {
              totalFakeConf += segment.details.video.fake_confidence;
              count++;
            } else if (segment.confidence !== undefined) {
              totalFakeConf += segment.confidence;
              count++;
            }
          });
          if (count > 0) {
            deepfakePercentage = Math.round((totalFakeConf / count) * 100);
          }
        }
      }

      const resultLabel: 'FAKE' | 'REAL' =
        (res?.summary?.overall_result || res?.video_analysis?.overall_result || (deepfakePercentage > 50 ? 'FAKE' : 'REAL')) === 'FAKE'
          ? 'FAKE'
          : 'REAL';

      setOverlayPercentage(deepfakePercentage);
      setOverlayResult(resultLabel);
      setOverlayMode('result');
      setBusy(false);
    } catch (error: any) {
      console.error(error);
      setOverlayVisible(false);
      setBusy(false);
      const errorMessage = error?.response?.data?.error || error?.message || error?.toString() || '알 수 없는 오류';
      if (errorMessage.includes('얼굴이 감지되지') || errorMessage.includes('face')) {
        Alert.alert('얼굴 감지 실패', '영상에서 얼굴이 감지되지 않았습니다.\n사람 얼굴이 포함된 영상을 업로드해주세요.');
      } else {
        Alert.alert('분석 실패', errorMessage);
      }
    }
  };

  const closeOverlay = () => {
    setOverlayVisible(false);
    setOverlayMode('loading');
    setOverlayPercentage(0);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>영상으로 탐지</Text>
      <Text style={styles.subtitle}>분석할 영상을 선택한 뒤 분석을 진행하세요.</Text>

      <View style={styles.selectedBox}>
        <Text style={styles.selectedLabel}>선택된 영상</Text>
        <Text style={styles.selectedPath}>{videoUri ?? '아직 선택되지 않았습니다.'}</Text>
      </View>

      <TouchableOpacity style={styles.primaryButton} onPress={pickVideo} activeOpacity={0.8} disabled={busy}>
        <Text style={styles.primaryButtonText}>영상 다시 선택</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.secondaryButton, (!videoUri || busy) && styles.secondaryButtonDisabled]}
        onPress={() => setConfirmVisible(true)}
        activeOpacity={0.8}
        disabled={!videoUri || busy}
      >
        <Text style={styles.secondaryButtonText}>{busy ? '처리 중…' : '분석 시작'}</Text>
      </TouchableOpacity>

      {/* 분석 확인 모달 */}
      <Modal visible={confirmVisible} transparent animationType="fade" onRequestClose={() => setConfirmVisible(false)}>
        <View style={styles.modalOverlay}>
          <View style={styles.confirmCard}>
            <Text style={styles.confirmTitle}>영상 분석 안내</Text>
            <Text style={styles.confirmSubtitle}>선택한 영상을 분석하시겠습니까?</Text>
            <View style={styles.confirmButtons}>
              <TouchableOpacity
                style={[styles.confirmButton, styles.confirmButtonSpacing]}
                onPress={() => setConfirmVisible(false)}
                activeOpacity={0.8}
              >
                <Text style={styles.confirmButtonText}>취소</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.confirmButton} onPress={handleAnalyze} activeOpacity={0.8} disabled={busy}>
                <Text style={styles.confirmButtonText}>분석하기</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* 위젯 스타일 오버레이 */}
      <Modal visible={overlayVisible} transparent animationType="fade" onRequestClose={closeOverlay}>
        <View style={styles.widgetOverlay}>
          <View style={styles.widgetCard}>
            {overlayMode === 'loading' ? (
              <>
                <View style={styles.loadingRow}>
                  {LOADING_SVGS.map((svg, index) => (
                    <View
                      key={`loading-${index}`}
                      style={[
                        styles.loadingFrame,
                        { width: LOADING_SIZES[index], height: LOADING_SIZES[index] },
                        loadingFrame === index ? styles.loadingFrameVisible : styles.loadingFrameHidden,
                      ]}
                    >
                      <SvgXml xml={svg} width="100%" height="100%" />
                    </View>
                  ))}
                </View>
                <Text style={styles.widgetTitle}>위젯 분석 중</Text>
                <Text style={styles.widgetSubtitle}>영상 업로드 및 분석을 수행하고 있습니다...</Text>
                <TouchableOpacity style={styles.widgetButton} onPress={closeOverlay} activeOpacity={0.8} disabled={busy}>
                  <Text style={styles.widgetButtonText}>닫기</Text>
                </TouchableOpacity>
              </>
            ) : (
              <>
                <Text style={styles.widgetTitle}>분석 완료</Text>
                <Text style={styles.widgetPercentage}>{overlayPercentage}%</Text>
                <Text style={styles.widgetResult}>
                  {overlayResult === 'FAKE' ? '위험 확률이 높습니다.' : '위험 확률이 낮습니다.'}
                </Text>
                <TouchableOpacity style={styles.widgetButton} onPress={closeOverlay} activeOpacity={0.8}>
                  <Text style={styles.widgetButtonText}>닫기</Text>
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000', padding: 24, justifyContent: 'center' },
  title: { fontSize: 28, fontWeight: '700', color: '#fff', marginBottom: 8, textAlign: 'center' },
  subtitle: { fontSize: 16, color: '#9ca3af', textAlign: 'center', marginBottom: 32 },
  selectedBox: {
    borderRadius: 16,
    backgroundColor: '#111827',
    padding: 20,
    marginBottom: 24,
  },
  selectedLabel: { color: '#9ca3af', marginBottom: 6 },
  selectedPath: { color: '#fff' },
  primaryButton: {
    backgroundColor: '#ffc628',
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  primaryButtonText: { color: '#000', fontSize: 16, fontWeight: '700' },
  secondaryButton: {
    borderColor: '#ffc628',
    borderWidth: 2,
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
  },
  secondaryButtonDisabled: {
    opacity: 0.4,
  },
  secondaryButtonText: { color: '#ffc628', fontSize: 16, fontWeight: '700' },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  confirmCard: {
    backgroundColor: '#fff',
    borderRadius: 24,
    padding: 24,
    width: '100%',
  },
  confirmTitle: { fontSize: 20, fontWeight: '700', marginBottom: 12, color: '#111827' },
  confirmSubtitle: { fontSize: 16, color: '#4b5563', marginBottom: 24 },
  confirmButtons: { flexDirection: 'row', justifyContent: 'flex-end' },
  confirmButtonSpacing: { marginRight: 12 },
  confirmButton: {
    backgroundColor: '#ffc628',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 14,
  },
  confirmButtonText: { color: '#000', fontWeight: '700' },
  widgetOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  widgetCard: {
    backgroundColor: '#fff',
    borderRadius: 32,
    padding: 32,
    width: 320,
    alignItems: 'center',
  },
  loadingRow: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginBottom: 24 },
  loadingFrame: { marginHorizontal: 4, opacity: 0 },
  loadingFrameVisible: { opacity: 1 },
  loadingFrameHidden: { opacity: 0 },
  widgetTitle: { fontSize: 20, fontWeight: '700', color: '#111827', marginBottom: 8, textAlign: 'center' },
  widgetSubtitle: { fontSize: 15, color: '#4b5563', textAlign: 'center', marginBottom: 24 },
  widgetPercentage: { fontSize: 48, fontWeight: '800', color: '#111827', marginBottom: 12 },
  widgetResult: { fontSize: 16, color: '#4b5563', marginBottom: 24, textAlign: 'center' },
  widgetButton: {
    backgroundColor: '#ffc628',
    paddingVertical: 14,
    paddingHorizontal: 40,
    borderRadius: 20,
  },
  widgetButtonText: { color: '#000', fontWeight: '700', fontSize: 16 },
});
