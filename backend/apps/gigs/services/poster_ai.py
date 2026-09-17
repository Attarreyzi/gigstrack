import os
import json
import re
import logging
from datetime import datetime, time
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from google import genai
from google.genai import types

from apps.gigs.models import Gig, GigLineup, GigTicketTier, GigStatus
from apps.venues.models import Venue
from apps.artists.models import Artist, Genre

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Anda adalah asisten AI ahli yang bertugas menganalisis gambar poster/pamflet konser musik di Indonesia (Instagram poster, festival flyer, gigs poster).
Tugas Anda adalah membaca dan mengekstrak semua informasi penting dari poster ini dengan sangat akurat dan mengembalikannya HANYA dalam format JSON murni.

Struktur JSON yang WAJIB dihasilkan:
{
    "title": "Nama resmi acara/konser/festival",
    "artists": ["Nama Band/Musisi 1", "Nama Band/Musisi 2", ...],
    "headliner": "Nama musisi/band utama jika jelas terlihat, atau null",
    "venue_name": "Nama venue / tempat acara (contoh: M Bloc Space, GBK Senayan, Rossi Musik, Synchronize Field)",
    "city": "Kota acara (contoh: Jakarta, Bandung, Yogyakarta, Surabaya, Denpasar, Medan, dll)",
    "address": "Alamat spesifik jika tertulis, atau gabungkan dengan kota",
    "date": "YYYY-MM-DD (format tahun-bulan-tanggal. Jika tahun tidak tertulis, gunakan tahun saat ini/mendatang 2026/2027)",
    "time": "HH:MM (format 24 jam waktu mulai jika ada, contoh: 19:00, atau null)",
    "doors_open": "Waktu open gate / doors open (contoh: 18:30 WIB)",
    "ticket_price": 0, // Harga termurah / mulai dari (angka integer rupiah, contoh: 150000). Jika gratis tulis 0.
    "is_free": false, // true jika ada tulisan Free Entry, HTM: Free, Gratis, Donasi
    "ticket_tiers": [
        // Ekstrak SEMUA kategori tiket yang tertera (Early Bird, Presale 1, Presale 2, Regular, VIP, Daily Pass, 3-Day Pass, OTS, dll)
        {
            "tier_name": "Nama Kategori (contoh: Presale 1 / Early Bird / 3-Day Pass / VIP)",
            "price": 250000, // Angka integer rupiah
            "is_sold_out": false, // true jika ada cap SOLD OUT / HABIS
            "description": "Keterangan opsional (misal: Akses 3 Hari / Daily Pass)"
        }
    ],
    "ticket_url": "URL pembelian tiket jika tertera (contoh: loket.com/..., tiket.com/..., atau null)",
    "genres": ["Indie Rock", "Pop", "Metal", "Punk", ...], // Perkiraan genre musik dari band yang tertera
    "description": "Ringkasan informasi acara dan lineup lengkap untuk deskripsi",
    "confidence_score": 0.95 // Nilai 0.0 - 1.0 seberapa jelas poster terbaca
}

