# 📚 Dokumentasi Lengkap: Sistem Deteksi Gesture Tangan Interaktif

**Sistem deteksi gesture tangan real-time dengan efek partikel responsif** menggunakan MediaPipe HandLandmarker + OpenCV

---

## 📦 Instalasi

### Prasyarat
- **Python 3.8+** (disarankan 3.10 atau lebih baru)
- **Webcam** yang bekerja dengan baik
- **Koneksi internet** (untuk download model MediaPipe)

### Langkah-Langkah Instalasi

#### 1. Buat Virtual Environment
```bash
python -m venv venv
```

#### 2. Aktivasi Virtual Environment

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Verifikasi Instalasi
Program akan otomatis mengunduh model `hand_landmarker.task` pada pertama kali dijalankan. Model ini akan disimpan di folder `models/`.

**Dependencies yang diinstal:**
- `opencv-python>=4.9.0` - Pemrosesan video dan rendering
- `mediapipe>=0.10.30` - Deteksi hand landmarks
- `numpy>=1.26.0` - Operasi numerik dan particle physics
- `Pillow>=10.0.0` - Pemrosesan gambar

---

## 🚀 Cara Menjalankan

```bash
python main.py
```

### Kontrol Keyboard
- **Q** - Keluar dari program
- **R** - Reset buffer gesture (jika deteksi terjebak di label salah)

---

## ✋ Panduan Gesture & Efek Partikel

Sistem ini mendeteksi **8 gestur dasar** dengan **efek partikel unik** untuk masing-masing. Selain itu, ada **6 kombinasi dual-hand** yang menghasilkan efek spesial!

### 🎯 GESTURE TUNGGAL (Single Hand)

#### 1. **LOVE** ❤️ (ASL "I Love You")
**Bentuk Gesture:**
- ✋ Jempol (ibu jari) **TERBUKA**
- ☝️ Telunjuk **TERBUKA**
- 🤙 Kelingking **TERBUKA**
- 🤞 Jari tengah & manis **TERTEKUK**

**Efek Partikel:**
- 🎬 Tampilkan teks **"I LOVE YOU"** yang tersusun dari partikel
- Animasi teks dengan efek 3D yang mengalir halus
- Partikel bergerak dengan smooth lerping ke posisi target

**Kegunaan:** Ekspresikan cinta/kasih sayang dengan cara futuristik! ✨

---

#### 2. **ROCK ON** 🤘 (Heavy Metal Sign)
**Bentuk Gesture:**
- ☝️ Telunjuk **TERBUKA**
- 🤙 Kelingking **TERBUKA**
- 👊 Jempol **TERTEKUK**
- 🤞 Jari tengah & manis **TERTEKUK**

**Efek Partikel:**
- 🔺 Tampilkan **piramida 3D** yang tersusun dari partikel
- Piramida berputar dan merespons gerakan tangan
- Efek dinamis saat tangan bergerak

**Kegunaan:** Gesture rock and roll! 🎸

---

#### 3. **OK SIGN** 👌
**Bentuk Gesture:**
- 👌 Jempol & telunjuk **BERSENTUHAN** (membentuk O)
- ✋ Jari tengah, manis, kelingking **TERBUKA**

**Efek Partikel:**
- 💎 Tampilkan **diamond 3D** yang berkilau dari partikel
- Bentuk berubah mengikuti gerakan tangan dengan responsif

**Kegunaan:** Gesture persetujuan/OK! 

---

#### 4. **PEACE** ✌️ (Victory Sign)
**Bentuk Gesture:**
- ☝️ Telunjuk **TERBUKA**
- 📌 Jari tengah **TERBUKA**
- 👊 Jempol, manis, kelingking **TERTEKUK**

**Efek Partikel:**
- ♾️ Tampilkan **infinity sign** dari partikel yang mengalir
- Animasi endless-loop yang elegan

**Kegunaan:** Gesture peace/kemenangan! 🎉

---

#### 5. **POINTING** 👉 (Index Finger Only)
**Bentuk Gesture:**
- ☝️ Telanjuk **TERBUKA** - menunjuk
- 👊 Semua jari lain **TERTEKUK**

