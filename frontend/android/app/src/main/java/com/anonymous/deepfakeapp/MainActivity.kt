package com.anonymous.deepfakeapp

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Bundle
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.result.ActivityResultLauncher

import com.facebook.react.ReactActivity
import com.facebook.react.ReactActivityDelegate
import com.facebook.react.defaults.DefaultNewArchitectureEntryPoint.fabricEnabled
import com.facebook.react.defaults.DefaultReactActivityDelegate

import expo.modules.ReactActivityDelegateWrapper

class MainActivity : ReactActivity() {
  private var mediaProjectionLauncher: ActivityResultLauncher<Intent>? = null
  private var mediaProjectionCaptureLauncher: ActivityResultLauncher<Intent>? = null
  private var mediaProjectionWithAnalysisLauncher: ActivityResultLauncher<Intent>? = null
  override fun onCreate(savedInstanceState: Bundle?) {
    // Set the theme to AppTheme BEFORE onCreate to support
    // coloring the background, status bar, and navigation bar.
    // This is required for expo-splash-screen.
    setTheme(R.style.AppTheme);
    
    // 위젯에서 녹화 시작 시 Activity를 투명하게 만들기
    val hideActivity = intent.getBooleanExtra("hideActivity", false)
    if (hideActivity) {
      // 투명 Activity로 만들기
      window.setFlags(
        android.view.WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
        android.view.WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
      )
      // Activity를 백그라운드로 유지
      moveTaskToBack(true)
    }
    
    // ActivityResultLauncher 초기화 (super.onCreate() 전에 호출해야 함)
    mediaProjectionLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
      handleMediaProjectionResult(result.resultCode, result.data, FloatingWidgetModule.REQUEST_MEDIA_PROJECTION)
      // 위젯에서 시작한 경우 권한 요청 후 Activity 종료
      if (intent.getBooleanExtra("hideActivity", false)) {
        finish()
      }
    }
    
    mediaProjectionCaptureLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
      handleMediaProjectionResult(result.resultCode, result.data, FloatingWidgetModule.REQUEST_MEDIA_PROJECTION_CAPTURE)
      if (intent.getBooleanExtra("hideActivity", false)) {
        finish()
      }
    }
    
    mediaProjectionWithAnalysisLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
      handleMediaProjectionResult(result.resultCode, result.data, FloatingWidgetModule.REQUEST_MEDIA_PROJECTION_WITH_ANALYSIS)
      if (intent.getBooleanExtra("hideActivity", false)) {
        finish()
      }
    }
    
    super.onCreate(null)
    
    // FloatingService에서 녹화 완료 후 MainActivity를 시작한 경우 처리
    val showRecordingComplete = intent.getBooleanExtra("showRecordingComplete", false)
    if (showRecordingComplete) {
      val filePath = intent.getStringExtra("filePath")
      val autoStop = intent.getBooleanExtra("autoStop", false)
      if (filePath != null) {
        // React Native로 녹화 완료 이벤트 전송
        sendRecordingCompleteToReactNative(filePath, autoStop)
      }
    }
    
    // FloatingService에서 녹화 시작을 위해 MainActivity를 시작한 경우
    handleIntent(intent)
  }
  
  private fun sendRecordingCompleteToReactNative(filePath: String, autoStop: Boolean) {
    try {
      val reactInstanceManager = (application as? com.facebook.react.ReactApplication)?.reactNativeHost?.reactInstanceManager
      val reactContext = reactInstanceManager?.currentReactContext as? com.facebook.react.bridge.ReactApplicationContext
      
      reactContext?.let {
        val params = com.facebook.react.bridge.Arguments.createMap().apply {
          putString("filePath", filePath)
          putString("type", "recording")
          putBoolean("autoStop", autoStop)
        }
        
        // React Native가 준비될 때까지 대기 후 이벤트 전송
        android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
          try {
            it.getJSModule(com.facebook.react.modules.core.DeviceEventManagerModule.RCTDeviceEventEmitter::class.java)
              .emit("onRecordingComplete", params)
            android.util.Log.d("MainActivity", "✅ Recording complete event sent to React Native: $filePath")
          } catch (e: Exception) {
            android.util.Log.e("MainActivity", "❌ Failed to send recording complete event", e)
          }
        }, 500)
      } ?: run {
        android.util.Log.e("MainActivity", "ReactContext is null, cannot send recording complete event")
      }
    } catch (e: Exception) {
      android.util.Log.e("MainActivity", "Error sending recording complete to React Native", e)
    }
  }
  
  override fun onNewIntent(intent: Intent?) {
    super.onNewIntent(intent)
    setIntent(intent)
    
    // FloatingService에서 녹화 완료 후 MainActivity를 시작한 경우 처리
    val showRecordingComplete = intent?.getBooleanExtra("showRecordingComplete", false) ?: false
    if (showRecordingComplete) {
      val filePath = intent?.getStringExtra("filePath")
      val autoStop = intent?.getBooleanExtra("autoStop", false) ?: false
      if (filePath != null) {
        // React Native로 녹화 완료 이벤트 전송
        sendRecordingCompleteToReactNative(filePath, autoStop)
      }
    }
    
    handleIntent(intent)
  }
  
  private fun handleIntent(intent: Intent?) {
    when (intent?.action) {
      "START_RECORDING" -> {
        android.util.Log.d("MainActivity", "handleIntent: START_RECORDING action received")
        val hideActivity = intent?.getBooleanExtra("hideActivity", false) ?: false
        
        // 위젯에서 시작한 경우 Activity를 백그라운드로 유지
        if (hideActivity) {
          moveTaskToBack(true)
        }
        
        // MediaProjection 권한 요청
        val mediaProjectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        val captureIntent = mediaProjectionManager.createScreenCaptureIntent()
        mediaProjectionLauncher?.launch(captureIntent)
        android.util.Log.d("MainActivity", "MediaProjection 권한 요청 시작: requestCode=${FloatingWidgetModule.REQUEST_MEDIA_PROJECTION}, hideActivity=$hideActivity")
      }
      "START_RECORDING_WITH_ANALYSIS" -> {
        android.util.Log.d("MainActivity", "handleIntent: START_RECORDING_WITH_ANALYSIS action received")
        // MediaProjection 권한 요청 (자동 분석 플래그 포함)
        val mediaProjectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        val captureIntent = mediaProjectionManager.createScreenCaptureIntent()
        mediaProjectionWithAnalysisLauncher?.launch(captureIntent)
        android.util.Log.d("MainActivity", "MediaProjection 권한 요청 시작 (자동 분석): requestCode=${FloatingWidgetModule.REQUEST_MEDIA_PROJECTION_WITH_ANALYSIS}")
      }
      "UPLOAD_VIDEO" -> {
        android.util.Log.d("MainActivity", "handleIntent: UPLOAD_VIDEO action received")
        // React Native 네비게이션으로 Upload 화면으로 이동
        // React Native 측에서 처리하도록 이벤트 전송
        val reactInstanceManager = (application as? com.facebook.react.ReactApplication)?.reactNativeHost?.reactInstanceManager
        val reactContext = reactInstanceManager?.currentReactContext as? com.facebook.react.bridge.ReactApplicationContext
        reactContext?.let {
          val params = com.facebook.react.bridge.Arguments.createMap().apply {
            putString("action", "UPLOAD_VIDEO")
          }
          it.getJSModule(com.facebook.react.modules.core.DeviceEventManagerModule.RCTDeviceEventEmitter::class.java)
            .emit("navigateToUpload", params)
        }
      }
      "VIEW_RESULT" -> {
        android.util.Log.d("MainActivity", "handleIntent: VIEW_RESULT action received")
        val videoId = intent.getStringExtra("videoId")
        // React Native 네비게이션으로 Result 화면으로 이동
        val reactInstanceManager = (application as? com.facebook.react.ReactApplication)?.reactNativeHost?.reactInstanceManager
        val reactContext = reactInstanceManager?.currentReactContext as? com.facebook.react.bridge.ReactApplicationContext
        reactContext?.let {
          val params = com.facebook.react.bridge.Arguments.createMap().apply {
            putString("action", "VIEW_RESULT")
            if (videoId != null) {
              putString("videoId", videoId)
            }
          }
          it.getJSModule(com.facebook.react.modules.core.DeviceEventManagerModule.RCTDeviceEventEmitter::class.java)
            .emit("navigateToResult", params)
        }
      }
      "CAPTURE_FRAME" -> {
        android.util.Log.d("MainActivity", "handleIntent: CAPTURE_FRAME action received")
        // MediaProjection 권한 요청
        val mediaProjectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        val captureIntent = mediaProjectionManager.createScreenCaptureIntent()
        mediaProjectionCaptureLauncher?.launch(captureIntent)
      }
    }
  }

  /**
   * Returns the name of the main component registered from JavaScript. This is used to schedule
   * rendering of the component.
   */
  override fun getMainComponentName(): String = "main"

  /**
   * Returns the instance of the [ReactActivityDelegate]. We use [DefaultReactActivityDelegate]
   * which allows you to enable New Architecture with a single boolean flags [fabricEnabled]
   */
  override fun createReactActivityDelegate(): ReactActivityDelegate {
    return ReactActivityDelegateWrapper(
          this,
          BuildConfig.IS_NEW_ARCHITECTURE_ENABLED,
          object : DefaultReactActivityDelegate(
              this,
              mainComponentName,
              fabricEnabled
          ){})
  }

  /**
    * Align the back button behavior with Android S
    * where moving root activities to background instead of finishing activities.
    * @see <a href="https://developer.android.com/reference/android/app/Activity#onBackPressed()">onBackPressed</a>
    */
  override fun invokeDefaultOnBackPressed() {
      if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.R) {
          if (!moveTaskToBack(false)) {
              // For non-root activities, use the default implementation to finish them.
              super.invokeDefaultOnBackPressed()
          }
          return
      }

      // Use the default back button implementation on Android S
      // because it's doing more than [Activity.moveTaskToBack] in fact.
      super.invokeDefaultOnBackPressed()
  }

  private fun handleMediaProjectionResult(resultCode: Int, data: Intent?, requestCode: Int) {
    android.util.Log.d("MainActivity", "handleMediaProjectionResult called: requestCode=$requestCode, resultCode=$resultCode")
    
    // FloatingWidgetModule의 MediaProjection 결과 처리
    val module = FloatingWidgetModule.getInstance()
    android.util.Log.d("MainActivity", "FloatingWidgetModule instance: ${module != null}")
    
    when (requestCode) {
      FloatingWidgetModule.REQUEST_MEDIA_PROJECTION -> {
        android.util.Log.d("MainActivity", "REQUEST_MEDIA_PROJECTION result received")
        
        // FloatingWidgetModule이 없거나 promise가 없는 경우, 직접 FloatingService로 전달
        // (위젯 버튼에서 직접 호출한 경우)
        if (module == null || !module.hasPendingRecordingPromise()) {
          android.util.Log.d("MainActivity", "FloatingWidgetModule이 없거나 promise가 없음, 직접 FloatingService로 전달")
          
            if (resultCode == Activity.RESULT_OK && data != null) {
            val serviceIntent = Intent(this, FloatingService::class.java).apply {
              action = FloatingService.ACTION_START_RECORDING
              putExtra("resultCode", resultCode)
              putExtra("resultData", data)
              putExtra("autoAnalyze", false)
            }
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
              startForegroundService(serviceIntent)
            } else {
              startService(serviceIntent)
            }
            android.util.Log.d("MainActivity", "FloatingService로 직접 전달 완료")
            
            // 위젯에서 시작한 경우 Activity를 백그라운드로 보내기
            if (intent.getBooleanExtra("hideActivity", false)) {
              moveTaskToBack(true)
            }
            return
          }
        }
        
        // React Native에서 호출한 경우 (정상 경로)
        if (module != null) {
          android.util.Log.d("MainActivity", "Calling onMediaProjectionResult (React Native 경로)")
          module.onMediaProjectionResult(resultCode, data)
        } else {
          android.util.Log.e("MainActivity", "FloatingWidgetModule instance is null!")
        }
      }
      FloatingWidgetModule.REQUEST_MEDIA_PROJECTION_CAPTURE -> {
        android.util.Log.d("MainActivity", "REQUEST_MEDIA_PROJECTION_CAPTURE result received")
        module?.onMediaProjectionResultForCapture(resultCode, data)
      }
      FloatingWidgetModule.REQUEST_MEDIA_PROJECTION_WITH_ANALYSIS -> {
        android.util.Log.d("MainActivity", "REQUEST_MEDIA_PROJECTION_WITH_ANALYSIS result received")
        if (resultCode == Activity.RESULT_OK && data != null) {
          val serviceIntent = Intent(this, FloatingService::class.java).apply {
            action = FloatingService.ACTION_START_RECORDING
            putExtra("resultCode", resultCode)
            putExtra("resultData", data)
            putExtra("autoAnalyze", true)
          }
          
          if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
          } else {
            startService(serviceIntent)
          }
        }
      }
      else -> {
        android.util.Log.d("MainActivity", "Unknown requestCode: $requestCode")
      }
    }
  }
}
