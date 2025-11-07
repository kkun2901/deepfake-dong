// 유틸 함수들 정의 예정

export const formatNumber = (num: number) => new Intl.NumberFormat().format(num);

// Floating widget native bridge (safe optional access)
// Wraps Android native module; no-ops on unsupported platforms
import { NativeModules, Platform, NativeEventEmitter } from "react-native";

type FloatingWidgetModuleType = {
  checkOverlayPermission(): Promise<boolean>;
  requestOverlayPermission(): Promise<boolean>;
  startService(): Promise<void>;
  stopService(): Promise<void>;
  startRecording(): Promise<void>;
  stopRecording(): Promise<{ filePath: string } | null>;
  captureFrame(): Promise<{ filePath: string } | null>;
  updateUploadProgress(progress: number): Promise<void>;
  updateAnalyzing(): Promise<void>;
  updateAnalysisResult(
    result: string,
    deepfakePercentage: number,
    audioPercentage: number,
    videoId: string | null
  ): Promise<void>;
};

const maybeModule: Partial<FloatingWidgetModuleType> =
  (NativeModules as any)?.FloatingWidgetModule || {};

export const FloatingWidget = {
  async checkOverlayPermission(): Promise<boolean> {
    if (Platform.OS !== "android") {
      console.log("[FloatingWidget] checkOverlayPermission: Not Android, returning false");
      return false;
    }
    if (typeof maybeModule.checkOverlayPermission === "function") {
      try {
        console.log("[FloatingWidget] checkOverlayPermission: Calling native module");
        const result = await maybeModule.checkOverlayPermission();
        console.log("[FloatingWidget] checkOverlayPermission result:", result);
        return result;
      } catch (e) {
        console.error("[FloatingWidget] checkOverlayPermission error:", e);
        return false;
      }
    }
    console.warn("[FloatingWidget] checkOverlayPermission: Native module method not found");
    return false;
  },
  async requestOverlayPermission(): Promise<boolean> {
    if (Platform.OS !== "android") {
      console.log("[FloatingWidget] requestOverlayPermission: Not Android, returning false");
      return false;
    }
    if (typeof maybeModule.requestOverlayPermission === "function") {
      try {
        console.log("[FloatingWidget] requestOverlayPermission: Calling native module");
        const result = await maybeModule.requestOverlayPermission();
        console.log("[FloatingWidget] requestOverlayPermission result:", result);
        return result;
      } catch (e) {
        console.error("[FloatingWidget] requestOverlayPermission error:", e);
        return false;
      }
    }
    console.warn("[FloatingWidget] requestOverlayPermission: Native module method not found");
    return false;
  },
  async startService(): Promise<void> {
    if (Platform.OS !== "android") {
      console.log("[FloatingWidget] startService: Not Android, returning");
      return;
    }
    if (typeof maybeModule.startService === "function") {
      try {
        console.log("[FloatingWidget] startService: Calling native module");
        await maybeModule.startService();
        console.log("[FloatingWidget] startService: Success");
      } catch (e) {
        console.error("[FloatingWidget] startService error:", e);
        throw e;
      }
    } else {
      console.error("[FloatingWidget] startService: Native module method not found");
      throw new Error("startService method not available");
    }
  },
  async stopService(): Promise<void> {
    if (Platform.OS !== "android") return;
    if (typeof maybeModule.stopService === "function") {
      try {
        await maybeModule.stopService();
      } catch (e) {
        console.error("[FloatingWidget] stopService error:", e);
      }
    }
  },
  async startRecording(): Promise<void> {
    if (Platform.OS !== "android") return;
    if (typeof maybeModule.startRecording === "function") {
      try {
        await maybeModule.startRecording();
      } catch (e) {
        console.error("[FloatingWidget] startRecording error:", e);
        throw e;
      }
    }
  },
  async stopRecording(): Promise<{ filePath: string } | null> {
    if (Platform.OS !== "android") return null;
    if (typeof maybeModule.stopRecording === "function") {
      try {
        return await maybeModule.stopRecording();
      } catch (e) {
        console.error("[FloatingWidget] stopRecording error:", e);
        return null;
      }
    }
    return null;
  },
  async captureFrame(): Promise<{ filePath: string } | null> {
    if (Platform.OS !== "android") return null;
    if (typeof maybeModule.captureFrame === "function") {
      try {
        return await maybeModule.captureFrame();
      } catch (e) {
        console.error("[FloatingWidget] captureFrame error:", e);
        return null;
      }
    }
    return null;
  },
  async updateUploadProgress(progress: number): Promise<void> {
    if (Platform.OS !== "android") return;
    if (typeof maybeModule.updateUploadProgress === "function") {
      try {
        await maybeModule.updateUploadProgress(progress);
      } catch (e) {
        console.error("[FloatingWidget] updateUploadProgress error:", e);
      }
    }
  },
  async updateAnalyzing(): Promise<void> {
    if (Platform.OS !== "android") return;
    if (typeof maybeModule.updateAnalyzing === "function") {
      try {
        await maybeModule.updateAnalyzing();
      } catch (e) {
        console.error("[FloatingWidget] updateAnalyzing error:", e);
      }
    }
  },
  async updateAnalysisResult(
    result: string,
    deepfakePercentage: number,
    audioPercentage: number,
    videoId: string | null
  ): Promise<void> {
    if (Platform.OS !== "android") return;
    if (typeof maybeModule.updateAnalysisResult === "function") {
      try {
        await maybeModule.updateAnalysisResult(
          result,
          deepfakePercentage,
          audioPercentage,
          videoId
        );
      } catch (e) {
        console.error("[FloatingWidget] updateAnalysisResult error:", e);
      }
    }
  },
};