**Efek Partikel:**
- 🔷 Tampilkan **silinder 3D** yang tercipta dari partikel
- Silinder mengikuti arah telunjuk yang menunjuk

**Kegunaan:** Gesture penunjukan/arahan!

---

#### 6. **FIST UP / FIST DOWN** ✊ (Kepalan Tangan)
**Bentuk Gesture:**
- ✊ **SEMUA JARI TERTEKUK** membentuk kepalan
- Posisi tangan ke atas (FIST_UP) atau ke bawah (FIST_DOWN)

**Efek Partikel:**

**FIST_UP (Kepalan ke atas):**
- 💗 Tampilkan **big heart** (hati besar) yang meledak dari partikel
- Efek yang energik dan penuh semangat!

**FIST_DOWN (Kepalan ke bawah):**
- 🌌 Tampilkan **black hole** yang menyedot partikel
- Partikel tertarik ke pusat dengan efek gravitasi yang misterius

**Kegunaan:** Ekspresikan emosi kuat! 💪

---

#### 7. **C SHAPE** 🤲 (Huruf C - Tangan Melengkung)
**Bentuk Gesture:**
- 🤲 Jari-jari **MELENGKUNG SEBAGIAN** (semi-curled, seperti memegang gelas)
- 👍 Jempol membentuk gap dengan telunjuk (spacing 0.35-1.0)
- Jari tidak penuh tergenggam, tapi juga tidak lurus

**Efek Partikel:**
- 🪐 Tampilkan **planet/Mars** dengan efek berbintik-bintik
- Partikel membentuk permukaan planet yang menggelembung
- Gravitasi dan rotasi dinamis sesuai gerakan tangan

**Kegunaan:** Gesture yang artistic dan natural! 🌍

---

#### 8. **OPEN PALM** ✋ (Telapak Tangan Terbuka)
**Bentuk Gesture:**
- ✋ **SEMUA JARI TERBUKA LEBAR** (5 jari mengembang)
- Posisi relaks dan natural

**Efek Partikel:**
- ⭐ Tampilkan **starfield** - ribuan bintang bergerak
- Partikel menyebar seperti bintang-bintang di luar angkasa
- Efek kosmik yang menakjubkan!

**Kegunaan:** Mode neutral dengan efek keren! 🌠

---

### 💪 KOMBINASI DUAL-HAND (Two Hands)

Sistem dapat mendeteksi **dua tangan sekaligus**! Kombinasi gesture spesial dengan efek lebih dahsyat:

| Kombinasi | Efek Partikel |
|---|---|
| **LOVE + LOVE** ❤️❤️ | Teks **"I LOVE YOU"** besar dengan efek sparkle |
| **OPEN_PALM + OPEN_PALM** 🌟🌟 | **SUPERNOVA** - ledakan partikel spektakuler! |
| **FIST_UP + FIST_UP** 💗💗 | **BIG HEART** - hati raksasa yang berdenyut |
| **FIST_DOWN + FIST_DOWN** 🌌🌌 | **BLACK HOLE** - singularitas penyedot partikel |
| **PEACE + PEACE** ♾️♾️ | **INFINITY SIGN** - simbol tak terbatas |
| **OK_SIGN + OK_SIGN** 💎💎 | **DIAMOND 3D** - berlian kristal besar |
| **POINTING + POINTING** 🔷🔷 | **CYLINDER 3D** - silinder 3D yang imposing |
| **ROCK_ON + ROCK_ON** 🔺🔺 | **PYRAMID 3D** - piramida raksasa |
| **C_SHAPE + C_SHAPE** 🪐🪐 | **MARS** - planet Mars dengan detail lebih banyak |
| **FIST_UP + OPEN_PALM** (Mixed) 🎆 | **PLANET** - planet dengan orbit dan efek khusus |

---

## 🎮 Fitur Interaktif