PENTING:
1. Pastikan nama artis/band diekstrak secara terpisah dan bersih dari kata tambahan seperti 'Feat', 'With', 'Presenting'.
2. Jika acara adalah FESTIVAL dengan banyak harga (Presale 1, Presale 2, VIP, dll), ekstrak SEMUA tier ke array 'ticket_tiers'.
3. Format tanggal WAJIB YYYY-MM-DD. Terjemahkan nama bulan Indonesia.
4. Hanya kembalikan valid JSON string tanpa teks pengantar atau penutup apapun.
"""


class PosterAIService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', None)
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY belum dikonfigurasi di file .env atau settings.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = 'gemini-3.6-flash'

    def analyze_poster(self, image_bytes: bytes, mime_type: str = 'image/jpeg') -> dict:
        """
        Menganalisis gambar poster menggunakan Gemini Vision API.
        Mengembalikan dictionary data konser yang sudah dinormalisasi dan divalidasi.
        """
        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    image_part,
                    SYSTEM_PROMPT + "\n\nAnalisis poster di atas dan keluarkan format JSON murni:"
                ]
            )

            raw_text = response.text.strip() if response.text else "{}"
            
            # Bersihkan blok markdown ```json jika ada
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
                raw_text = re.sub(r"```\s*$", "", raw_text, flags=re.MULTILINE)
            
            parsed_data = json.loads(raw_text.strip())
            return self.normalize_extracted_data(parsed_data)

        except json.JSONDecodeError as jde:
            logger.error(f"Gagal parse response Gemini ke JSON: {jde}")
            return {
                "success": False,
                "error": "Hasil AI tidak dapat dibaca sebagai format JSON yang valid.",
                "raw_response": str(raw_text) if 'raw_text' in locals() else None
            }
        except Exception as e:
            logger.error(f"Error pada analyze_poster Gemini Vision: {e}")
            return {
                "success": False,
                "error": f"Gagal menganalisis poster: {str(e)}"
            }

    def apply_corrections(self, current_data: dict, correction_instruction: str) -> dict:
        """
        Memperbarui data konser berdasarkan instruksi teks alami dari user.
        Contoh: 'Ubah tanggal jadi 25 November 2026', 'Ganti harga tiket jadi 150rb', 'Venue di M Bloc Space Jakarta'
        """
        correction_prompt = f"""
        Berikut adalah data konser musik saat ini:
        {json.dumps(current_data, indent=2, ensure_ascii=False)}

        Instruksi koreksi dari user:
        "{correction_instruction}"

        Tugas Anda:
        Perbarui data JSON di atas berdasarkan instruksi koreksi dari user dengan sangat teliti.
        Pertahankan data lama untuk field yang TIDAK disebutkan dalam instruksi koreksi.

        Format JSON yang WAJIB dihasilkan (HANYA valid JSON murni):
        {{
            "title": "Nama resmi acara",
            "artists": ["Nama Band 1", "Nama Band 2"],
            "headliner": "Nama band utama atau null",
            "venue_name": "Nama venue",
            "city": "Kota",
            "address": "Alamat",
            "date": "YYYY-MM-DD",
            "time": "HH:MM",
            "doors_open": "18:30 WIB",
            "ticket_price": 150000,
            "is_free": false,
            "ticket_url": "URL tiket",
            "genres": ["Indie Rock", ...],
            "description": "Deskripsi acara",
            "confidence_score": 1.0
        }}
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    correction_prompt + "\n\nKeluarkan format JSON murni yang sudah dikoreksi:"
                ]
            )

            raw_text = response.text.strip() if response.text else "{}"
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
                raw_text = re.sub(r"```\s*$", "", raw_text, flags=re.MULTILINE)

            parsed_data = json.loads(raw_text.strip())
            return self.normalize_extracted_data(parsed_data)
        except Exception as e:
            logger.error(f"Error pada apply_corrections: {e}")
            return current_data

    def normalize_extracted_data(self, data: dict) -> dict:

        """
        Normalisasi dan validasi data konser hasil ekstraksi LLM.
        """
        title = (data.get("title") or "Konser Musik Indonesia").strip()
        artists = [a.strip() for a in data.get("artists", []) if a and isinstance(a, str) and a.strip()]
        headliner = data.get("headliner")
        venue_name = (data.get("venue_name") or "Venue Jakarta").strip()
        city = (data.get("city") or "Jakarta").strip()
        address = (data.get("address") or f"{venue_name}, {city}").strip()
        
        # Normalisasi Tanggal & Jam
        date_str = data.get("date")
        time_str = data.get("time") or "19:00"
        
        # Validasi format tanggal YYYY-MM-DD
        start_datetime = None
        if date_str:
            try:
                # Match YYYY-MM-DD
                match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
                if match:
                    y, m, d = map(int, match.groups())
                    # Jam & menit
                    t_match = re.search(r'(\d{1,2}):(\d{1,2})', time_str)
                    hour, minute = (int(t_match.group(1)), int(t_match.group(2))) if t_match else (19, 0)
                    
                    dt = datetime(y, m, d, hour, minute)
                    start_datetime = timezone.make_aware(dt) if timezone.is_naive(dt) else dt
            except Exception as ex:
                logger.warning(f"Error parsing date {date_str}: {ex}")

        # Fallback jika tanggal tidak valid (default: 7 hari dari sekarang)
        if not start_datetime:
            future_date = timezone.now() + timezone.timedelta(days=7)
            start_datetime = future_date.replace(hour=19, minute=0, second=0, microsecond=0)
            date_str = start_datetime.strftime('%Y-%m-%d')

        # Normalisasi Harga Tiket
        # Normalisasi Harga Tiket & Ticket Tiers
        raw_price = data.get("ticket_price", 0)
        is_free = bool(data.get("is_free", False))
        
        def parse_price(val):
            try:
                if isinstance(val, str):
                    p_clean = val.lower().replace("rp", "").replace(".", "").replace(",", "").strip()
                    if "k" in p_clean:
                        return int(float(p_clean.replace("k", "")) * 1000)
                    elif "rb" in p_clean:
                        return int(float(p_clean.replace("rb", "")) * 1000)
                    else:
                        digits = re.findall(r'\d+', p_clean)
                        return int(digits[0]) if digits else 0
                return int(val or 0)
            except Exception:
                return 0

        ticket_price = parse_price(raw_price)

        # Normalisasi Ticket Tiers
        raw_tiers = data.get("ticket_tiers", [])
        normalized_tiers = []
        if isinstance(raw_tiers, list):
            for idx, tier in enumerate(raw_tiers, start=1):
                if isinstance(tier, dict) and tier.get("tier_name"):
                    t_name = str(tier["tier_name"]).strip()
                    t_price = parse_price(tier.get("price", ticket_price))
                    t_sold_out = bool(tier.get("is_sold_out", False))
                    t_desc = str(tier.get("description", "")).strip()
                    normalized_tiers.append({
                        "order": idx,
                        "tier_name": t_name,
                        "price": t_price,
                        "is_sold_out": t_sold_out,
                        "description": t_desc
                    })

        # Jika ada tiers, tentukan ticket_price sebagai harga termurah aktif
        if normalized_tiers:
            active_prices = [t["price"] for t in normalized_tiers if t["price"] > 0 and not t["is_sold_out"]]
            if active_prices:
                ticket_price = min(active_prices)
            elif any(t["price"] > 0 for t in normalized_tiers):
                ticket_price = min(t["price"] for t in normalized_tiers if t["price"] > 0)
            else:
                ticket_price = 0

        if ticket_price == 0 and not normalized_tiers:
            is_free = True

        # Normalisasi link tiket
        ticket_url = (data.get("ticket_url") or "").strip()
        if not ticket_url:
            q_term = (headliner or (artists[0] if artists else title)).strip()
            ticket_url = f"https://www.loket.com/search?q={q_term}"

        genres = [g.strip() for g in data.get("genres", []) if g and isinstance(g, str)]
        if not genres:
            genres = ["Indie Rock", "Pop"]

        description = (data.get("description") or f"Konser {title} menampilkan {', '.join(artists)} di {venue_name}, {city}.").strip()

        return {
            "success": True,
            "title": title,
            "artists": artists,
            "headliner": headliner,
            "venue_name": venue_name,
            "city": city,
            "address": address,
            "date": start_datetime.strftime('%Y-%m-%d'),
            "time": start_datetime.strftime('%H:%M'),
            "start_datetime_iso": start_datetime.isoformat(),
            "doors_open": data.get("doors_open") or "18:30 WIB",
            "ticket_price": ticket_price,
            "is_free": is_free,
            "ticket_tiers": normalized_tiers,
            "ticket_url": ticket_url,
            "genres": genres,
            "description": description,
            "confidence_score": float(data.get("confidence_score") or 0.9)
        }

    def save_gig_to_database(self, normalized_data: dict, poster_file=None) -> Gig:
        """
        Menyimpan data hasil AI langsung ke database Django (Venue, Artists, Genres, Gig, GigLineup, GigTicketTier).
        """
        # 1. Venue
        venue_name = normalized_data["venue_name"]
        city = normalized_data["city"]
        address = normalized_data.get("address") or f"{venue_name}, {city}"
        
        venue, _ = Venue.objects.get_or_create(
            name__iexact=venue_name,
            city__iexact=city,
            defaults={
                "name": venue_name,
                "city": city,
                "address": address,
                "province": f"Provinsi {city}",
                "is_active": True
            }
        )

        # 2. Genres
        genre_objs = []
        genre_colors = ["#FF3366", "#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#06B6D4"]
        for idx, g_name in enumerate(normalized_data.get("genres", [])):
            genre, _ = Genre.objects.get_or_create(
                name__iexact=g_name,
                defaults={
                    "name": g_name.title(),
                    "color": genre_colors[idx % len(genre_colors)]
                }
            )
            genre_objs.append(genre)

        # 3. Artists
        artist_objs = []
        for a_name in normalized_data.get("artists", []):
            artist, _ = Artist.objects.get_or_create(
                name__iexact=a_name,
                defaults={
                    "name": a_name,
                    "hometown": city,
                    "is_active": True
                }
            )
            if genre_objs:
                artist.genres.set(genre_objs)
            artist_objs.append(artist)

        # 4. Gig
        start_datetime = datetime.fromisoformat(normalized_data["start_datetime_iso"])
        if timezone.is_naive(start_datetime):
            start_datetime = timezone.make_aware(start_datetime)

        title = normalized_data["title"]
        slug_candidate = slugify(f"{title}-{start_datetime.strftime('%Y%m%d')}")
        
        gig, created = Gig.objects.get_or_create(
            slug=slug_candidate,
            defaults={
                "title": title,
                "venue": venue,
                "start_datetime": start_datetime,
                "doors_open": normalized_data.get("doors_open", "18:30 WIB"),
                "ticket_price": normalized_data.get("ticket_price", 0),
                "is_free": normalized_data.get("is_free", False),
                "ticket_url": normalized_data.get("ticket_url", ""),
                "description": normalized_data.get("description", ""),
                "status": GigStatus.SCHEDULED,
                "is_featured": True
            }
        )

        if not created:
            gig.title = title
            gig.venue = venue
            gig.start_datetime = start_datetime
            gig.ticket_price = normalized_data.get("ticket_price", gig.ticket_price)
            gig.is_free = normalized_data.get("is_free", gig.is_free)
            gig.ticket_url = normalized_data.get("ticket_url", gig.ticket_url)
            gig.description = normalized_data.get("description", gig.description)

        if poster_file:
            gig.poster = poster_file
        
        gig.save()

        # 5. Lineups
        headliner_name = normalized_data.get("headliner", "")
        for order, artist in enumerate(artist_objs, start=1):
            is_hl = (headliner_name and headliner_name.lower() in artist.name.lower()) or (order == 1)
            GigLineup.objects.get_or_create(
                gig=gig,
                artist=artist,
                defaults={
                    "order": order,
                    "is_headliner": is_hl,
                    "set_time": f"{19 + order - 1}:00 - {19 + order}:00 WIB"
                }
            )

        # 6. Ticket Tiers
        for tier_data in normalized_data.get("ticket_tiers", []):
            GigTicketTier.objects.update_or_create(
                gig=gig,
                tier_name__iexact=tier_data["tier_name"],
                defaults={
                    "tier_name": tier_data["tier_name"],
                    "price": tier_data.get("price", 0),
                    "is_sold_out": tier_data.get("is_sold_out", False),
                    "description": tier_data.get("description", ""),
                    "order": tier_data.get("order", 1)
                }
            )

        return gig

