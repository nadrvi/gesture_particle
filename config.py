"""
config.py - Pengaturan global sistem deteksi gesture tangan & Particle Universe 3D.
"""

# --- Kamera & Render Canvas ---
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# --- High-Refresh Rate Engine Settings ---
TARGET_FPS = 120
FRAME_TIME = 1.0 / TARGET_FPS

# --- MediaPipe Hands (Dual-Hand Combo Mode) ---
HAND_LANDMARKER_MODEL = "models/hand_landmarker.task"
MAX_NUM_HANDS = 2             # Di-upgrade ke 2 Tangan Sekaligus!
MIN_DETECTION_CONFIDENCE = 0.60
MIN_TRACKING_CONFIDENCE = 0.60

# --- Stabilisasi Gesture ---
GESTURE_BUFFER_SIZE = 5
MIN_VOTES_RATIO = 0.5

# --- Particle Universe 3D Engine ---
PARTICLE_COUNT = 1400
PARTICLE_LERP_FACTOR = 0.08
FOCAL_LENGTH_3D = 600.0

# --- Stardust Spark Emitter & Plasma Beam ---
SPARK_VELOCITY_THRESHOLD = 380.0
MAX_SPARKS_POOL = 350
SHOCKWAVE_SPEED = 1200.0

# --- Asset ---
LOGO_PATH = "assets/cakrawala_logo.png"
LOGO_DISPLAY_WIDTH = 180

# --- Tampilan & HUD ---
DRAW_HAND_LANDMARKS = True
SHOW_FPS = True
MIRROR_CAMERA = True