### Particle System
Setiap partikel memiliki:
- **Current Position (posisi saat ini)** - posisi real-time partikel
- **Target Position (target posisi)** - posisi tujuan partikel
- **Smooth Lerping** - transisi smooth antar target tanpa teleport
- **Hand Repulsion** - partikel terdorong saat tangan mendekat, lalu kembali ke formasi

### Physics Engine
- **Lerp Factor (PARTICLE_LERP_FACTOR)** = 0.08 - menentukan smooth animasi
- **Jumlah Partikel (PARTICLE_COUNT)** = 1400 - detail tinggi
- **Stiffness & Damping** - mencegah partikel terlalu kasar atau terlalu lambat
- **Mass** - setiap partikel punya massa yang unik

### Shockwave & Spark System
- **Stardust Spark Emitter** - spark yang terpancar saat gesture berubah
- **Plasma Beam** - efek cahaya antar partikel
- **Shockwave Speed** = 1200.0 - gelombang eksplosif

---

## ⚙️ Konfigurasi & Kalibrasi

Edit file `config.py` untuk menyesuaikan:

```python
# --- Kamera ---
FRAME_WIDTH = 1280      # Lebar frame video
FRAME_HEIGHT = 720      # Tinggi frame video
MIRROR_CAMERA = True    # Cerminkan video (lebih natural)

# --- Performance ---
TARGET_FPS = 120        # Target frame rate (120 FPS untuk smooth)
PARTICLE_COUNT = 1400   # Jumlah partikel (↑ = lebih detail, ↓ = lebih cepat)
PARTICLE_LERP_FACTOR = 0.08  # Smooth lerping (0.0-1.0)

# --- Deteksi Gesture ---
GESTURE_BUFFER_SIZE = 5       # Jumlah frame untuk stabilisasi
MIN_VOTES_RATIO = 0.5         # Persentase akurasi minimum
MIN_DETECTION_CONFIDENCE = 0.60  # Kepercayaan deteksi hand
MIN_TRACKING_CONFIDENCE = 0.60   # Kepercayaan tracking tangan

# --- Visual ---
DRAW_HAND_LANDMARKS = True  # Tampilkan kerangka tangan
SHOW_FPS = True            # Tampilkan FPS counter
```

### Jika Gesture Tidak Terdeteksi dengan Baik:
1. **Cek pencahayaan** - pastikan cahaya cukup
2. **Tingkatkan `GESTURE_BUFFER_SIZE`** - gesture lebih stabil tapi delay lebih tinggi
3. **Turunkan `MIN_DETECTION_CONFIDENCE`** - detector lebih sensitif (tapi mungkin false positive)
4. **Kalibrasikan gesture di `gesture_detector.py`** - sesuaikan threshold curl ratio

---

## 🎨 Struktur Project

```
just-fun-bro/
├── main.py                      # 🎬 Entry point, capture webcam, render
├── gesture_detector.py          # 🤖 Deteksi & klasifikasi gesture
├── overlay_utils.py             # ✨ Particle system engine
├── config.py                    # ⚙️ Semua parameter kalibrasi
├── requirements.txt             # 📦 Dependencies
├── models/
│   └── hand_landmarker.task     # 🧠 Model MediaPipe (auto-download)
├── assets/
│   └── cakrawala_logo.png       # 🏫 Logo kampus (optional)
├── video_frames/                # 📹 Capture frame (auto-generated)
└── DOKUMENTASI_LENGKAP.md       # 📚 Dokumentasi ini
```

---

## 🔧 Troubleshooting

### ❌ Program crash dengan error MediaPipe
**Solusi:**
- Pastikan file `models/hand_landmarker.task` ada di folder `models/`
- Jika belum ada, pastikan koneksi internet aktif saat pertama kali run
- Manual download: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

### ❌ Gesture tidak terdeteksi dengan konsisten
**Solusi:**
- Tekan **R** untuk reset buffer gesture
- Gerakkan tangan lebih lambat dan jelas
- Tingkatkan pencahayaan di sekitar Anda
- Kalibrasikan ulang di `gesture_detector.py`

