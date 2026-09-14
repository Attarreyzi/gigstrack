# 🎸 GigTrack - Live Music & Gigs Radar

Platform pelacak gig dan konser musik live untuk menemukan jadwal band yang tampil **hari ini**, besok, maupun jadwal mendatang berdasarkan genre, musisi, venue, dan kota.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Django 5.x, Django REST Framework (DRF), `django-filter`, `django-cors-headers`
- **Frontend**: React.js, Vite, Vanilla CSS Modern (Dark Mode Aesthetic)
- **Database**: SQLite (Local Development) & PostgreSQL (Production/Docker Ready)
- **Container**: Docker & Docker Compose

---

## 🚀 Panduan Menjalankan (Local Development Tanpa Docker)

### 1. Jalankan Backend (Django)

Buka terminal PowerShell baru, masuk ke folder `backend`:

```powershell
cd backend

# Buat virtual environment (opsional tapi direkomendasikan)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Jalankan migrasi database
python manage.py makemigrations
python manage.py migrate

# Masukkan data dummy realistis (Gigs hari ini & mendatang)
python seed_data.py

# Buat superuser untuk akses Django Admin (opsional)
python manage.py createsuperuser

# Jalankan server backend
python manage.py runserver 8000
```
Backend API akan berjalan di: `http://127.0.0.1:8000/api/`
Django Admin Panel di: `http://127.0.0.1:8000/admin/`

---

### 2. Jalankan Frontend (React + Vite)

Buka terminal baru lainnya, masuk ke folder `frontend`:

```powershell
cd frontend

# Install dependencies
npm install

# Jalankan development server
npm run dev
```
Buka browser di: `http://localhost:5173/`

---

## 🐳 Panduan Menjalankan dengan Docker (Opsional)

Jika Docker Desktop sudah terpasang di komputer kamu:

```powershell
# Jalankan seluruh stack (PostgreSQL + Django + React)
docker compose up --build
```
Semua service (database, backend, frontend) akan otomatis menyala dan saling terhubung!
