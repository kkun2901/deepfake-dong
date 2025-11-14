package com.anonymous.deepfakeapp

import android.app.*
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
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
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.TextView
import android.graphics.drawable.BitmapDrawable
import java.io.InputStream
import androidx.core.app.NotificationCompat
import com.facebook.react.bridge.Arguments
import com.facebook.react.modules.core.DeviceEventManagerModule
import com.facebook.react.ReactApplication
import java.io.File
import java.io.FileOutputStream
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException

class FloatingService : Service() {
    // 플로팅 위젯 관련 변수
    private var windowManager: WindowManager? = null
    private var floatingView: FrameLayout? = null
    private var recordButton: ImageButton? = null
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
        const val ACTION_RECORD_FROM_NOTIFICATION = "com.anonymous.deepfakeapp.RECORD_FROM_NOTIFICATION"
        const val ACTION_CAPTURE_FROM_NOTIFICATION = "com.anonymous.deepfakeapp.CAPTURE_FROM_NOTIFICATION"
        const val ACTION_UPLOAD_FROM_NOTIFICATION = "com.anonymous.deepfakeapp.UPLOAD_FROM_NOTIFICATION"
        const val ACTION_VIDEO_RECORD_FROM_NOTIFICATION = "com.anonymous.deepfakeapp.VIDEO_RECORD_FROM_NOTIFICATION"
        const val ACTION_VIEW_RESULT = "com.anonymous.deepfakeapp.VIEW_RESULT"
        const val ACTION_UPDATE_UPLOADING = "com.anonymous.deepfakeapp.UPDATE_UPLOADING"
        const val ACTION_UPDATE_ANALYZING = "com.anonymous.deepfakeapp.UPDATE_ANALYZING"
        const val ACTION_UPDATE_ANALYSIS_RESULT = "com.anonymous.deepfakeapp.UPDATE_ANALYSIS_RESULT"
        
        // Notification
        const val CHANNEL_ID = "floating_widget_channel"
        const val NOTIFICATION_ID = 1001
        
