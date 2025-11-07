package com.anonymous.deepfakeapp

import android.app.*
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.Image
import android.media.ImageReader
import android.media.MediaRecorder
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.FrameLayout
import android.widget.Button
import androidx.core.app.NotificationCompat
import com.facebook.react.bridge.Arguments
import com.facebook.react.modules.core.DeviceEventManagerModule
import com.facebook.react.ReactApplication
import java.io.File
import java.io.FileOutputStream

class FloatingService : Service() {
    private var windowManager: WindowManager? = null
    private var floatingView: FrameLayout? = null
    private var recordButton: Button? = null  // 버튼 참조 저장
    private var isExpanded = false
    private var isRecording = false
    private var mediaProjection: MediaProjection? = null
    private var mediaProjectionManager: MediaProjectionManager? = null
    private var mediaRecorder: MediaRecorder? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var screenWidth = 0
    private var screenHeight = 0
    private var screenDensity = 0
    private var recordingFile: File? = null
    private var recordingHandler: android.os.Handler? = null
    private val MAX_RECORDING_DURATION_MS = 15_000L // 15초
    private var recordActionInProgress: Boolean = false
    
    companion object {
        // Service Actions
        const val ACTION_START = "com.anonymous.deepfakeapp.START"
        const val ACTION_STOP = "com.anonymous.deepfakeapp.STOP"
        const val ACTION_TOGGLE_MENU = "com.anonymous.deepfakeapp.TOGGLE_MENU"
        const val ACTION_START_RECORDING = "com.anonymous.deepfakeapp.START_RECORDING"
        const val ACTION_STOP_RECORDING = "com.anonymous.deepfakeapp.STOP_RECORDING"
        const val ACTION_CAPTURE_FRAME = "com.anonymous.deepfakeapp.CAPTURE_FRAME"
        
        // Notification
        const val CHANNEL_ID = "floating_widget_channel"
        const val NOTIFICATION_ID = 1001
    }

    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        mediaProjectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        createNotificationChannel()
        