const widgetModule: any = (NativeModules as any)?.FloatingWidgetModule;

// NativeEventEmitter는 모듈이 없어도 생성 가능 (DeviceEventEmitter 사용)
// React Native의 기본 DeviceEventEmitter를 사용하여 더 안정적으로 이벤트 수신
export const FloatingWidgetEvents = Platform.OS === "android" && widgetModule
  ? new NativeEventEmitter(widgetModule)
  : Platform.OS === "android"
  ? new NativeEventEmitter() // 모듈 없이도 기본 이벤트 emitter 사용
  : null;

// 디버깅용 로그
if (Platform.OS === "android") {
  // 네이티브 모듈 로딩 확인을 위해 약간의 지연 후 확인
  setTimeout(() => {
    const allModules = Object.keys(NativeModules);
    const hasExpoGo = !!(NativeModules as any)?.ExpoGo;
    const isLikelyExpoGo = hasExpoGo || (__DEV__ && allModules.length < 5);
    const currentWidgetModule = (NativeModules as any)?.FloatingWidgetModule;
    
    console.log("[utils] FloatingWidgetEvents 초기화 (지연 확인):", {
      widgetModule: !!currentWidgetModule,
      widgetModuleType: typeof currentWidgetModule,
      hasAddListener: currentWidgetModule && typeof currentWidgetModule.addListener === "function",
      hasCheckPermission: currentWidgetModule && typeof currentWidgetModule.checkOverlayPermission === "function",
      hasStartService: currentWidgetModule && typeof currentWidgetModule.startService === "function",
      eventsInitialized: !!FloatingWidgetEvents,
      availableModules: allModules.filter(m => m.toLowerCase().includes('widget') || m.toLowerCase().includes('float')),
      allNativeModules: allModules.slice(0, 20), // 처음 20개만 표시
      hasExpoGo: hasExpoGo,
      isLikelyExpoGo: isLikelyExpoGo,
      nativeModulesCount: allModules.length,
    });
    
    if (!currentWidgetModule && allModules.length === 0) {
      console.error("[utils] 네이티브 모듈이 전혀 로드되지 않았습니다!");
      console.error("[utils] 이는 앱이 Expo Go에서 실행 중이거나, 네이티브 빌드가 제대로 되지 않았을 수 있습니다.");
      console.error("[utils] 해결 방법:");
      console.error("[utils] 1. npm run android (네이티브 빌드)");
      console.error("[utils] 2. 앱을 완전히 종료하고 다시 시작");
      console.error("[utils] 3. npx expo prebuild --clean 후 다시 빌드");
    } else if (!currentWidgetModule) {
      console.warn("[utils] FloatingWidgetModule이 로드되지 않았습니다.");
      console.warn("[utils] 하지만 다른 네이티브 모듈은 로드되었습니다:", allModules.slice(0, 10));
      console.warn("[utils] FloatingWidgetPackage가 MainApplication.kt에 등록되어 있는지 확인하세요.");
    }
  }, 1000); // 1초 후 확인
}

// 이벤트 타입 정의
export type RecordingCompleteEvent = {
  filePath: string;
  type: "recording";
};

export type CaptureCompleteEvent = {
  filePath: string;
  type: "capture";
};