package com.anonymous.deepfakeapp

import android.app.*
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.PixelFormat
import android.graphics.RectF
import android.graphics.drawable.BitmapDrawable
import android.graphics.drawable.GradientDrawable
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.Image
import android.media.ImageReader
import android.media.MediaRecorder
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.util.Base64
import android.widget.FrameLayout
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Button
import androidx.core.app.NotificationCompat
import com.caverock.androidsvg.SVG
import com.facebook.react.bridge.Arguments
import com.facebook.react.modules.core.DeviceEventManagerModule
import com.facebook.react.ReactApplication
import kotlin.math.roundToInt
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.util.concurrent.Executors
import java.util.concurrent.ExecutorService
import java.util.concurrent.TimeUnit

class FloatingService : Service() {
    private var windowManager: WindowManager? = null
    private var floatingView: FrameLayout? = null
    private var mainButtonView: View? = null
    private var resultIconView: ImageView? = null
    private var recordButton: ImageButton? = null  // 버튼 참조 저장
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
    private val backendBaseUrl = if (BuildConfig.DEBUG) {
        "http://10.56.56.21:8000"
    } else {
        "https://your-production-url.com"
    }
    private val analysisClient: OkHttpClient = OkHttpClient.Builder()
        .callTimeout(120, TimeUnit.SECONDS)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)
        .writeTimeout(120, TimeUnit.SECONDS)
        .build()
    private val analysisExecutor: ExecutorService = Executors.newSingleThreadExecutor()
    private val mainHandler = Handler(Looper.getMainLooper())
    private var analysisOverlay: AnalysisOverlayComponents? = null
    private var analysisOverlayParams: WindowManager.LayoutParams? = null
    private var lastAnalysisFilePath: String? = null
    private var lastAnalysisVideoId: String? = null
    private var widgetAnalysisInProgress: Boolean = false
    private val loadingFrameNames = arrayOf("loding1", "loding2", "loding3", "loding4")
    private var loadingFrameIndex = 0
    private var loadingAnimationRunning = false
    private val loadingAnimationRunnable = object : Runnable {
        override fun run() {
            if (!loadingAnimationRunning) return
            val overlay = analysisOverlay ?: return
            overlay.loadingImages.forEachIndexed { index, imageView ->
                if (index == loadingFrameIndex) {
                    imageView.visibility = View.VISIBLE
                    imageView.setImageDrawable(loadIconDrawable(loadingFrameNames[index]))
                } else {
                    imageView.visibility = View.INVISIBLE
                }
            }
            loadingFrameIndex = (loadingFrameIndex + 1) % loadingFrameNames.size
            mainHandler.postDelayed(this, 250L)
        }
    }
    
    companion object {
        // Service Actions
        const val ACTION_START = "com.anonymous.deepfakeapp.START"
        const val ACTION_STOP = "com.anonymous.deepfakeapp.STOP"
        const val ACTION_TOGGLE_MENU = "com.anonymous.deepfakeapp.TOGGLE_MENU"
        const val ACTION_START_RECORDING = "com.anonymous.deepfakeapp.START_RECORDING"
        const val ACTION_STOP_RECORDING = "com.anonymous.deepfakeapp.STOP_RECORDING"
        const val ACTION_CAPTURE_FRAME = "com.anonymous.deepfakeapp.CAPTURE_FRAME"
        const val ACTION_UPDATE_UPLOADING = "com.anonymous.deepfakeapp.UPDATE_UPLOADING"
        const val ACTION_UPDATE_ANALYZING = "com.anonymous.deepfakeapp.UPDATE_ANALYZING"
        const val ACTION_UPDATE_ANALYSIS_RESULT = "com.anonymous.deepfakeapp.UPDATE_ANALYSIS_RESULT"
        
        // Notification
        const val CHANNEL_ID = "floating_widget_channel"
        const val NOTIFICATION_ID = 1001
    }

    private data class AnalysisOverlayComponents(
        val container: FrameLayout,
        val loadingImages: List<ImageView>,
        val statusText: TextView,
        val percentageText: TextView,
        val detailText: TextView,
        val progressBar: ProgressBar,
        val closeButton: Button,
        val openAppButton: Button
    )
    private data class NativeAnalysisResult(
        val percentage: Int,
        val videoId: String?,
        val rawJson: JSONObject
    )

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
            ACTION_UPDATE_UPLOADING -> {
                // 업로드 진행률 업데이트 (필요시 구현)
                val progress = intent?.getIntExtra("progress", 0) ?: 0
                android.util.Log.d("FloatingService", "Upload progress: $progress%")
            }
            ACTION_UPDATE_ANALYZING -> {
                // 분석 중 상태 업데이트 (필요시 구현)
                android.util.Log.d("FloatingService", "Analysis in progress")
            }
            ACTION_UPDATE_ANALYSIS_RESULT -> {
                // 분석 결과 업데이트 (필요시 구현)
                val result = intent?.getStringExtra("result") ?: ""
                val deepfakePercentage = intent?.getIntExtra("deepfakePercentage", 0) ?: 0
                val audioPercentage = intent?.getIntExtra("audioPercentage", 0) ?: 0
                android.util.Log.d("FloatingService", "Analysis result: $result, deepfake: $deepfakePercentage%, audio: $audioPercentage%")
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
        val mainButtonSize = (70 * resources.displayMetrics.density).toInt()
        val mainButton = object : View(this) {
            private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
            private val arcRect = RectF()

            override fun onDraw(canvas: Canvas) {
                super.onDraw(canvas)
                val sizePx = width.coerceAtMost(height).toFloat()
                val radius = sizePx / 2f
                val centerX = width / 2f
                val centerY = height / 2f

                // 기본 흰색 원
                paint.style = Paint.Style.FILL
                paint.color = Color.WHITE
                canvas.drawCircle(centerX, centerY, radius, paint)

                // 금색 호 (우측-하단 90도)
                paint.color = Color.parseColor("#FFC628")
                arcRect.set(centerX - radius, centerY - radius, centerX + radius, centerY + radius)
                canvas.drawArc(arcRect, 0f, 90f, true, paint)

                // 검은색 원
                paint.color = Color.BLACK
                val blackRadiusRatio = 26.4964f / 52.0713f
                val blackDxRatio = (50.8315f - 52.0713f) / 52.0713f
                val blackDyRatio = (51.0069f - 52.0713f) / 52.0713f
                canvas.drawCircle(
                    centerX + blackDxRatio * radius,
                    centerY + blackDyRatio * radius,
                    radius * blackRadiusRatio,
                    paint
                )

                // 흰색 작은 원
                paint.color = Color.WHITE
                val whiteRadiusRatio = 16.1283f / 52.0713f
                val whiteDxRatio = (61.1996f - 52.0713f) / 52.0713f
                val whiteDyRatio = (61.3751f - 52.0713f) / 52.0713f
                canvas.drawCircle(
                    centerX + whiteDxRatio * radius,
                    centerY + whiteDyRatio * radius,
                    radius * whiteRadiusRatio,
                    paint
                )
            }
        }.apply {
            layoutParams = FrameLayout.LayoutParams(mainButtonSize, mainButtonSize).apply {
                gravity = Gravity.CENTER
            }
            elevation = 10f
            setLayerType(View.LAYER_TYPE_SOFTWARE, null)
        }.also { mainButtonView = it }

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
        mainButtonView = mainButton

        // Create menu buttons
        val iconSize = (54 * resources.displayMetrics.density).toInt()
        val iconPadding = (10 * resources.displayMetrics.density).toInt()

        recordButton = ImageButton(this).apply {
            setImageDrawable(loadIconDrawable("camera"))
            scaleType = ImageView.ScaleType.CENTER_INSIDE
            background = createCircleBackground(Color.parseColor("#F2FFFFFF"))
            setPadding(iconPadding, iconPadding, iconPadding, iconPadding)
            val size = iconSize
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
                    // MainActivity를 백그라운드에서 시작하여 MediaProjection 권한 요청
                    // FLAG_ACTIVITY_NEW_TASK만 사용하고, 투명 Activity로 처리
                    val intent = Intent(this@FloatingService, MainActivity::class.java).apply {
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_NO_ANIMATION
                        action = "START_RECORDING"
                        putExtra("hideActivity", true)  // Activity를 숨기도록 표시
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
            setImageDrawable(loadIconDrawable("cap"))
            scaleType = ImageView.ScaleType.CENTER_INSIDE
            background = createCircleBackground(Color.parseColor("#F2FFFFFF"))
            setPadding(iconPadding, iconPadding, iconPadding, iconPadding)
            val size = iconSize
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

        val exitBtn = ImageButton(this).apply {
            setImageDrawable(loadIconDrawable("del"))
            scaleType = ImageView.ScaleType.CENTER_INSIDE
            background = createCircleBackground(Color.parseColor("#F2FFFFFF"))
            setPadding(iconPadding, iconPadding, iconPadding, iconPadding)
            val size = iconSize
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
        resultIconView = ImageView(this).apply {
            visibility = View.GONE
            layoutParams = FrameLayout.LayoutParams(
                mainButtonSize,
                mainButtonSize
            ).apply {
                gravity = Gravity.CENTER
            }
            scaleType = ImageView.ScaleType.FIT_CENTER
        }
        floatingView!!.addView(resultIconView)
        resultIconView?.bringToFront()
        floatingView!!.addView(menuContainer)
        resultIconView?.bringToFront()

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

    private fun loadIconDrawable(name: String): BitmapDrawable? {
        // 1) Try rendering SVG directly (preserves vector quality)
        try {
            assets.open("$name.svg").use { stream ->
                val svg = SVG.getFromInputStream(stream)
                val viewBox = svg.documentViewBox
                val intrinsicWidth = if (svg.documentWidth != -1f) svg.documentWidth else viewBox?.width() ?: 120f
                val intrinsicHeight = if (svg.documentHeight != -1f) svg.documentHeight else viewBox?.height() ?: 120f
                
                val bitmap = Bitmap.createBitmap(
                    intrinsicWidth.toInt().coerceAtLeast(1),
                    intrinsicHeight.toInt().coerceAtLeast(1),
                    Bitmap.Config.ARGB_8888
                )
                val canvas = Canvas(bitmap)
                canvas.drawColor(Color.TRANSPARENT)
                svg.renderToCanvas(canvas)
                return BitmapDrawable(resources, bitmap)
            }
        } catch (e: Exception) {
            android.util.Log.w("FloatingService", "Failed to render SVG for $name, falling back to PNG/base64", e)
        }
        
        // 2) Try PNG version (pre-decoded asset)
        try {
            assets.open("$name.png").use { stream ->
                val bitmap = BitmapFactory.decodeStream(stream)
                if (bitmap != null) {
                    return BitmapDrawable(resources, bitmap)
                }
            }
        } catch (_: Exception) {
            // fallback to SVG
        }

        val assetName = "$name.svg"
        return try {
            val svgContent = assets.open(assetName).bufferedReader().use { it.readText() }
            val match = Regex("base64,([A-Za-z0-9+/=]+)\"").find(svgContent) ?: return null
            val bytes = Base64.decode(match.groupValues[1], Base64.DEFAULT)
            val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
            BitmapDrawable(resources, bitmap)
        } catch (e: Exception) {
            android.util.Log.e("FloatingService", "Failed to load asset $assetName", e)
            null
        }
    }

    private fun createCircleBackground(fillColor: Int): GradientDrawable {
        val strokeWidth = (1 * resources.displayMetrics.density).toInt().coerceAtLeast(1)
        return GradientDrawable().apply {
            shape = GradientDrawable.OVAL
            setColor(fillColor)
            setStroke(strokeWidth, Color.parseColor("#33000000"))
        }
    }

    private fun ensureAnalysisOverlay(): AnalysisOverlayComponents {
        analysisOverlay?.let { return it }
        
        val container = FrameLayout(this).apply {
            setBackgroundColor(Color.TRANSPARENT)
        }
        
        val cardWidth = (320 * resources.displayMetrics.density).toInt()
        val card = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 48, 48, 48)
            background = GradientDrawable().apply {
                cornerRadius = 40f
                setColor(Color.WHITE)
                setStroke(
                    (2 * resources.displayMetrics.density).toInt(),
                    Color.parseColor("#F3F4F6")
                )
            }
            layoutParams = FrameLayout.LayoutParams(
                cardWidth,
                FrameLayout.LayoutParams.WRAP_CONTENT
            )
            minimumWidth = cardWidth
        }
        
        val loadingContainer = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            val size = (60 * resources.displayMetrics.density).toInt()
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                size
            ).apply {
                bottomMargin = (24 * resources.displayMetrics.density).toInt()
                gravity = Gravity.CENTER_HORIZONTAL
            }
            gravity = Gravity.CENTER
        }
        
        val loadingImages = loadingFrameNames.mapIndexed { index, _ ->
            ImageView(this).apply {
                val size = if (index == 0 || index == loadingFrameNames.lastIndex) {
                    (54 * resources.displayMetrics.density).toInt()
                } else {
                    (74 * resources.displayMetrics.density).toInt()
                }
                layoutParams = LinearLayout.LayoutParams(size, size)
                visibility = if (index == 0) View.VISIBLE else View.INVISIBLE
                scaleType = ImageView.ScaleType.FIT_CENTER
            }.also { loadingContainer.addView(it) }
        }
        
        val statusText = TextView(this).apply {
            text = "위젯 분석 중"
            setTextColor(Color.parseColor("#111827"))
            textSize = 18f
        }
        
        val percentageText = TextView(this).apply {
            text = "0%"
            setTextColor(Color.parseColor("#111827"))
            textSize = 48f
            setPadding(0, 24, 0, 12)
            visibility = View.GONE
        }
        
        val detailText = TextView(this).apply {
            text = "영상 업로드 및 분석을 수행하고 있습니다..."
            setTextColor(Color.parseColor("#4B5563"))
            textSize = 16f
        }
        
        val progressBar = ProgressBar(this).apply {
            isIndeterminate = true
            visibility = View.VISIBLE
        }
        
        val buttonRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(0, 32, 0, 0)
            gravity = Gravity.CENTER
            setBaselineAligned(false)
        }
        
        fun createButtonBackground(): GradientDrawable = GradientDrawable().apply {
            cornerRadius = 24f
            setColor(Color.parseColor("#FFC628"))
        }
        
        val buttonSpacing = (12 * resources.displayMetrics.density).toInt()
        
        val openAppButton = Button(this).apply {
            text = "앱에서 보기"
            visibility = View.GONE
            setTextColor(Color.BLACK)
            background = createButtonBackground()
            setPadding(40, 12, 40, 12)
        }
        
        val closeButton = Button(this).apply {
            text = "닫기"
            setTextColor(Color.BLACK)
            background = createButtonBackground()
            setPadding(40, 12, 40, 12)
            setOnClickListener { hideAnalysisOverlay() }
        }
        
        val openParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply {
            marginEnd = buttonSpacing
        }
        buttonRow.addView(openAppButton, openParams)
        buttonRow.addView(closeButton)
        
        card.addView(loadingContainer)
        card.addView(statusText)
        card.addView(percentageText)
        card.addView(detailText)
        card.addView(progressBar)
        card.addView(buttonRow)
        
        container.addView(card)
        
        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
            } else {
                WindowManager.LayoutParams.TYPE_PHONE
            },
            WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN or WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.CENTER
        }
        
        windowManager?.addView(container, params)
        analysisOverlayParams = params
        val components = AnalysisOverlayComponents(
            container,
            loadingImages,
            statusText,
            percentageText,
            detailText,
            progressBar,
            closeButton,
            openAppButton
        )
        analysisOverlay = components
        openAppButton.setOnClickListener {
            openResultInApp()
        }
        return components
    }

    private fun showAnalysisOverlayLoading(autoStop: Boolean) {
        val overlay = ensureAnalysisOverlay()
        overlay.container.visibility = View.VISIBLE
        overlay.statusText.text = "위젯 분석 중"
        overlay.detailText.text = if (autoStop) {
            "자동 종료된 영상을 업로드하고 있습니다..."
        } else {
            "영상 업로드 및 분석을 수행하고 있습니다..."
        }
        overlay.loadingImages.forEachIndexed { index, imageView ->
            if (index == 0) {
                imageView.visibility = View.VISIBLE
                imageView.setImageDrawable(loadIconDrawable(loadingFrameNames[0]))
            } else {
                imageView.visibility = View.INVISIBLE
            }
        }
        overlay.progressBar.visibility = View.GONE
        overlay.percentageText.visibility = View.GONE
        overlay.openAppButton.visibility = View.GONE
        startLoadingAnimation()
    }

    private fun showAnalysisOverlayResult(percentage: Int, videoId: String?) {
        val overlay = ensureAnalysisOverlay()
        overlay.progressBar.visibility = View.GONE
        overlay.loadingImages.forEach { it.visibility = View.GONE }
        stopLoadingAnimation()
        overlay.percentageText.visibility = View.VISIBLE
        overlay.percentageText.text = "$percentage%"
        overlay.statusText.text = "분석 완료"
        overlay.detailText.text = if (percentage >= 50) {
            "위험 확률이 높습니다."
        } else {
            "위험 확률이 낮습니다."
        }
        overlay.openAppButton.visibility = View.VISIBLE
        lastAnalysisVideoId = videoId
        showResultIcon()
    }

    private fun showAnalysisOverlayError(message: String) {
        val overlay = ensureAnalysisOverlay()
        overlay.progressBar.visibility = View.GONE
        overlay.loadingImages.forEach { it.visibility = View.GONE }
        stopLoadingAnimation()
        overlay.percentageText.visibility = View.GONE
        overlay.statusText.text = "분석 실패"
        overlay.detailText.text = message
        overlay.openAppButton.visibility = View.VISIBLE
        hideResultIcon()
    }

    private fun hideAnalysisOverlay() {
        analysisOverlay?.let {
            try {
                windowManager?.removeView(it.container)
            } catch (_: Exception) {
            }
        }
        stopLoadingAnimation()
        analysisOverlay = null
        analysisOverlayParams = null
        hideResultIcon()
    }

    private fun openResultInApp() {
        val path = lastAnalysisFilePath ?: return
        hideAnalysisOverlay()
        sendRecordingCompleteEvent(path, false)
    }

    private fun showResultIcon() {
        mainHandler.post {
            val drawable = loadIconDrawable("we2")
            resultIconView?.apply {
                setImageDrawable(drawable)
                visibility = View.VISIBLE
            }
            mainButtonView?.visibility = View.INVISIBLE
        }
    }

    private fun hideResultIcon() {
        mainHandler.post {
            resultIconView?.visibility = View.GONE
            mainButtonView?.visibility = View.VISIBLE
        }
    }

    private fun startLoadingAnimation() {
        if (loadingAnimationRunning) return
        loadingAnimationRunning = true
        loadingFrameIndex = 0
        mainHandler.post(loadingAnimationRunnable)
    }

    private fun stopLoadingAnimation() {
        if (!loadingAnimationRunning) return
        loadingAnimationRunning = false
        mainHandler.removeCallbacks(loadingAnimationRunnable)
    }

    private fun startWidgetAnalysis(file: File, autoStop: Boolean) {
        if (widgetAnalysisInProgress) {
            android.util.Log.w("FloatingService", "Widget analysis already running, skipping new request")
            return
        }
        widgetAnalysisInProgress = true
        lastAnalysisFilePath = file.absolutePath
        mainHandler.post { showAnalysisOverlayLoading(autoStop) }
        analysisExecutor.execute {
            try {
                val result = performWidgetAnalysisRequest(file)
                mainHandler.post {
                    widgetAnalysisInProgress = false
                    showAnalysisOverlayResult(result.percentage, result.videoId)
                }
            } catch (e: Exception) {
                android.util.Log.e("FloatingService", "Native widget analysis failed", e)
                mainHandler.post {
                    widgetAnalysisInProgress = false
                    showAnalysisOverlayError(e.message ?: "분석 중 오류가 발생했습니다.")
                }
            }
        }
    }

    private fun performWidgetAnalysisRequest(file: File): NativeAnalysisResult {
        val mediaType = "video/mp4".toMediaType()
        val body = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("user_id", "widget_user")
            .addFormDataPart("video", file.name, file.asRequestBody(mediaType))
            .build()
        val url = "$backendBaseUrl/analyze-video/"
        android.util.Log.d("FloatingService", "Uploading widget recording to $url (${file.length()} bytes)")
        val request = Request.Builder()
            .url(url)
            .post(body)
            .build()
        analysisClient.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IOException("분석 서버 응답 오류: ${response.code}")
            }
            val jsonText = response.body?.string() ?: throw IOException("서버 응답이 비어있습니다")
            val json = JSONObject(jsonText)
            val percentage = calculateDeepfakePercentage(json)
            val videoId = json.optString("videoId", null)
            android.util.Log.d("FloatingService", "Native analysis success: $percentage%, videoId=$videoId")
            return NativeAnalysisResult(percentage, videoId, json)
        }
    }

    private fun calculateDeepfakePercentage(json: JSONObject): Int {
        json.optJSONObject("video_analysis")?.optDouble("overall_confidence")?.takeIf { !it.isNaN() }?.let {
            return (it * 100).roundToInt()
        }
        val summary = json.optJSONObject("summary")
        if (summary != null && summary.optString("overall_result", "").equals("FAKE", ignoreCase = true)) {
            val conf = summary.optDouble("overall_confidence")
            if (!conf.isNaN()) {
                return (conf * 100).roundToInt()
            }
        }
        val timeline = json.optJSONArray("timeline")
        if (timeline != null && timeline.length() > 0) {
            var total = 0.0
            var count = 0
            for (i in 0 until timeline.length()) {
                val segment = timeline.optJSONObject(i) ?: continue
                val result = segment.optString("result", segment.optString("ensemble_result", ""))
                if (result.equals("FAKE", ignoreCase = true)) {
                    val details = segment.optJSONObject("details")
                    val video = details?.optJSONObject("video")
                    val conf = video?.optDouble("fake_confidence")
                    if (conf != null && !conf.isNaN()) {
                        total += conf
                        count++
                        continue
                    }
                    val altConf = segment.optDouble("confidence")
                    if (!altConf.isNaN()) {
                        total += altConf
                        count++
                    }
                }
            }
            if (count > 0) {
                return (total / count * 100).roundToInt()
            }
        }
        return 0
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
        mainButtonView = null
        resultIconView = null
    }

    override fun onDestroy() {
        super.onDestroy()
        stopFloatingWidget()
        hideAnalysisOverlay()
        analysisExecutor.shutdownNow()
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
                        
                        // 해상도와 비트레이트를 높여서 분석 정확도 향상
                        // 원본 해상도 유지 (최대 1920x1080)
                        val width = minOf(screenWidth, 1920)
                        val height = minOf(screenHeight, 1080)
                        setVideoSize(width, height)
                        // 비트레이트를 높여서 품질 향상 (8Mbps)
                        setVideoEncodingBitRate(8 * 1000 * 1000) // 8Mbps
                        // 프레임레이트를 높여서 더 많은 프레임 확보 (30fps)
                        setVideoFrameRate(30) // 30fps
                        
                        android.util.Log.d("FloatingService", "MediaRecorder configured: ${width}x${height}, bitrate=8Mbps, fps=30")
                        
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
                    if (!autoStop) {
                        try {
                            android.widget.Toast.makeText(this@FloatingService, "녹화가 완료되었습니다", android.widget.Toast.LENGTH_SHORT).show()
                        } catch (e: Exception) {
                            // ignore
                        }
                    }
                    android.util.Log.d("FloatingService", "위젯 네이티브 분석 시작: ${file.absolutePath}")
                    startWidgetAnalysis(file, autoStop)
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
        val recordBtn = recordButton ?: floatingView?.findViewWithTag<ImageButton>("record_btn")
        android.util.Log.d("FloatingService", "recordBtn found: ${recordBtn != null}")
        
        if (recordBtn != null) {
            val newDescription = if (recording) "녹화 중지" else "녹화"
            val fillColor = if (recording) Color.parseColor("#FFE04C32") else Color.parseColor("#F2FFFFFF")
            
            android.util.Log.d("FloatingService", "Updating button: description='$newDescription'")
            
            // 메인 스레드에서 실행 확인 (이미 메인 스레드에서 호출되지만 안전을 위해)
            recordBtn.post {
                recordBtn.contentDescription = newDescription
                recordBtn.background = createCircleBackground(fillColor)
                android.util.Log.d("FloatingService", "Button updated successfully: contentDescription='${recordBtn.contentDescription}'")
            }
        } else {
            android.util.Log.e("FloatingService", "recordBtn not found! floatingView=$floatingView, recordButton=$recordButton")
            // 버튼을 다시 찾아서 저장 시도
            floatingView?.let { view ->
                val foundBtn = view.findViewWithTag<ImageButton>("record_btn")
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