### ❌ Program lag/FPS rendah
**Solusi:**
- Turunkan `PARTICLE_COUNT` di `config.py` (e.g., dari 1400 ke 800)
- Turunkan `FRAME_WIDTH` & `FRAME_HEIGHT` untuk resolusi lebih rendah
- Tutup aplikasi background lain

### ❌ Webcam tidak terdeteksi
**Solusi:**
- Pastikan webcam sudah connect ke laptop
- Cek di Device Manager (Windows) atau System Preferences (Mac)
- Ubah `CAMERA_INDEX` di `config.py` jika punya multiple cameras:
  ```python
  CAMERA_INDEX = 0  # Coba 0, 1, 2, dst.
  ```

---

## 📊 Bagaimana Sistem Kerja?

### 1️⃣ **Capture & Preprocessing**
- Video dari webcam ditangkap di 1280x720
- Jika `MIRROR_CAMERA = True`, video dicerminkan (lebih natural)
- Konversi dari BGR (OpenCV) ke RGB (MediaPipe)

### 2️⃣ **Hand Detection**
- MediaPipe HandLandmarker mendeteksi **sampai 2 tangan** sekaligus
- Extract **21 landmark points** per tangan (pergelangan hingga ujung jari)
- Confidence threshold untuk filtering deteksi palsu

### 3️⃣ **Gesture Classification**
- Hitung **finger states** (lurus/tertekuk) berdasarkan jarak landmark
- Hitung **curl ratio** untuk gesture seperti C_SHAPE
- Gunakan **majority-vote buffer** untuk stabilisasi (5 frame terakhir)
- Hasilkan label gesture yang stabil

### 4️⃣ **Dual-Hand Combo Resolution**
- Jika 2 tangan terdeteksi, resolve kombinasi gesture
- Misal: LOVE + LOVE → TEXT (teks I LOVE YOU lebih besar)

### 5️⃣ **Particle Physics Simulation**
- Setiap partikel punya posisi saat ini & target posisi
- **Smooth Lerping**: `current_pos += (target_pos - current_pos) * lerp_factor`
- **Hand Repulsion**: Partikel yang dekat tangan terdorong radius tertentu
- Update velocity & posisi berdasarkan physics engine

### 6️⃣ **3D Rendering**
- Partikel diproyeksikan ke 2D screen menggunakan perspective projection
- Alpha blending dengan background video
- Render hand landmarks skeleton (jika `DRAW_HAND_LANDMARKS = True`)

### 7️⃣ **Display**
- Overlay partikel di atas video webcam
- Show FPS counter (jika `SHOW_FPS = True`)
- Output ke layar (120 FPS target)

---

## 🎓 Tips & Tricks

### ✅ Untuk Deteksi Gesture Terbaik:
1. **Gesture with confidence** - tunjukkan gesture dengan jelas dan penuh percaya diri
2. **Good lighting** - pencahayaan yang bagus sangat membantu
3. **Smooth movements** - gerakan tangan yang halus, bukan tiba-tiba
4. **Keep hand in frame** - pastikan tangan tetap visible di webcam

### ✅ Untuk Efek Partikel Maksimal:
1. **Gunakan kombinasi dual-hand** - efek lebih spektakuler!
2. **Move your hand around** - gerakan tangan membuat partikel bergerak menarik
3. **Mix different gestures** - coba berbagai kombinasi untuk efek unik
4. **Use repulsion effect** - letakkan tangan di tengah partikel untuk efek dorong

### ✅ Development:
1. **Tambah gesture baru** di `gesture_detector.py` → `classify()` method
2. **Tambah particle mode** di `overlay_utils.py` → `ParticleSystem.MODES`
3. **Kalibrasi gesture** dengan adjusting threshold di `_is_c_shape()`, dll.

---

## 📞 Support & Credits

**Framework:**
- MediaPipe (Google) - Hand detection
- OpenCV - Video processing
- NumPy - Numerical computation
- Pillow - Image handling

**Built with:** Python 3.10+

---

**Selamat mencoba! Enjoy the interactive hand gesture particle system! 🎉✨**
