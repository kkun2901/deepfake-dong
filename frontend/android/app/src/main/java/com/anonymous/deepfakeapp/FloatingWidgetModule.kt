package com.anonymous.deepfakeapp

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import com.facebook.react.bridge.*
import com.facebook.react.modules.core.DeviceEventManagerModule

class FloatingWidgetModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {
    
    private val reactContext: ReactApplicationContext = reactContext

    override fun getName(): String = "FloatingWidgetModule"
    
    // FloatingService에서 이벤트를 보낼 수 있도록 static 참조 제공
    companion object {
        @Volatile
        private var instance: FloatingWidgetModule? = null
        
               private const val REQUEST_OVERLAY_PERMISSION = 1001
               const val REQUEST_MEDIA_PROJECTION = 1002
               const val REQUEST_MEDIA_PROJECTION_CAPTURE = 1003
               const val REQUEST_MEDIA_PROJECTION_WITH_ANALYSIS = 1004
        
        fun getInstance(): FloatingWidgetModule? = instance
        
        fun sendRecordingCompleteEvent(context: ReactApplicationContext, filePath: String, autoStop: Boolean) {
            try {
                android.util.Log.d("FloatingWidgetModule", "sendRecordingCompleteEvent called: $filePath, autoStop=$autoStop")
                val params = Arguments.createMap().apply {
                    putString("filePath", filePath)
                    putString("type", "recording")
                    putBoolean("autoStop", autoStop)
                }
                
                // React Native가 완전히 준비될 때까지 여러 번 시도
                var attempts = 0
                val maxAttempts = 30
                val handler = android.os.Handler(android.os.Looper.getMainLooper())
                
                val tryEmit = object : Runnable {
                    override fun run() {
                        try {
                            val deviceEventEmitter = context.getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter::class.java)
                            deviceEventEmitter.emit("onRecordingComplete", params)
                            android.util.Log.d("FloatingWidgetModule", "✅ Recording complete event sent successfully: $filePath, autoStop=$autoStop")
                        } catch (e: Exception) {
                            android.util.Log.e("FloatingWidgetModule", "❌ Failed to send event (attempt ${attempts + 1}/$maxAttempts): ${e.message}")
                            attempts++
                            if (attempts < maxAttempts) {
                                handler.postDelayed(this, 200) // 200ms마다 재시도
                            } else {
                                android.util.Log.e("FloatingWidgetModule", "❌ Failed to send event after $maxAttempts attempts", e)
                                e.printStackTrace()
                            }
                        }
                    }
                }
                
                // 첫 시도는 약간의 딜레이 후
                handler.postDelayed(tryEmit, 500)
            } catch (e: Exception) {
                android.util.Log.e("FloatingWidgetModule", "Error in sendRecordingCompleteEvent", e)
                e.printStackTrace()
            }
        }
    }
    
    init {
        instance = this
    }

    @ReactMethod
    fun checkOverlayPermission(promise: Promise) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val hasPermission = Settings.canDrawOverlays(reactApplicationContext)
            promise.resolve(hasPermission)
        } else {
            promise.resolve(true)
        }
    }

    @ReactMethod
    fun requestOverlayPermission(promise: Promise) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val hasPermission = Settings.canDrawOverlays(reactApplicationContext)
            if (hasPermission) {
                promise.resolve(true)
                return
            }

            val currentActivity = currentActivity
            if (currentActivity == null) {
                promise.reject("NO_ACTIVITY", "No current activity")
                return
            }

            try {
                val intent = Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:${reactApplicationContext.packageName}")
                )
                currentActivity.startActivityForResult(intent, REQUEST_OVERLAY_PERMISSION, null)
                
                // Note: This is async - user will grant permission and return to app
                // Promise will be resolved when user comes back
                promise.resolve(false)
            } catch (e: Exception) {
                promise.reject("ERROR", "Failed to request overlay permission", e)
            }
        } else {
            promise.resolve(true)
        }
    }

    @ReactMethod
    fun startService(promise: Promise) {
        try {
            val intent = Intent(reactApplicationContext, FloatingService::class.java).apply {
                action = FloatingService.ACTION_START
            }
            
            // Android 8.0 이상에서는 foreground service로 시작해야 함
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                try {
                    reactApplicationContext.startForegroundService(intent)
                    android.util.Log.d("FloatingWidgetModule", "Foreground service started")
                } catch (e: Exception) {
                    android.util.Log.e("FloatingWidgetModule", "Failed to start foreground service, trying regular service", e)
                    reactApplicationContext.startService(intent)
                }
            } else {
                reactApplicationContext.startService(intent)
            }
            
            promise.resolve(null)
        } catch (e: Exception) {
            android.util.Log.e("FloatingWidgetModule", "Failed to start service", e)
            promise.reject("ERROR", "Failed to start service: ${e.message}", e)
        }
    }

    @ReactMethod
    fun stopService(promise: Promise) {
        try {
            val intent = Intent(reactApplicationContext, FloatingService::class.java).apply {
                action = FloatingService.ACTION_STOP
            }
            reactApplicationContext.stopService(intent)
            promise.resolve(null)
        } catch (e: Exception) {
            promise.reject("ERROR", "Failed to stop service", e)
        }
    }

    @ReactMethod
    fun startRecording(promise: Promise) {
        try {
            val currentActivity = currentActivity
            if (currentActivity == null) {
                promise.reject("NO_ACTIVITY", "No current activity")
                return
            }

            // MainActivity에서 ActivityResultLauncher를 사용하므로
            // MainActivity의 handleIntent를 통해 처리하도록 Intent 전달
            val intent = Intent(reactApplicationContext, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
                action = "START_RECORDING"
            }
            currentActivity.startActivity(intent)
            
            // Activity result를 저장할 임시 저장소
            pendingRecordingPromise = promise
        } catch (e: Exception) {
            promise.reject("ERROR", "Failed to start recording", e)
        }
    }
    
    fun onMediaProjectionResult(resultCode: Int, data: Intent?) {
        android.util.Log.d("FloatingWidgetModule", "onMediaProjectionResult called: resultCode=$resultCode, data=$data")
        
        val promise = pendingRecordingPromise ?: run {
            android.util.Log.e("FloatingWidgetModule", "pendingRecordingPromise is null!")
            return
        }
        pendingRecordingPromise = null
        
        try {
            if (resultCode == Activity.RESULT_OK && data != null) {
                android.util.Log.d("FloatingWidgetModule", "MediaProjection 권한 허용됨, FloatingService 시작")
                
                val intent = Intent(reactApplicationContext, FloatingService::class.java).apply {
                    action = FloatingService.ACTION_START_RECORDING
                    putExtra("resultCode", resultCode)
                    putExtra("resultData", data)
                }
                
                android.util.Log.d("FloatingWidgetModule", "Intent 생성: action=${intent.action}")
                
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    android.util.Log.d("FloatingWidgetModule", "startForegroundService 호출")
                    reactApplicationContext.startForegroundService(intent)
                } else {
                    android.util.Log.d("FloatingWidgetModule", "startService 호출")
                    reactApplicationContext.startService(intent)
                }
                
                android.util.Log.d("FloatingWidgetModule", "FloatingService 시작 완료, promise.resolve()")
                promise.resolve(null)
            } else {
                android.util.Log.w("FloatingWidgetModule", "MediaProjection 권한 취소됨: resultCode=$resultCode")
                promise.reject("USER_CANCELLED", "User cancelled media projection permission")
            }
        } catch (e: Exception) {
            android.util.Log.e("FloatingWidgetModule", "FloatingService 시작 실패", e)
            e.printStackTrace()
            promise.reject("ERROR", "Failed to start recording service", e)
        }
    }
    
    @ReactMethod
    fun captureFrame(promise: Promise) {
        try {
            val currentActivity = currentActivity
            if (currentActivity == null) {
                promise.reject("NO_ACTIVITY", "No current activity")
                return
            }

            // MainActivity에서 ActivityResultLauncher를 사용하므로
            // MainActivity의 handleIntent를 통해 처리하도록 Intent 전달
            val intent = Intent(reactApplicationContext, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
                action = "CAPTURE_FRAME"
            }
            currentActivity.startActivity(intent)
            
            pendingCapturePromise = promise
        } catch (e: Exception) {
            promise.reject("ERROR", "Failed to capture frame", e)
        }
    }
    
    fun onMediaProjectionResultForCapture(resultCode: Int, data: Intent?) {
        val promise = pendingCapturePromise ?: return
        pendingCapturePromise = null
        
        try {
            if (resultCode == Activity.RESULT_OK && data != null) {
                val intent = Intent(reactApplicationContext, FloatingService::class.java).apply {
                    action = FloatingService.ACTION_CAPTURE_FRAME
                    putExtra("resultCode", resultCode)
                    putExtra("resultData", data)
                }
                
                reactApplicationContext.startService(intent)
                promise.resolve(null)
            } else {
                promise.reject("USER_CANCELLED", "User cancelled media projection permission")
            }
        } catch (e: Exception) {
            promise.reject("ERROR", "Failed to capture frame", e)
        }
    }

    @ReactMethod
    fun stopRecording(promise: Promise) {
        try {
            val intent = Intent(reactApplicationContext, FloatingService::class.java).apply {
                action = FloatingService.ACTION_STOP_RECORDING
            }
            reactApplicationContext.startService(intent)
            promise.resolve(null)
        } catch (e: Exception) {
            promise.reject("ERROR", "Failed to stop recording", e)
        }
    }
    
    @ReactMethod
    fun updateUploadProgress(progress: Int, promise: Promise) {
        try {
            val intent = Intent(reactApplicationContext, FloatingService::class.java).apply {
                action = FloatingService.ACTION_UPDATE_UPLOADING
                putExtra("progress", progress)
            }
            reactApplicationContext.startService(intent)
            promise.resolve(null)
        } catch (e: Exception) {
            promise.reject("ERROR", "Failed to update upload progress", e)
        }
    }
    
    @ReactMethod
    fun updateAnalyzing(promise: Promise) {
        try {
            val intent = Intent(reactApplicationContext, FloatingService::class.java).apply {
                action = FloatingService.ACTION_UPDATE_ANALYZING
            }
            reactApplicationContext.startService(intent)
            promise.resolve(null)
        } catch (e: Exception) {
            promise.reject("ERROR", "Failed to update analyzing state", e)
        }
    }
    
    @ReactMethod
    fun updateAnalysisResult(
        result: String,
        deepfakePercentage: Int,
        audioPercentage: Int,
        videoId: String?,
        promise: Promise
    ) {
        try {
            val intent = Intent(reactApplicationContext, FloatingService::class.java).apply {
                action = FloatingService.ACTION_UPDATE_ANALYSIS_RESULT
                putExtra("result", result)
                putExtra("deepfakePercentage", deepfakePercentage)
                putExtra("audioPercentage", audioPercentage)
                if (videoId != null) {
                    putExtra("videoId", videoId)
                }
            }
            reactApplicationContext.startService(intent)
            promise.resolve(null)
        } catch (e: Exception) {
            promise.reject("ERROR", "Failed to update analysis result", e)
        }
    }
    
    // NativeEventEmitter를 위한 필수 메서드
    @ReactMethod
    fun addListener(eventName: String) {
        // 이벤트 리스너 추가 (필요한 경우 추가 로직 구현)
        // 현재는 DeviceEventManagerModule을 직접 사용하므로 빈 구현
    }

    @ReactMethod
    fun removeListeners(count: Int) {
        // 이벤트 리스너 제거 (필요한 경우 추가 로직 구현)
        // 현재는 DeviceEventManagerModule을 직접 사용하므로 빈 구현
    }
    
    private var pendingRecordingPromise: Promise? = null
    private var pendingCapturePromise: Promise? = null
    
    // MainActivity에서 pendingRecordingPromise 상태를 확인하기 위한 public 메서드
    fun hasPendingRecordingPromise(): Boolean {
        return pendingRecordingPromise != null
    }
}