        val metrics = resources.displayMetrics
        screenWidth = metrics.widthPixels
        screenHeight = metrics.heightPixels
        screenDensity = metrics.densityDpi
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> {
                android.util.Log.d("FloatingService", "=== ACTION_START 처리 시작 ===")
                // 위젯 표시를 먼저 수행 (foreground service보다 우선)
                android.util.Log.d("FloatingService", "showFloatingWidget() 호출")
                showFloatingWidget()
                android.util.Log.d("FloatingService", "showFloatingWidget() 완료")
                
                // Foreground service는 위젯 표시 후에 시도 (권한이 없어도 위젯은 이미 표시됨)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    try {
                        // Android 14+에서는 foregroundServiceType을 명시해야 하지만,
                        // 권한이 없어도 위젯은 이미 표시되었으므로 시도만 함
                        startForeground(NOTIFICATION_ID, createNotification())
                        android.util.Log.d("FloatingService", "Foreground service started for ACTION_START")
                    } catch (e: Exception) {
                        android.util.Log.w("FloatingService", "Foreground service 시작 실패 (권한 없음), 하지만 위젯은 이미 표시됨", e)
                        // 위젯은 이미 표시되었으므로 계속 진행
                    }
                }
            }
            ACTION_STOP -> {
                stopFloatingWidget()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
            ACTION_TOGGLE_MENU -> {
                toggleMenu()
            }
            ACTION_START_RECORDING -> {
                android.util.Log.d("FloatingService", "=== ACTION_START_RECORDING received ===")
                android.util.Log.d("FloatingService", "Intent: $intent")
                android.util.Log.d("FloatingService", "Current isRecording state: $isRecording")
                android.util.Log.d("FloatingService", "Current mediaProjection state: $mediaProjection")
                
                // Foreground service로 시작 (Android 14+ 필수)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    try {
                        startForeground(NOTIFICATION_ID, createNotification())
                        android.util.Log.d("FloatingService", "Foreground service started")
                    } catch (e: Exception) {
                        android.util.Log.e("FloatingService", "Failed to start foreground service", e)
                        e.printStackTrace()
                    }
                }
                
                startScreenRecording(intent)
            }
            ACTION_STOP_RECORDING -> {
                stopScreenRecording()
            }
            ACTION_CAPTURE_FRAME -> {
                captureFrame(intent)
            }
        }
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Floating Widget Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Floating widget service is running"
                setShowBadge(false)
            }
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        // Android 14+에서는 foregroundServiceType을 명시해야 함
        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Floating Widget")
            .setContentText("위젯이 실행 중입니다")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setOngoing(true)
        
        // Android 14+ (API 34+)에서는 foregroundServiceType 설정
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            builder.setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
        }
        
        return builder.build()
    }

    private fun showFloatingWidget() {
        try {
            android.util.Log.d("FloatingService", "=== showFloatingWidget() 시작 ===")
            
            if (floatingView != null) {
                android.util.Log.w("FloatingService", "floatingView가 이미 존재함, 반환")
                return
            }

            if (windowManager == null) {
                android.util.Log.e("FloatingService", "windowManager가 null입니다!")
                return
            }

            android.util.Log.d("FloatingService", "위젯 뷰 생성 시작")

        // Create container
        floatingView = FrameLayout(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.WRAP_CONTENT,
                FrameLayout.LayoutParams.WRAP_CONTENT
            )
        }

        // Create main button
        val mainButton = View(this).apply {
            val size = (60 * resources.displayMetrics.density).toInt()
            layoutParams = FrameLayout.LayoutParams(size, size).apply {
                gravity = Gravity.CENTER
            }
            setBackgroundColor(Color.parseColor("#2563eb")) // 파란색
            elevation = 8f
            // 둥근 모서리
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                clipToOutline = true
            }
        }

        // Create menu container
        val menuContainer = FrameLayout(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.WRAP_CONTENT,
                FrameLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                gravity = Gravity.CENTER
            }
            visibility = View.GONE
            alpha = 0f
        }

        // Create menu buttons
        recordButton = Button(this).apply {
            text = "녹화"
            textSize = 10f
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.parseColor("#10b981"))
            val size = (50 * resources.displayMetrics.density).toInt()
            layoutParams = FrameLayout.LayoutParams(size, size).apply {
                gravity = Gravity.CENTER_HORIZONTAL or Gravity.TOP
                bottomMargin = (80 * resources.displayMetrics.density).toInt()
            }
            elevation = 6f
            tag = "record_btn"
            setOnClickListener {
                if (recordActionInProgress) return@setOnClickListener
                recordActionInProgress = true
                toggleMenu()
                if (isRecording) {
                    // 녹화 중지
                    stopScreenRecording(false)
                } else {
                    // MainActivity로 이동하여 MediaProjection 권한 요청 (매번 요청)
                    val intent = Intent(this@FloatingService, MainActivity::class.java).apply {
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK
                        action = "START_RECORDING"
                    }
                    startActivity(intent)
                }
                // 짧은 디바운스: 연타/전환 중복 방지
                android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                    recordActionInProgress = false
                }, 700)
            }
        }
        val recordBtn = recordButton!!

        val captureBtn = Button(this).apply {
            text = "캡처"
            textSize = 10f
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.parseColor("#10b981"))
            val size = (50 * resources.displayMetrics.density).toInt()
            layoutParams = FrameLayout.LayoutParams(size, size).apply {
                gravity = Gravity.CENTER_VERTICAL or Gravity.START
                marginEnd = (80 * resources.displayMetrics.density).toInt()
            }
            elevation = 6f
            setOnClickListener {
                toggleMenu()
                // MainActivity로 이동하여 MediaProjection 권한 요청
                val intent = Intent(this@FloatingService, MainActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK
                    action = "CAPTURE_FRAME"
                }
                startActivity(intent)
            }
        }

        val exitBtn = Button(this).apply {
            text = "종료"
            textSize = 10f
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.parseColor("#10b981"))
            val size = (50 * resources.displayMetrics.density).toInt()
            layoutParams = FrameLayout.LayoutParams(size, size).apply {
                gravity = Gravity.CENTER_VERTICAL or Gravity.END
                marginStart = (80 * resources.displayMetrics.density).toInt()
            }
            elevation = 6f
            setOnClickListener {
                stopSelf()
            }
        }

        // Add menu buttons to container
        menuContainer.addView(recordBtn)
        menuContainer.addView(captureBtn)
        menuContainer.addView(exitBtn)

        // Add views
        floatingView!!.addView(mainButton)
        floatingView!!.addView(menuContainer)

        // Set click listener
        mainButton.setOnClickListener { toggleMenu() }

        // Store menu container reference
        menuContainer.tag = "menu_container"

        val layoutParams = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
            } else {
                WindowManager.LayoutParams.TYPE_PHONE
            },
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 100
            y = 300
        }

        setupDragHandler(mainButton)
        
        try {
            android.util.Log.d("FloatingService", "WindowManager에 뷰 추가 시도...")
            android.util.Log.d("FloatingService", "LayoutParams: type=${layoutParams.type}, flags=${layoutParams.flags}")
            android.util.Log.d("FloatingService", "위치: x=${layoutParams.x}, y=${layoutParams.y}")
            
            windowManager?.addView(floatingView, layoutParams)
            android.util.Log.d("FloatingService", "✅ 위젯 뷰가 성공적으로 추가되었습니다!")
            android.util.Log.d("FloatingService", "플로팅 버튼이 화면에 표시되어야 합니다")
        } catch (e: Exception) {
            android.util.Log.e("FloatingService", "❌ 위젯 뷰 추가 실패", e)
            e.printStackTrace()
            
            // 권한 오류인 경우
            if (e.message?.contains("permission") == true || e.message?.contains("SYSTEM_ALERT_WINDOW") == true) {
                android.util.Log.e("FloatingService", "SYSTEM_ALERT_WINDOW 권한이 필요합니다!")
                try {
                    android.widget.Toast.makeText(this, "다른 앱 위에 표시 권한이 필요합니다", android.widget.Toast.LENGTH_LONG).show()
                } catch (toastEx: Exception) {
                    // Toast 실패는 무시
                }
            }
            
            floatingView = null
        }
        } catch (e: Exception) {
            android.util.Log.e("FloatingService", "showFloatingWidget() 전체 오류", e)
            e.printStackTrace()
            floatingView = null
        }
    }

    private fun setupDragHandler(mainButton: View) {
        mainButton.setOnTouchListener(object : View.OnTouchListener {
            private var initialX = 0
            private var initialY = 0
            private var initialTouchX = 0f
            private var initialTouchY = 0f

            override fun onTouch(v: View, event: MotionEvent): Boolean {
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        val params = floatingView?.layoutParams as? WindowManager.LayoutParams
                        params?.let {
                            initialX = it.x
                            initialY = it.y
                            initialTouchX = event.rawX
                            initialTouchY = event.rawY
                        }
                    }
                    MotionEvent.ACTION_MOVE -> {
                        val params = floatingView?.layoutParams as? WindowManager.LayoutParams
                        params?.let {
                            it.x = initialX + (event.rawX - initialTouchX).toInt()
                            it.y = initialY + (event.rawY - initialTouchY).toInt()
                            windowManager?.updateViewLayout(floatingView, it)
                        }
                    }
                }
                return false
            }
        })
    }

    private fun toggleMenu() {
        val menuContainer = floatingView?.findViewWithTag<FrameLayout>("menu_container") ?: return
        isExpanded = !isExpanded
        
        if (isExpanded) {
            menuContainer.visibility = View.VISIBLE
            menuContainer.animate()
                .alpha(1f)
                .setDuration(200)
                .start()
        } else {
            menuContainer.animate()
                .alpha(0f)
                .setDuration(200)
                .withEndAction {
                    menuContainer.visibility = View.GONE
                }
                .start()
        }
    }

    private fun stopFloatingWidget() {
        floatingView?.let {
            windowManager?.removeView(it)
            floatingView = null
        }
        recordButton = null  // 버튼 참조도 초기화
    }

    override fun onDestroy() {
        super.onDestroy()
        stopFloatingWidget()
    }

    private fun startScreenRecording(intent: Intent?) {
        android.util.Log.d("FloatingService", "startScreenRecording called, intent: $intent")
        
        if (mediaProjection != null || isRecording) {
            android.util.Log.w("FloatingService", "Already recording or mediaProjection exists")
            return
        }

        try {
            val resultCode = intent?.getIntExtra("resultCode", Activity.RESULT_CANCELED) ?: Activity.RESULT_CANCELED
            android.util.Log.d("FloatingService", "resultCode: $resultCode")
            
            val resultData = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                intent?.getParcelableExtra("resultData", Intent::class.java)
            } else {
                @Suppress("DEPRECATION")
                intent?.getParcelableExtra<Intent>("resultData")
            }
            
            android.util.Log.d("FloatingService", "resultData: $resultData, resultCode OK: ${resultCode == Activity.RESULT_OK}")
            
            // Foreground service가 시작된 상태에서 MediaProjection 생성 (Android 14+ 필수)
            if (resultCode == Activity.RESULT_OK && resultData != null) {
                android.util.Log.d("FloatingService", "Creating MediaProjection in Service (foreground service running)")
                try {
                    mediaProjection = mediaProjectionManager?.getMediaProjection(resultCode, resultData)
                    
                    // Android 14+ (API 34+)에서는 callback 등록 필수
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE && mediaProjection != null) {
                        mediaProjection!!.registerCallback(object : MediaProjection.Callback() {
                            override fun onStop() {
                                android.util.Log.d("FloatingService", "MediaProjection stopped")
                                if (isRecording) {
                                    stopScreenRecording(false)
                                }
                                mediaProjection = null
                            }
                        }, android.os.Handler(android.os.Looper.getMainLooper()))
                        android.util.Log.d("FloatingService", "MediaProjection callback registered")
                    }
                    
                    android.util.Log.d("FloatingService", "MediaProjection created successfully")
                } catch (e: Exception) {
                    android.util.Log.e("FloatingService", "Failed to create MediaProjection in Service", e)
                    e.printStackTrace()
                    return
                }
            }
            
            if (mediaProjection != null) {
                android.util.Log.d("FloatingService", "Starting screen recording...")
                
                // 녹화 파일 생성
                val outputDir = File(getExternalFilesDir(null), "recordings")
                if (!outputDir.exists()) {
                    outputDir.mkdirs()
                    android.util.Log.d("FloatingService", "녹화 디렉토리 생성: ${outputDir.absolutePath}")
                }
                recordingFile = File(outputDir, "recording_${System.currentTimeMillis()}.mp4")
                android.util.Log.d("FloatingService", "녹화 파일 경로: ${recordingFile?.absolutePath}")
                
                // MediaRecorder 설정 (오디오 없이 비디오만)
                mediaRecorder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                    MediaRecorder(this)
                } else {
                    @Suppress("DEPRECATION")
                    MediaRecorder()
                }.apply {
                    try {
                        // 오디오 없이 비디오만 녹화 (에뮬레이터 호환성)
                        setVideoSource(MediaRecorder.VideoSource.SURFACE)
                        setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                        setOutputFile(recordingFile!!.absolutePath)
                        setVideoEncoder(MediaRecorder.VideoEncoder.H264)
                        
                        // 해상도와 비트레이트를 에뮬레이터에 맞게 조정
                        val width = minOf(screenWidth, 1280)
                        val height = minOf(screenHeight, 720)
                        setVideoSize(width, height)
                        setVideoEncodingBitRate(2 * 1000 * 1000) // 2Mbps로 낮춤
                        setVideoFrameRate(24) // 24fps로 낮춤
                        
                        android.util.Log.d("FloatingService", "MediaRecorder configured: ${width}x${height}, bitrate=2Mbps, fps=24")
                        
                        try {
                            prepare()
                            android.util.Log.d("FloatingService", "MediaRecorder prepared successfully")
                        } catch (e: Exception) {
                            android.util.Log.e("FloatingService", "Failed to prepare MediaRecorder: ${e.message}", e)
                            e.printStackTrace()
                            release()
                            mediaRecorder = null
                            
                            // 에러를 사용자에게 알림
                            try {
                                android.widget.Toast.makeText(this@FloatingService, "녹화 준비 실패: ${e.message}", android.widget.Toast.LENGTH_LONG).show()
                            } catch (toastEx: Exception) {
                                // Toast 실패는 무시
                            }
                            return
                        }
                    } catch (e: Exception) {
                        android.util.Log.e("FloatingService", "Failed to configure MediaRecorder: ${e.message}", e)
                        e.printStackTrace()
                        release()
                        mediaRecorder = null
                        return
                    }
                }
                
                val surface = mediaRecorder?.surface
                virtualDisplay = mediaProjection?.createVirtualDisplay(
                    "ScreenCapture",
                    screenWidth, screenHeight, screenDensity,
                    DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                    surface, null, null
                )
                
                mediaRecorder?.start()
                isRecording = true
                android.util.Log.d("FloatingService", "=== RECORDING STARTED SUCCESSFULLY ===")
                android.util.Log.d("FloatingService", "Recording file: ${recordingFile?.absolutePath}")
                android.util.Log.d("FloatingService", "VirtualDisplay created: ${virtualDisplay != null}")
                android.util.Log.d("FloatingService", "MediaRecorder started: ${mediaRecorder != null}")
                android.util.Log.d("FloatingService", "isRecording set to: $isRecording")
                
                // 메인 스레드에서 버튼 업데이트 (UI 업데이트는 메인 스레드에서만 가능)
                android.os.Handler(android.os.Looper.getMainLooper()).post {
                    android.util.Log.d("FloatingService", "Updating record button to recording state (메인 스레드)")
                    updateRecordButton(true)
                    android.util.Log.d("FloatingService", "Record button updated")
                }
                
                // 녹화 시작 확인을 위한 Toast 메시지 (선택사항)
                try {
                    android.widget.Toast.makeText(this, "녹화가 시작되었습니다", android.widget.Toast.LENGTH_SHORT).show()
                } catch (e: Exception) {
                    // Toast 실패는 무시
                }
                
                // 15초 후 자동 종료 타이머 설정
                recordingHandler = android.os.Handler(android.os.Looper.getMainLooper())
                recordingHandler?.postDelayed({
                    if (isRecording) {
                        android.util.Log.d("FloatingService", "15초 타이머 만료 - 자동 종료")
                        // 자동 종료 알림 표시 (Notification + Toast)
                        try {
                            // Notification으로도 알림 표시 (더 확실함)
                            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
                            val notification = NotificationCompat.Builder(this, CHANNEL_ID)
                                .setContentTitle("녹화 완료")
                                .setContentText("15초 자동 종료되었습니다")
                                .setSmallIcon(android.R.drawable.ic_dialog_info)
                                .setAutoCancel(true)
                                .build()
                            notificationManager.notify(NOTIFICATION_ID + 1, notification)
                            
                            // Toast도 표시 (UI 스레드에서)
                            android.os.Handler(android.os.Looper.getMainLooper()).post {
                                try {
                                    android.widget.Toast.makeText(this@FloatingService, "녹화가 완료되었습니다 (15초 자동 종료)", android.widget.Toast.LENGTH_LONG).show()
                                } catch (e: Exception) {
                                    android.util.Log.e("FloatingService", "Toast 표시 실패", e)
                                }
                            }
                        } catch (e: Exception) {
                            android.util.Log.e("FloatingService", "알림 표시 실패", e)
                        }
                        stopScreenRecording(true) // autoStop = true로 전달
                    }
                }, MAX_RECORDING_DURATION_MS)
            } else {
                android.util.Log.e("FloatingService", "=== FAILED TO START RECORDING ===")
                android.util.Log.e("FloatingService", "Reason: mediaProjection is null")
                android.util.Log.e("FloatingService", "resultCode: $resultCode (OK=${resultCode == Activity.RESULT_OK})")
                android.util.Log.e("FloatingService", "resultData: $resultData")
            }
        } catch (e: Exception) {
            android.util.Log.e("FloatingService", "Error starting recording", e)
            e.printStackTrace()
            stopScreenRecording(false)
        }
    }

    private fun stopScreenRecording(autoStop: Boolean = false) {
        try {
            // 타이머 취소
            recordingHandler?.removeCallbacksAndMessages(null)
            recordingHandler = null
            
            virtualDisplay?.release()
            virtualDisplay = null
            
            mediaRecorder?.apply {
                try {
                    stop()
                } catch (e: Exception) {
                    e.printStackTrace()
                }
                release()
            }
            mediaRecorder = null
            
            mediaProjection?.stop()
            mediaProjection = null
            
            isRecording = false
            
            // 메인 스레드에서 버튼 업데이트
            android.os.Handler(android.os.Looper.getMainLooper()).post {
                android.util.Log.d("FloatingService", "Updating record button to stopped state (메인 스레드)")
                updateRecordButton(false)
            }
            
            // 녹화 완료 이벤트 전송
            recordingFile?.let { file ->
                android.util.Log.d("FloatingService", "=== 녹화 완료 처리 시작 ===")
                android.util.Log.d("FloatingService", "파일 경로: ${file.absolutePath}")
                android.util.Log.d("FloatingService", "파일 존재: ${file.exists()}")
                android.util.Log.d("FloatingService", "파일 크기: ${file.length()} bytes")
                android.util.Log.d("FloatingService", "autoStop: $autoStop")
                
                if (file.exists() && file.length() > 0) {
                    // 자동 종료가 아닐 때만 추가 알림 표시 (자동 종료는 이미 Toast 표시함)
                    if (!autoStop) {
                        try {
                            android.widget.Toast.makeText(this@FloatingService, "녹화가 완료되었습니다", android.widget.Toast.LENGTH_SHORT).show()
                        } catch (e: Exception) {
                            // Toast 실패는 무시
                        }
                    }
                    android.util.Log.d("FloatingService", "이벤트 전송 시작: ${file.absolutePath}")
                    sendRecordingCompleteEvent(file.absolutePath, autoStop)
                    android.util.Log.d("FloatingService", "이벤트 전송 완료")
                } else {
                    android.util.Log.e("FloatingService", "녹화 파일이 존재하지 않거나 비어있음")
                    file.delete()
                    // 파일이 비어있으면 에러 알림
                    try {
                        android.widget.Toast.makeText(this@FloatingService, "녹화 파일 생성 실패", android.widget.Toast.LENGTH_SHORT).show()
                    } catch (e: Exception) {
                        // Toast 실패는 무시
                    }
                }
            } ?: run {
                android.util.Log.e("FloatingService", "recordingFile이 null입니다")
            }
            recordingFile = null
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun captureFrame(intent: Intent?) {
        try {
            val resultCode = intent?.getIntExtra("resultCode", Activity.RESULT_CANCELED) ?: return
            val resultData = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                intent?.getParcelableExtra("resultData", Intent::class.java)
            } else {
                @Suppress("DEPRECATION")
                intent?.getParcelableExtra<Intent>("resultData")
            }
            
            if (resultCode != Activity.RESULT_OK || resultData == null) {
                return
            }
            
            val captureProjection = mediaProjectionManager?.getMediaProjection(resultCode, resultData) ?: return
            
            // 화면 캡처를 위한 ImageReader 생성
            val imageReader = ImageReader.newInstance(screenWidth, screenHeight, PixelFormat.RGBA_8888, 1)
            
            // VirtualDisplay 생성
            val captureDisplay = captureProjection.createVirtualDisplay(
                "ScreenCapture",
                screenWidth, screenHeight, screenDensity,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                imageReader.surface, null, null
            )
            
            imageReader.setOnImageAvailableListener({ reader ->
                val image = reader.acquireLatestImage()
                image?.let {
                    val planes = it.planes
                    val buffer = planes[0].buffer
                    val pixelStride = planes[0].pixelStride
                    val rowStride = planes[0].rowStride
                    val rowPadding = rowStride - pixelStride * screenWidth
                    
                    val bitmap = Bitmap.createBitmap(
                        screenWidth + rowPadding / pixelStride,
                        screenHeight,
                        Bitmap.Config.ARGB_8888
                    )
                    bitmap.copyPixelsFromBuffer(buffer)
                    
                    // 정확한 크기로 자르기
                    val finalBitmap = Bitmap.createBitmap(bitmap, 0, 0, screenWidth, screenHeight)
                    bitmap.recycle()
                    
                    // 파일로 저장
                    val outputDir = File(getExternalFilesDir(null), "captures")
                    if (!outputDir.exists()) {
                        outputDir.mkdirs()
                    }
                    val captureFile = File(outputDir, "capture_${System.currentTimeMillis()}.png")
                    FileOutputStream(captureFile).use { out ->
                        finalBitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
                    }
                    finalBitmap.recycle()
                    
                    // 이벤트 전송
                    sendCaptureCompleteEvent(captureFile.absolutePath)
                    
                    // 정리
                    captureDisplay.release()
                    captureProjection.stop()
                    imageReader.close()
                    it.close()
                }
            }, android.os.Handler(android.os.Looper.getMainLooper()))
            
            // 잠시 후 캡처 (화면이 렌더링될 시간을 줌)
            android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                try {
                    captureDisplay.release()
                } catch (e: Exception) {
                    e.printStackTrace()
                }
                captureProjection.stop()
                imageReader.close()
            }, 1000)
            
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    private fun updateRecordButton(recording: Boolean) {
        android.util.Log.d("FloatingService", "updateRecordButton called: recording=$recording")
        android.util.Log.d("FloatingService", "floatingView is null: ${floatingView == null}")
        android.util.Log.d("FloatingService", "recordButton stored reference is null: ${recordButton == null}")
        
        // 저장된 참조를 먼저 시도
        val recordBtn = recordButton ?: floatingView?.findViewWithTag<Button>("record_btn")
        android.util.Log.d("FloatingService", "recordBtn found: ${recordBtn != null}")
        
        if (recordBtn != null) {
            val newText = if (recording) "녹화 중지" else "녹화"
            val newColor = if (recording) "#dc2626" else "#10b981"
            
            android.util.Log.d("FloatingService", "Updating button: text='$newText', color=$newColor")
            
            // 메인 스레드에서 실행 확인 (이미 메인 스레드에서 호출되지만 안전을 위해)
            recordBtn.post {
                recordBtn.text = newText
                recordBtn.setBackgroundColor(Color.parseColor(newColor))
                android.util.Log.d("FloatingService", "Button updated successfully: text='${recordBtn.text}', color applied")
            }
        } else {
            android.util.Log.e("FloatingService", "recordBtn not found! floatingView=$floatingView, recordButton=$recordButton")
            // 버튼을 다시 찾아서 저장 시도
            floatingView?.let { view ->
                val foundBtn = view.findViewWithTag<Button>("record_btn")
                if (foundBtn != null) {
                    android.util.Log.d("FloatingService", "Found button on retry, storing reference")
                    recordButton = foundBtn
                    updateRecordButton(recording)  // 재귀 호출로 다시 시도
                }
            }
        }
    }
    
    private fun sendRecordingCompleteEvent(filePath: String, autoStop: Boolean = false) {
        try {
            android.util.Log.d("FloatingService", "sendRecordingCompleteEvent called: $filePath, autoStop=$autoStop")
            
            val app = applicationContext as? ReactApplication
            val reactInstanceManager = app?.reactNativeHost?.reactInstanceManager
            
            // React Native 컨텍스트가 준비될 때까지 대기
            var reactContext: com.facebook.react.bridge.ReactApplicationContext? = null
            var attempts = 0
            while (reactContext == null && attempts < 10) {
                reactContext = reactInstanceManager?.currentReactContext as? com.facebook.react.bridge.ReactApplicationContext
                if (reactContext == null) {
                    android.util.Log.d("FloatingService", "ReactContext not ready, waiting... (attempt ${attempts + 1}/10)")
                    Thread.sleep(100)
                    attempts++
                }
            }
            
            if (reactContext != null) {
                android.util.Log.d("FloatingService", "ReactContext found, sending event via FloatingWidgetModule")
                FloatingWidgetModule.sendRecordingCompleteEvent(reactContext, filePath, autoStop)
            } else {
                android.util.Log.e("FloatingService", "ReactContext is null after waiting, trying alternative method")
                // 대안: 직접 이벤트 전송 시도
                reactContext = reactInstanceManager?.currentReactContext as? com.facebook.react.bridge.ReactApplicationContext
                reactContext?.let {
                    val params = Arguments.createMap().apply {
                        putString("filePath", filePath)
                        putString("type", "recording")
                        putBoolean("autoStop", autoStop)
                    }
                    android.os.Handler(android.os.Looper.getMainLooper()).post {
                        try {
                            it.getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter::class.java)
                                .emit("onRecordingComplete", params)
                            android.util.Log.d("FloatingService", "Recording complete event sent directly: $filePath")
                        } catch (e: Exception) {
                            android.util.Log.e("FloatingService", "Failed to send recording complete event directly", e)
                            e.printStackTrace()
                        }
                    }
                }
            }
            
            // 앱을 포그라운드로 가져오기 (Alert를 보이기 위해)
            // 이벤트를 먼저 전송한 후 앱을 포그라운드로 가져옴
            android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                try {
                    val intent = Intent(this, MainActivity::class.java).apply {
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
                        putExtra("showRecordingComplete", true)
                        putExtra("filePath", filePath)
                        putExtra("autoStop", autoStop)
                    }
                    startActivity(intent)
                    android.util.Log.d("FloatingService", "MainActivity brought to foreground (after event sent)")
                } catch (e: Exception) {
                    android.util.Log.e("FloatingService", "Failed to bring MainActivity to foreground", e)
                    e.printStackTrace()
                }
            }, 500) // 이벤트 전송 후 500ms 대기
        } catch (e: Exception) {
            android.util.Log.e("FloatingService", "Error in sendRecordingCompleteEvent", e)
            e.printStackTrace()
        }
    }
    
    private fun sendCaptureCompleteEvent(filePath: String) {
        try {
            val app = applicationContext as? ReactApplication
            val reactContext = app?.reactNativeHost?.reactInstanceManager?.currentReactContext as? com.facebook.react.bridge.ReactApplicationContext
            reactContext?.let {
                val params = Arguments.createMap().apply {
                    putString("filePath", filePath)
                    putString("type", "capture")
                }
                it.getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter::class.java)
                    .emit("onCaptureComplete", params)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

}

