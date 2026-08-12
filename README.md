# Hand Gesture Detection System — Universitas Cakrawala

Sistem deteksi gesture tangan real-time pakai **MediaPipe HandLandmarker (Tasks API)** + **OpenCV**.

| Gesture terdeteksi | Aksi |
|---|---|
| Huruf **C** (tangan melengkung seperti memegang gelas) | Tampilkan planet neon berorbit |
| Kepalan tangan | Tampilkan hati neon |
| Tanda **Love** (ASL "I Love You": jempol + telunjuk + kelingking terbuka, jari tengah & manis terlipat) | Tampilkan teks **I LOVE YOU** |
| Telapak tangan terbuka | Ubah target partikel menjadi starfield |

## Struktur project

```
hand_gesture_system/
├── main.py              # entry point: capture webcam, render overlay
├── gesture_detector.py  # klasifikasi gesture dari landmark tangan
├── overlay_utils.py      # alpha-blending logo/hati ke frame + fallback drawing
├── config.py             # semua parameter/threshold yang bisa dikalibrasi
├── requirements.txt
├── models/                # dibuat otomatis; berisi hand_landmarker.task
└── assets/
    └── cakrawala_logo.png   # <-- TARUH LOGO KAMPUS DI SINI (PNG transparan)
```

## Instalasi

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

MediaPipe versi terbaru sudah tidak menyediakan `mp.solutions.hands`. Program ini
memakai Tasks API dan akan mengunduh `models/hand_landmarker.task` otomatis saat
pertama kali dijalankan. Jika jaringan dibatasi, unduh file model tersebut dan
letakkan di lokasi itu secara manual.

## Particle System interaktif

Setiap partikel menyimpan `current_pos` dan `target_pos`. Pada setiap frame,
posisinya bergerak memakai LERP sehingga transisi bentuk tidak teleportasi.
Target yang tersedia adalah starfield, hati, teks `I LOVE YOU`, dan planet.
Posisi pergelangan tangan dipakai sebagai gaya repel: partikel di sekitar tangan
akan terdorong, berputar, lalu kembali membentuk target setelah tangan menjauh.
Panel kamera hanya menampilkan kerangka koneksi tulang tangan agar fokus tetap
pada tracking, tanpa icon gesture atau tulisan tambahan.

Pemetaan mode:

- Gesture C → planet berorbit.
- Kepalan → bentuk hati.
- Gesture Love → teks `I LOVE YOU`.
- Telapak terbuka → starfield.

Jumlah partikel dan kecepatan transisi bisa dikalibrasi melalui
`PARTICLE_COUNT` dan `PARTICLE_LERP_FACTOR` di `config.py`.

## Menjalankan

```bash
python main.py
```

- Tekan **q** untuk keluar.
- Tekan **r** untuk reset buffer gesture (kalau deteksi kepenceng/nyangkut di label yang salah).

## Menambahkan logo asli

Program **tidak akan crash** kalau logo belum ada — otomatis pakai placeholder
lingkaran "UC". Begitu file `assets/cakrawala_logo.png` (PNG dengan alpha
channel/transparan) tersedia, program otomatis pakai logo asli tanpa perlu
ubah kode apa pun.

## Cara kerja deteksi (ringkas)

1. **MediaPipe Hands** mengekstrak 21 titik landmark tangan per frame.
2. `gesture_detector.py` menghitung:
   - **Status tiap jari** (lurus/tidak) berdasarkan jarak wrist→tip vs wrist→pip.
   - **Curl ratio** tiap jari (dipakai khusus untuk mendeteksi huruf C —
     jari harus menekuk *sebagian*, tidak lurus penuh dan tidak menggenggam penuh).
   - **Celah jempol-telunjuk** (memastikan bentuk C, bukan gesture "OK" yang menempel).
3. Hasil klasifikasi mentah dimasukkan ke **buffer majority-vote** (`GESTURE_BUFFER_SIZE`
   frame terakhir) supaya output stabil dan tidak flicker akibat noise landmark.
4. `overlay_utils.py` menempelkan gambar dengan alpha blending yang benar
   (bukan sekadar overwrite pixel) + clipping supaya tidak crash walau posisi
   overlay keluar dari batas frame.

## Kalibrasi

Kalau di kondisi pencahayaan/ukuran tangan lu deteksinya kurang akurat, ubah
nilai-nilai berikut di `config.py` atau langsung di `gesture_detector.py`:

- `GESTURE_BUFFER_SIZE`, `MIN_VOTES_RATIO` — seberapa "lama" gesture harus
  konsisten sebelum dianggap valid.
- Range curl ratio di `_is_c_shape()` (default `1.0–1.55`) dan range gap
  jempol-telunjuk (default `0.35–1.1`) — sesuaikan kalau bentuk C susah kedetect
  atau malah kesenggol gesture lain.

## Testing tanpa webcam

Logic classifier sudah divalidasi pakai data landmark sintetis (tanpa perlu
kamera) — cek pola pengujian serupa kalau mau nambah gesture baru:
buat 21 titik landmark palsu, panggil `GestureClassifier.classify()`, dan
assert label yang keluar sesuai ekspektasi.

## Menambahkan gesture baru

1. Tambah method `_is_<nama_gesture>()` di `gesture_detector.py` yang
   menerima `landmarks` (dan/atau `FingerState`) lalu return `bool`.
2. Tambahkan ke percabangan di `classify()`.
3. Tambah rendering-nya di `main.py` (overlay/teks sesuai label baru).

## Catatan penting (biar ga salah paham)

- Program pakai **1 tangan** secara default (`MAX_NUM_HANDS = 1` di `config.py`).
  Ganti ke 2 kalau mau deteksi dua tangan sekaligus (misal gesture hati pakai 2 tangan).
- Threshold di atas dikalibrasi dengan estimasi geometris umum — kemungkinan
  perlu sedikit fine-tuning di kondisi kamera/pencahayaan asli lu. Cara paling
  gampang: nyalain `DRAW_HAND_LANDMARKS = True` (default sudah aktif), amati
  titik-titik landmark real-time, lalu sesuaikan angka di `config.py`.