        // Notification States
        const val STATE_INITIAL = "initial"
        const val STATE_UPLOADING = "uploading"
        const val STATE_ANALYZING = "analyzing"
        const val STATE_COMPLETED = "completed"
    }
    
    // 알림 상태 관리
    private var notificationState = STATE_INITIAL
    private var uploadProgress = 0
    private var analysisResult: String? = null
    private var deepfakePercentage = 0
    private var audioPercentage = 0
    private var videoId: String? = null

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
                // 플로팅 위젯 표시
                showFloatingWidget()
                return START_STICKY
            }
            ACTION_STOP -> {
                stopFloatingWidget()
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
                return START_NOT_STICKY
            }
            ACTION_UPLOAD_FROM_NOTIFICATION -> {
                android.util.Log.d("FloatingService", "=== ACTION_UPLOAD_FROM_NOTIFICATION received ===")
                // "업로드" 버튼 = 녹화 시작 후 자동 분석
                if (isRecording) {
                    // 이미 녹화 중이면 무시
                    android.util.Log.d("FloatingService", "이미 녹화 중이므로 무시")
                    return START_STICKY
                }
                
                // 상태를 초기 상태로 리셋
                notificationState = STATE_INITIAL
                analysisResult = null
                deepfakePercentage = 0
                audioPercentage = 0
                videoId = null
                
                // 녹화 시작 (자동 분석 플래그 설정)
                val recordIntent = Intent(this, MainActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    action = "START_RECORDING_WITH_ANALYSIS"
                }
                startActivity(recordIntent)
                return START_STICKY
            }
            ACTION_VIDEO_RECORD_FROM_NOTIFICATION -> {
                android.util.Log.d("FloatingService", "=== ACTION_VIDEO_RECORD_FROM_NOTIFICATION received ===")
                if (isRecording) {
                    // 녹화 중이면 중지
                    stopScreenRecording()
                } else {
                    // 녹화 중이 아니면 시작 (MediaProjection 권한 요청)
                    val recordIntent = Intent(this, MainActivity::class.java).apply {
                        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        action = "START_RECORDING"
                    }
                    startActivity(recordIntent)
                }
                return START_STICKY
            }
            ACTION_VIEW_RESULT -> {
                android.util.Log.d("FloatingService", "=== ACTION_VIEW_RESULT received ===")
                // MainActivity로 이동하여 결과 화면 열기
                val resultIntent = Intent(this, MainActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    action = "VIEW_RESULT"
                    putExtra("videoId", videoId)
                }
                startActivity(resultIntent)
                return START_STICKY
            }
            ACTION_UPDATE_UPLOADING -> {
                android.util.Log.d("FloatingService", "=== ACTION_UPDATE_UPLOADING received ===")
                notificationState = STATE_UPLOADING
                uploadProgress = intent?.getIntExtra("progress", 0) ?: 0
                updateNotification()
                return START_STICKY
            }
            ACTION_UPDATE_ANALYZING -> {
                android.util.Log.d("FloatingService", "=== ACTION_UPDATE_ANALYZING received ===")
                notificationState = STATE_ANALYZING
                updateNotification()
                return START_STICKY
            }
            ACTION_UPDATE_ANALYSIS_RESULT -> {
                android.util.Log.d("FloatingService", "=== ACTION_UPDATE_ANALYSIS_RESULT received ===")
                notificationState = STATE_COMPLETED
                deepfakePercentage = intent?.getIntExtra("deepfakePercentage", 0) ?: 0
                audioPercentage = intent?.getIntExtra("audioPercentage", 0) ?: 0
                analysisResult = intent?.getStringExtra("result") ?: "REAL"
                videoId = intent?.getStringExtra("videoId")
                updateNotification()
                return START_STICKY
            }
            ACTION_RECORD_FROM_NOTIFICATION -> {
                android.util.Log.d("FloatingService", "=== ACTION_RECORD_FROM_NOTIFICATION received ===")
                // MainActivity로 이동하여 MediaProjection 권한 요청
                val recordIntent = Intent(this, MainActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    action = "START_RECORDING"
                }
                startActivity(recordIntent)
                // 알림 업데이트
                updateNotification()
                return START_STICKY
            }
            ACTION_CAPTURE_FROM_NOTIFICATION -> {
                android.util.Log.d("FloatingService", "=== ACTION_CAPTURE_FROM_NOTIFICATION received ===")
                // MainActivity로 이동하여 MediaProjection 권한 요청
                val captureIntent = Intent(this, MainActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    action = "CAPTURE_FRAME"
                }
                startActivity(captureIntent)
                return START_STICKY
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
                return START_STICKY
            }
            ACTION_STOP_RECORDING -> {
                stopScreenRecording()
                return START_STICKY
            }
            ACTION_CAPTURE_FRAME -> {
                captureFrame(intent)
                return START_STICKY
            }
        }
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "딥페이크 탐지 서비스",
                NotificationManager.IMPORTANCE_DEFAULT  // IMPORTANCE_LOW는 알림이 표시되지 않을 수 있음
            ).apply {
                description = "딥페이크 탐지 서비스가 실행 중입니다"
                setShowBadge(true)
                setSound(null, null)
                enableVibration(false)
            }
            val notificationManager = getSystemService(NotificationManager::class.java)
            notificationManager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        // 앱으로 이동하는 Intent
        val appIntent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val appPendingIntent = PendingIntent.getActivity(
            this, 0, appIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setOngoing(true) // 계속 표시되는 알림
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(appPendingIntent) // 알림 클릭 시 앱으로 이동
            .setAutoCancel(false) // 자동으로 사라지지 않음
        
        // 비디오 녹화 버튼 (모든 상태에서 표시, 녹화 중/중지 토글)
        val videoRecordIntent = Intent(this, FloatingService::class.java).apply {
            action = ACTION_VIDEO_RECORD_FROM_NOTIFICATION
        }
        val videoRecordPendingIntent = PendingIntent.getService(
            this, 4, videoRecordIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val videoButtonText = if (isRecording) "녹화 중지" else "비디오"
        
        // 상태에 따라 다른 알림 표시
        when (notificationState) {
            STATE_INITIAL -> {
                // 초기화면: 비디오 녹화 버튼만 (녹화 종료 시 자동 분석)
                builder.setContentTitle("딥페이크 탐지")
                    .setContentText(if (isRecording) "녹화 중..." else "화면을 녹화하세요")
                    .setStyle(NotificationCompat.BigTextStyle()
                        .bigText(if (isRecording) "화면 녹화가 진행 중입니다. 녹화 종료 시 자동으로 분석됩니다." else "화면을 녹화하여 딥페이크를 탐지하세요. 녹화 종료 시 자동으로 분석됩니다."))
                    .addAction(
                        android.R.drawable.ic_menu_camera,
                        videoButtonText,
                        videoRecordPendingIntent
                    )
            }
            STATE_UPLOADING -> {
                // 업로드 중: 진행 상태
                builder.setContentTitle("영상 업로드 중...")
                    .setContentText("업로드 진행률: $uploadProgress%")
                    .setProgress(100, uploadProgress, false)
                    .addAction(
                        android.R.drawable.ic_menu_camera,
                        videoButtonText,
                        videoRecordPendingIntent
                    )
            }
            STATE_ANALYZING -> {
                // 분석 중
                builder.setContentTitle("딥페이크 분석 중...")
                    .setContentText("영상을 분석하고 있습니다")
                    .setProgress(0, 0, true) // 무한 진행 표시
                    .addAction(
                        android.R.drawable.ic_menu_camera,
                        videoButtonText,
                        videoRecordPendingIntent
                    )
            }
            STATE_COMPLETED -> {
                // 분석 완료: 결과 표시
                val resultText = if (analysisResult == "FAKE") {
                    "FIKE가 딥페이크를 찾았어요!"
                } else {
                    "이 영상은 진짜입니다"
                }
                
                val viewResultIntent = Intent(this, FloatingService::class.java).apply {
                    action = ACTION_VIEW_RESULT
                }
                val viewResultPendingIntent = PendingIntent.getService(
                    this, 3, viewResultIntent,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                
                val resultDetail = if (analysisResult == "FAKE") {
                    "이 영상은 ${deepfakePercentage}% 확률로 딥페이크로 판단합니다.\n" +
                    "음성영역 ${audioPercentage}% 확률로 위조로 판단합니다."
                } else {
                    "이 영상은 진짜입니다."
                }
                
                builder.setContentTitle(resultText)
                    .setContentText(resultDetail)
                    .setStyle(NotificationCompat.BigTextStyle()
                        .bigText(resultDetail))
                    .setProgress(0, 0, false) // 진행 표시 제거
                    .addAction(
                        android.R.drawable.ic_menu_camera,
                        videoButtonText,
                        videoRecordPendingIntent
                    )
                    .addAction(
                        android.R.drawable.ic_menu_view,
                        "자세히 보기",
                        viewResultPendingIntent
                    )
                
                // 상태는 완료 상태로 유지 (사용자가 결과를 확인할 수 있도록)
                // 다음 업로드를 위해서는 사용자가 "업로드" 버튼을 다시 누르면 초기 상태로 돌아감
            }
        }
        
        // 종료 버튼은 모든 상태에서 표시
        val stopIntent = Intent(this, FloatingService::class.java).apply {
            action = ACTION_STOP
        }
        val stopPendingIntent = PendingIntent.getService(
            this, 2, stopIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        builder.addAction(
            android.R.drawable.ic_menu_close_clear_cancel,
            "종료",
            stopPendingIntent
        )
        
        // Android 14+ (API 34+)에서는 foregroundServiceType 설정
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            builder.setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
        }
        
        return builder.build()
    }
    
    private fun updateNotification() {
        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.notify(NOTIFICATION_ID, createNotification())
    }

    // 플로팅 위젯 표시
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

        // Create main button with camera icon
        val mainButton = ImageView(this).apply {
            val size = (60 * resources.displayMetrics.density).toInt() // 초기 크기로 복원
            layoutParams = FrameLayout.LayoutParams(size, size).apply {
                gravity = Gravity.CENTER
            }
            
            // 카메라 아이콘 로드 시도
            try {
                // drawable에 camera_icon.png가 있으면 사용
                val iconResId = resources.getIdentifier("camera_icon", "drawable", packageName)
                if (iconResId != 0) {
                    setImageResource(iconResId)
                    setBackgroundColor(Color.TRANSPARENT)
                } else {
                    // 아이콘이 없으면 임시로 배경색 사용
                    android.util.Log.w("FloatingService", "camera_icon drawable을 찾을 수 없습니다. PNG로 변환해서 drawable에 추가하세요.")
                    setBackgroundColor(Color.parseColor("#2563eb")) // 임시 파란색 배경
                }
            } catch (e: Exception) {
                android.util.Log.e("FloatingService", "Failed to load camera icon", e)
                setBackgroundColor(Color.parseColor("#2563eb")) // 임시 파란색 배경
            }
            
            scaleType = ImageView.ScaleType.CENTER_INSIDE
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
        recordButton = ImageButton(this).apply {
            try {
                val recordIcon = ContextCompat.getDrawable(this@FloatingService, resources.getIdentifier("icon_record", "drawable", packageName))
                if (recordIcon != null) {
                    setImageDrawable(recordIcon)
                } else {
                    // 아이콘을 찾을 수 없으면 기본 아이콘 사용
                    setImageResource(android.R.drawable.ic_media_play)
                }
            } catch (e: Exception) {
                android.util.Log.e("FloatingService", "Failed to load icon_record", e)
                setImageResource(android.R.drawable.ic_media_play)
            }
            setBackgroundColor(Color.TRANSPARENT)
            val size = (50 * resources.displayMetrics.density).toInt() // 초기 크기로 복원
            layoutParams = FrameLayout.LayoutParams(size, size).apply {
                gravity = Gravity.CENTER_HORIZONTAL or Gravity.TOP
                bottomMargin = (80 * resources.displayMetrics.density).toInt()
            }
            elevation = 6f
            tag = "record_btn"
            scaleType = android.widget.ImageView.ScaleType.FIT_CENTER
            setPadding(8, 8, 8, 8)
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

        val captureBtn = ImageButton(this).apply {
            try {
                val captureIcon = ContextCompat.getDrawable(this@FloatingService, resources.getIdentifier("icon_capture", "drawable", packageName))
                if (captureIcon != null) {
                    setImageDrawable(captureIcon)
                }
            } catch (e: Exception) {
                android.util.Log.e("FloatingService", "Failed to load icon_capture", e)
            }
            setBackgroundColor(Color.TRANSPARENT)
            val size = (50 * resources.displayMetrics.density).toInt() // 초기 크기로 복원
            layoutParams = FrameLayout.LayoutParams(size, size).apply {
                gravity = Gravity.CENTER_VERTICAL or Gravity.START
                marginEnd = (80 * resources.displayMetrics.density).toInt()
            }
            elevation = 6f
            scaleType = android.widget.ImageView.ScaleType.FIT_CENTER
            setPadding(8, 8, 8, 8)
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

        val exitBtn = ImageButton(this).apply {
            try {
                val closeIcon = ContextCompat.getDrawable(this@FloatingService, resources.getIdentifier("icon_close", "drawable", packageName))
                if (closeIcon != null) {
                    setImageDrawable(closeIcon)
                }
            } catch (e: Exception) {
                android.util.Log.e("FloatingService", "Failed to load icon_close", e)
            }
            setBackgroundColor(Color.TRANSPARENT)
            val size = (50 * resources.displayMetrics.density).toInt() // 초기 크기로 복원
            layoutParams = FrameLayout.LayoutParams(size, size).apply {
                gravity = Gravity.CENTER_VERTICAL or Gravity.END
                marginStart = (80 * resources.displayMetrics.density).toInt()
            }
            elevation = 6f
            scaleType = android.widget.ImageView.ScaleType.FIT_CENTER
            setPadding(8, 8, 8, 8)
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

    // 플로팅 위젯 메뉴 토글
    private fun toggleMenu() {
        val menuContainer = floatingView?.findViewWithTag<FrameLayout>("menu_container") ?: return
        val mainButton = floatingView?.getChildAt(0) ?: return
        
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
    
    // 녹화 버튼 아이콘 업데이트
    private fun updateRecordButton(recording: Boolean) {
        recordButton?.let { button ->
            try {
                val iconResId: Int = if (recording) {
                    // 녹화 중일 때는 종료 아이콘 표시
                    resources.getIdentifier("icon_close", "drawable", packageName)
                } else {
                    // 녹화 중이 아닐 때는 녹화 아이콘 표시
                    resources.getIdentifier("icon_record", "drawable", packageName)
                }
                
                if (iconResId != 0) {
                    val icon = ContextCompat.getDrawable(this, iconResId)
                    if (icon != null) {
                        button.setImageDrawable(icon)
                    } else {
                        // icon이 null인 경우 아무것도 하지 않음
                    }
                } else {
                    // iconResId가 0인 경우 아무것도 하지 않음
                }
            } catch (e: Exception) {
                android.util.Log.e("FloatingService", "Failed to update record button icon", e)
            }
        }
    }

    // 플로팅 위젯 제거
    private fun stopFloatingWidget() {
        floatingView?.let {
            try {
                windowManager?.removeView(it)
            } catch (e: Exception) {
                android.util.Log.e("FloatingService", "Error removing floating view", e)
            }
            floatingView = null
        }
        recordButton = null
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
                
                // 플로팅 위젯 버튼 업데이트
                updateRecordButton(true)
                
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
            
            // 플로팅 위젯 버튼 업데이트
            updateRecordButton(false)
            
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
                    
                    // 녹화 종료 시 항상 자동 분석 시작
                    android.util.Log.d("FloatingService", "녹화 종료 - 자동 분석 시작: ${file.absolutePath}")
                    startAutoAnalysis(file.absolutePath)
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
    
    private fun sendAnalyzingEvent() {
        try {
            val app = applicationContext as? ReactApplication
            val reactContext = app?.reactNativeHost?.reactInstanceManager?.currentReactContext as? com.facebook.react.bridge.ReactApplicationContext
            reactContext?.let {
                android.util.Log.d("FloatingService", "분석 시작 이벤트 전송")
                it.getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter::class.java)
                    .emit("onAnalyzing", Arguments.createMap())
            }
        } catch (e: Exception) {
            android.util.Log.e("FloatingService", "Error in sendAnalyzingEvent", e)
            e.printStackTrace()
        }
    }
    
    private fun sendAnalysisResultEvent(result: String, deepfakePercentage: Int, audioPercentage: Int, videoId: String?) {
        try {
            val app = applicationContext as? ReactApplication
            val reactContext = app?.reactNativeHost?.reactInstanceManager?.currentReactContext as? com.facebook.react.bridge.ReactApplicationContext
            reactContext?.let {
                val params = Arguments.createMap().apply {
                    putString("result", result)
                    putInt("deepfakePercentage", deepfakePercentage)
                    putInt("audioPercentage", audioPercentage)
                    putString("videoId", videoId)
                }
                android.util.Log.d("FloatingService", "분석 완료 이벤트 전송: result=$result, percentage=$deepfakePercentage%")
                it.getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter::class.java)
                    .emit("onAnalysisResult", params)
            }
        } catch (e: Exception) {
            android.util.Log.e("FloatingService", "Error in sendAnalysisResultEvent", e)
            e.printStackTrace()
        }
    }
    
    private fun startAutoAnalysis(videoFilePath: String) {
        android.util.Log.d("FloatingService", "=== 자동 분석 시작 ===")
        android.util.Log.d("FloatingService", "비디오 파일: $videoFilePath")
        
        // 백그라운드 스레드에서 분석 시작
        Thread {
            try {
                // 알림 상태를 "분석 중"으로 변경
                notificationState = STATE_ANALYZING
                android.os.Handler(android.os.Looper.getMainLooper()).post {
                    updateNotification()
                    // React Native로 분석 시작 이벤트 전송
                    sendAnalyzingEvent()
                }
                
                // API URL (개발 환경 기본값, 필요시 SharedPreferences에서 가져오기)
                val apiBaseUrl = "http://10.56.56.21:8000" // TODO: 설정에서 가져오기
                val apiUrl = "$apiBaseUrl/analyze-video/"
                
                android.util.Log.d("FloatingService", "API URL: $apiUrl")
                
                val client = OkHttpClient.Builder()
                    .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                    .writeTimeout(120, java.util.concurrent.TimeUnit.SECONDS)
                    .readTimeout(120, java.util.concurrent.TimeUnit.SECONDS)
                    .build()
                
                val videoFile = File(videoFilePath)
                val requestBody = MultipartBody.Builder()
                    .setType(MultipartBody.FORM)
                    .addFormDataPart("user_id", "user123")
                    .addFormDataPart(
                        "video",
                        videoFile.name,
                        videoFile.asRequestBody("video/mp4".toMediaType())
                    )
                    .build()
                
                val request = Request.Builder()
                    .url(apiUrl)
                    .post(requestBody)
                    .build()
                
                android.util.Log.d("FloatingService", "HTTP 요청 전송 중...")
                val response = client.newCall(request).execute()
                
                if (response.isSuccessful) {
                    val responseBody = response.body?.string()
                    android.util.Log.d("FloatingService", "분석 완료: ${responseBody?.substring(0, minOf(200, responseBody?.length ?: 0))}")
                    
                    // JSON 파싱하여 결과 추출
                    val jsonResponse = org.json.JSONObject(responseBody ?: "{}")
                    val summary = jsonResponse.optJSONObject("summary")
                    val videoAnalysis = jsonResponse.optJSONObject("video_analysis")
                    val audioAnalysis = jsonResponse.optJSONObject("audio_analysis")
                    
                    val result = summary?.optString("overall_result") 
                        ?: videoAnalysis?.optString("overall_result") 
                        ?: "REAL"
                    
                    val deepfakePercentage = ((summary?.optDouble("overall_confidence") 
                        ?: videoAnalysis?.optDouble("overall_confidence") 
                        ?: 0.0) * 100).toInt()
                    
                    val audioPercentage = ((audioAnalysis?.optDouble("fake_confidence") 
                        ?: 0.0) * 100).toInt()
                    
                    val videoId = jsonResponse.optString("videoId", "")
                    
                    // 메인 스레드에서 알림 업데이트
                    android.os.Handler(android.os.Looper.getMainLooper()).post {
                        notificationState = STATE_COMPLETED
                        analysisResult = result
                        this.deepfakePercentage = deepfakePercentage
                        this.audioPercentage = audioPercentage
                        this.videoId = videoId
                        updateNotification()
                        // React Native로 분석 완료 이벤트 전송
                        sendAnalysisResultEvent(result, deepfakePercentage, audioPercentage, videoId)
                    }
                    
                    android.util.Log.d("FloatingService", "분석 결과: $result, 딥페이크 확률: $deepfakePercentage%, 오디오 확률: $audioPercentage%")
                } else {
                    android.util.Log.e("FloatingService", "분석 실패: ${response.code} - ${response.message}")
                    android.os.Handler(android.os.Looper.getMainLooper()).post {
                        notificationState = STATE_INITIAL
                        updateNotification()
                        
                        try {
                            android.widget.Toast.makeText(
                                this@FloatingService,
                                "분석 실패: ${response.code}",
                                android.widget.Toast.LENGTH_SHORT
                            ).show()
                        } catch (e: Exception) {
                            // Toast 실패는 무시
                        }
                    }
                }
            } catch (e: Exception) {
                android.util.Log.e("FloatingService", "자동 분석 오류", e)
                e.printStackTrace()
                
                    android.os.Handler(android.os.Looper.getMainLooper()).post {
                        notificationState = STATE_INITIAL
                        updateNotification()
                        
                        try {
                            android.widget.Toast.makeText(
                                this@FloatingService,
                                "분석 오류: ${e.message}",
                                android.widget.Toast.LENGTH_SHORT
                            ).show()
                        } catch (toastEx: Exception) {
                            // Toast 실패는 무시
                        }
                    }
            }
        }.start()
    }

}

