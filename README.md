# GigTrack — Live Music & Indie Gigs Radar

> Platform pelacak gig dan konser musik langsung (*live music radar*) berskala nasional untuk memantau jadwal band yang tampil **hari ini**, jadwal akhir pekan, rundown susunan panggung, dan tiket di berbagai kota (Jakarta, Bandung, Bali, dll).

---

## Architecture & Tech Stack

Proyek ini dibangun dengan menerapkan prinsip **Separation of Concerns (SoC)** dan **Clean Layered Architecture**:

```text
[ React Frontend (Vite) ]  ←── HTTP/JSON (CORS) ──→  [ Django REST Framework ]
         :                                                      :
    LocalStorage                                          Django ORM
  (Saved Bookmarks)                                             :
                                                    [ SQLite / PostgreSQL ]
```

- **Backend**: Python 3.14, Django 5.x, Django REST Framework (DRF), `django-cors-headers`, `django-filter`, Pillow.
- **Frontend**: React.js 18, Vite, Vanilla CSS Design System (*Glassmorphism, Dark-mode music festival theme, SVG Vector Icons*).
- **Database**: SQLite (Zero-config local development) & PostgreSQL (Production/Docker Ready).
- **DevOps & QA**: Docker, Docker Compose, Automated Unit Testing (`django.test.TestCase`).

---

## Fitur Utama

1. **Real-time Live Radar**: Deteksi otomatis konser yang berlangsung Hari Ini berdasarkan tanggal server lokal (`timezone.localdate()`).
2. **Pencarian & Multi-Filter**: Pencarian nama band (*The Adams, .Feast, Reality Club, dll*), nama venue, filter kota dinamis, filter genre musik, dan filter tiket gratis (*Free Entry*).
3. **Rundown Timetable**: Modal detail yang menyajikan susunan jam tampil (*set time*) tiap band, status headliner, alamat venue, dan tautan Google Maps.
4. **Bookmark Favorit**: Kemampuan menyimpan konser ke daftar favorit pengguna menggunakan `localStorage` browser.
5. **Django Admin CMS**: Dashboard pengelolaan data band, venue, poster konser, dan rundown susunan acara secara terintegrasi.
6. **Automated Unit Testing**: Pengujian otomatis untuk memvalidasi akurasi query tanggal, filter wilayah, dan pencarian band.

---

## Struktur Repositori

```text
GigTrack/
├── backend/
│   ├── apps/
│   │   ├── artists/          # Model Genre & Artist, Serializer, ViewSet, Admin
│   │   ├── venues/           # Model Venue, Alamat, Kota, Serializer, ViewSet
│   │   └── gigs/             # Model Gig & GigLineup, Views (/today/, /cities/), Tests
│   ├── config/               # Settings, Routing URLs, WSGI, ASGI
│   ├── seed_data.py          # Script seeder data konser realistis
│   ├── requirements.txt      # Dependensi Python
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/       # Navbar, TodayRadar, FilterBar, GigCard, GigModal, Footer
│   │   ├── services/         # API HTTP Client (fetch wrapper)
│   │   ├── App.jsx           # State management & layout
│   │   └── index.css         # Custom Design System
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml        # Orkestrasi Docker (Postgres, Django, React)
├── .gitignore
└── README.md
```

---

## Panduan Menjalankan (Local Development)

### 1. Menjalankan Backend (Django)

Buka terminal di folder `backend`:

```powershell
cd backend

# 1. Jalankan migrasi database
.\venv\Scripts\python.exe manage.py makemigrations
.\venv\Scripts\python.exe manage.py migrate

# 2. Masukkan data konser awal (Data Hari Ini, Besok, & Mendatang)
.\venv\Scripts\python.exe seed_data.py

# 3. Jalankan server backend
.\venv\Scripts\python.exe manage.py runserver
```
* Backend API aktif di: `http://127.0.0.1:8000/api/`
* Django Admin Portal: `http://127.0.0.1:8000/admin/`

---

### 2. Menjalankan Frontend (React + Vite)

Buka terminal di folder `frontend`:

```powershell
cd frontend

# Install dependensi
npm install

# Jalankan server frontend
npm run dev
```
* Akses aplikasi web di browser: **`http://localhost:5173/`**

---

## Menjalankan Automated Unit Tests

Untuk memverifikasi keandalan API, filter tanggal, dan logika pencarian:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py test apps.gigs
```

Hasil pengujian otomatis:
```text
Creating test database for alias 'default'...
.....
----------------------------------------------------------------------
Ran 5 tests in 0.127s

OK
Destroying test database for alias 'default'...
```

---

## Lisensi
Proyek ini dibuat untuk keperluan portofolio Software Engineering dan bersifat Open Source di bawah lisensi MIT.
