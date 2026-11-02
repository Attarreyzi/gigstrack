import os
import json
import re
import logging
import time
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from google import genai
from google.genai import types


from apps.gigs.models import Gigs, GigsLineup, GigsTicketTier, GigsTicketLink, GigsStatus
from apps.venues.models import Venue
from apps.artists.models import Artist, Genre

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Anda adalah asisten AI ahli yang bertugas menganalisis gambar poster/pamflet konser musik di Indonesia (Instagram poster, festival flyer, Gigss poster).
Tugas Anda adalah membaca dan mengekstrak semua informasi penting dari poster ini dengan sangat akurat dan mengembalikannya HANYA dalam format JSON murni.

Struktur JSON yang WAJIB dihasilkan:
{
    "title": "Nama resmi acara/konser/festival",
    "artists": ["Nama Band/Musisi 1", "Nama Band/Musisi 2", ...],
    "headliner": "Nama musisi/band utama jika jelas terlihat, atau null",
    "lineups": [
        // Ekstrak detail artis per hari/rundown festival jika tertera di poster/flyer
        {
            "artist_name": "Nama Band/Musisi",
            "day": "Day 1 / Day 2 / Day 3 (HANYA jika tertera pembagian hari di poster, contoh: 'Day 1', 'Day 2'. Jika acara 1 hari biasa, isi null)",
            "set_time": "Jam tampil musisi jika tertulis di rundown (contoh: '19:30 WIB'). Jika tidak ada info jam tampil, isi 'TBA'",
            "is_headliner": false
        }
    ],
    "venue_name": "Nama venue / tempat acara (contoh: M Bloc Space, GBK Senayan, Rossi Musik, Synchronize Field)",
    "city": "Kota acara (contoh: Jakarta, Bandung, Yogyakarta, Surabaya, Denpasar, Medan, dll)",
    "address": "Alamat spesifik jika tertulis, atau gabungkan dengan kota",
    "date": "YYYY-MM-DD (format tahun-bulan-tanggal. Jika tahun tidak tertulis, gunakan tahun saat ini/mendatang 2026/2027)",
    "time": "HH:MM jika tertera, atau null jika belum ada info jam",
    "doors_open": "Waktu open gate / doors open HANYA jika tertulis di poster (contoh: '15:00 WIB'). Jika TIDAK TERTULIS di poster, isi 'TBA'. JANGAN mengarang jam jika tidak ada di poster!",
    "ticket_price": 0, // Harga termurah / mulai dari (angka integer rupiah, contoh: 150000). Jika gratis atau belum tertulis nominal harga di poster, tulis 0.
    "is_free": false, // WAJIB false KECUALI poster EKSPLISIT menuliskan kata 'FREE ENTRY', 'FREE', 'GRATIS', 'NO HTM', atau 'TANPA HTM'. Jika poster menyebutkan platform tiket (Goers, DetikEvent, Tiket.com, Loket, BBO, Artatix, Megatix, dll) meskipun nominal harga tidak tertulis, is_free WAJIB false!
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
    "ticket_platforms": ["GOERS", "Artatix", "detikevent"], // Ekstrak SEMUA nama platform/vendor tiket yang tertera di poster (contoh: GOERS, Artatix, detikevent, Loket, Tiket.com, BBO, Megatix, dll)
    "genres": ["Indie Rock", "Pop", "Metal", "Punk", ...], // Perkiraan genre musik dari band yang tertera

    "description": "Deskripsi singkat tema atau konsep acara (maksimal 1-2 kalimat). JANGAN mencantumkan daftar nama band penampil karena lineup sudah diekstrak tersendiri!",
    "confidence_score": 0.95 // Nilai 0.0 - 1.0 seberapa jelas poster terbaca
}

PENTING:
1. JANGAN mengarang Open Gate! Jika tidak ada tulisan jam buka gate/pintu, isi 'doors_open': 'TBA'.
2. Pastikan nama artis/band diekstrak secara terpisah dan bersih dari kata tambahan seperti 'Feat', 'With', 'Presenting'.
3. Jika acara adalah FESTIVAL dengan banyak harga (Presale 1, Presale 2, VIP, dll), ekstrak SEMUA tier ke array 'ticket_tiers'.
4. Format tanggal WAJIB YYYY-MM-DD. Terjemahkan nama bulan Indonesia.
5. Kolom 'description' HANYA untuk deskripsi singkat acara atau tema festival. JANGAN menyebutkan atau mengulang daftar nama lineup musisi di dalam deskripsi.
6. Hanya kembalikan valid JSON string tanpa teks pengantar atau penutup apapun.
"""



class PosterAIService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', None)
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY belum dikonfigurasi di file .env atau settings.")
        self.client = genai.Client(api_key=self.api_key)
        self.primary_model = 'gemini-3.8-flash'
        self.fallback_models = [
            'gemini-3.8-flash',
            'gemini-3.6-flash',
            'gemini-2.5-flash',
            'gemini-1.5-flash'
        ]


    def _generate_content_with_fallback(self, contents: list) -> str:
        """
        Mengeksekusi request ke Gemini API dengan dukungan auto-retry dan multi-model fallback.
        Jika model utama mengalami 503 UNAVAILABLE (High Demand), otomatis beralih ke model cadangan.
        """
        last_exception = None
        for model in self.fallback_models:
            for attempt in range(2):
                try:
                    logger.info(f"Memanggil Gemini API (Model: {model}, Percobaan: {attempt + 1})...")
                    response = self.client.models.generate_content(
                        model=model,
                        contents=contents
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as e:
                    last_exception = e
                    err_msg = str(e).lower()
                    logger.warning(f"Kendala pada model {model} (attempt {attempt + 1}): {e}")
                    if any(k in err_msg for k in ["503", "unavailable", "429", "high demand", "overloaded", "quota"]):
                        time.sleep(1.0)
                        continue
                    else:
                        time.sleep(0.5)

        raise last_exception or RuntimeError("Seluruh server model Gemini sedang sibuk. Silakan coba kembali dalam beberapa detik.")

    def analyze_poster(self, image_bytes: bytes = None, images_list: list = None, mime_type: str = 'image/jpeg') -> dict:
        """
        Menganalisis satu atau beberapa gambar poster sekaligus menggunakan Gemini Vision API.
        Mendukung multi-foto (misal Foto 1 = Poster Utama, Foto 2 = Daftar Tiket / Rundown).
        """
        try:
            image_parts = []
            if images_list and len(images_list) > 0:
                for item in images_list:
                    if isinstance(item, tuple) and len(item) == 2:
                        b_data, m_type = item
                        image_parts.append(types.Part.from_bytes(data=b_data, mime_type=m_type or mime_type))
                    elif isinstance(item, bytes):
                        image_parts.append(types.Part.from_bytes(data=item, mime_type=mime_type))
            elif image_bytes:
                image_parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
            else:
                return {
                    "success": False,
                    "error": "Tidak ada data gambar yang dikirimkan."
                }

            prompt_text = SYSTEM_PROMPT + "\n\nAnalisis seluruh gambar poster di atas secara komprehensif (gabungkan informasi jika ada beberapa foto) dan keluarkan HANYA format JSON murni:"

            raw_text = self._generate_content_with_fallback([*image_parts, prompt_text])
            
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
        Contoh: 'Ubah tanggal jadi 25 November 2026', 'Tiket beli di aplikasi BBO', 'Venue di M Bloc Space Jakarta'
        """
        correction_prompt = f"""
        Berikut adalah data konser musik saat ini:
        {json.dumps(current_data, indent=2, ensure_ascii=False)}

        Instruksi koreksi dari user:
        "{correction_instruction}"

        Tugas Anda:
        1. Perbarui data JSON di atas berdasarkan instruksi koreksi dari user dengan sangat teliti.
        2. PERINGATAN KERAS: WAJIB PERTAHANKAN seluruh data lama (termasuk seluruh isi array 'ticket_tiers', 'artists', 'genres', dll) secara utuh KECUALI jika secara spesifik diminta diubah oleh user dalam instruksi koreksi.
        3. Jika user menyebutkan platform tiket (misal: BBO, Loket, Tiket.com, Goers, TipTip), perbarui 'ticket_url' ke platform tersebut.

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
            "doors_open": "18:30 WIB atau TBA",
            "ticket_price": 5000,
            "is_free": false,
            "ticket_tiers": [
                {{
                    "tier_name": "Nama Kategori / Tier",
                    "price": 5000,
                    "is_sold_out": false,
                    "description": "Keterangan tier"
                }}
            ],
            "ticket_url": "URL tiket / platform",
            "genres": ["Indie Rock", "Pop"],
            "description": "Deskripsi acara",
            "confidence_score": 1.0
        }}
        """
        try:
            raw_text = self._generate_content_with_fallback([
                correction_prompt + "\n\nKeluarkan format JSON murni yang sudah dikoreksi:"
            ])
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
                raw_text = re.sub(r"```\s*$", "", raw_text, flags=re.MULTILINE)


            parsed_data = json.loads(raw_text.strip())

            # Safeguard: Pertahankan ticket_tiers dari current_data jika AI tidak mengembalikan ticket_tiers
            old_tiers = current_data.get("ticket_tiers", [])
            new_tiers = parsed_data.get("ticket_tiers", [])
            if old_tiers and (not new_tiers or len(new_tiers) == 0):
                # Periksa apakah user bermaksud menghapus tier (misal instruksi "ubah jadi gratis")
                if not any(kw in correction_instruction.lower() for kw in ["gratis", "free entry", "tanpa tiket"]):
                    parsed_data["ticket_tiers"] = old_tiers

            # Safeguard: Jika user mengoreksi link/platform tiket (misal BBO)
            if "bbo" in correction_instruction.lower():
                parsed_data["ticket_url"] = "https://www.bbo.co.id"

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

        # HANYA jadikan is_free = True jika secara eksplisit diset True dari AI / poster
        # (JANGAN menganggap otomatis gratis jika harga 0 tapi ada platform tiket)
        is_free = bool(data.get("is_free", False))

        # Safeguard: Jika terdeteksi platform tiket atau kata kunci berbayar (Goers, Artatix, Detikevent, Loket, Tiket, BBO, dll)
        # DAN tidak ada kata eksplisit 'free entry' / 'gratis', maka is_free WAJIB False!
        ticket_url = (data.get("ticket_url") or "").strip()
        description = (data.get("description") or f"Konser {title} menampilkan {', '.join(artists)} di {venue_name}, {city}.").strip()
        
        full_text_search = f"{title} {description} {ticket_url} {json.dumps(data)}".lower()
        platform_keywords = ["goers", "artatix", "detik", "loket", "tiket", "bbo", "megatix", "cognitix", "tiptip", "presale", "early bird", "ots"]
        free_keywords = ["free entry", "gratis", "no htm", "tanpa htm", "free admission"]
        
        if any(kw in full_text_search for kw in platform_keywords) and not any(fkw in full_text_search for fkw in free_keywords):
            is_free = False

        if not ticket_url:
            q_term = (headliner or (artists[0] if artists else title)).strip()
            ticket_url = f"https://www.loket.com/search?q={q_term}"

        genres = [g.strip() for g in data.get("genres", []) if g and isinstance(g, str)]
        # Jika poster tidak mendeskripsikan genre, jangan karang genre secara otomatis
        # Biarkan kosong kecuali jelas tertera


        description = (data.get("description") or f"Konser {title} menampilkan {', '.join(artists)} di {venue_name}, {city}.").strip()

        # Normalisasi Open Gate / Doors Open
        raw_doors = str(data.get("doors_open") or "").strip()
        if not raw_doors or raw_doors.lower() in ["tba", "none", "null", "belum ada", "belum diumumkan", ""]:
            doors_open = "TBA"
        else:
            doors_open = raw_doors

        raw_platforms = data.get("ticket_platforms", [])
        ticket_platforms = []
        if isinstance(raw_platforms, list):
            ticket_platforms = [str(p).strip() for p in raw_platforms if p and isinstance(p, (str, int))]

        # Fallback deteksi manual dari full_text_search jika AI luput mengekstrak array ticket_platforms
        if not ticket_platforms:
            if "goers" in full_text_search: ticket_platforms.append("GOERS")
            if "artatix" in full_text_search: ticket_platforms.append("Artatix")
            if "detik" in full_text_search: ticket_platforms.append("detikevent")
            if "loket" in full_text_search: ticket_platforms.append("Loket.com")
            if "tiket.com" in full_text_search: ticket_platforms.append("Tiket.com")
            if "bbo" in full_text_search: ticket_platforms.append("BBO")

        # Normalisasi Lineups & Multi-Day Rundown
        raw_lineups = data.get("lineups", [])
        normalized_lineups = []
        if isinstance(raw_lineups, list) and len(raw_lineups) > 0:
            for idx, item in enumerate(raw_lineups, start=1):
                if isinstance(item, dict) and item.get("artist_name"):
                    a_name = str(item["artist_name"]).strip()
                    d_day = str(item.get("day") or "").strip()
                    if d_day.lower() in ["none", "null", "tba", "false", ""]:
                        d_day = ""
                    s_time = str(item.get("set_time") or "").strip()
                    if not s_time or s_time.lower() in ["none", "null", "false"]:
                        s_time = "TBA"
                    is_hl = bool(item.get("is_headliner", False))
                    normalized_lineups.append({
                        "order": idx,
                        "artist_name": a_name,
                        "day": d_day,
                        "set_time": s_time,
                        "is_headliner": is_hl
                    })
                    if a_name not in artists:
                        artists.append(a_name)

        return {
            "success": True,
            "title": title,
            "artists": artists,
            "headliner": headliner,
            "lineups": normalized_lineups,
            "venue_name": venue_name,
            "city": city,
            "address": address,
            "date": start_datetime.strftime('%Y-%m-%d'),
            "time": start_datetime.strftime('%H:%M'),
            "start_datetime_iso": start_datetime.isoformat(),
            "doors_open": doors_open,
            "ticket_price": ticket_price,
            "is_free": is_free,
            "ticket_tiers": normalized_tiers,
            "ticket_url": ticket_url,
            "ticket_platforms": ticket_platforms,
            "genres": genres,
            "description": description,
            "confidence_score": float(data.get("confidence_score") or 0.9)
        }


    def save_Gigs_to_database(self, normalized_data: dict, poster_file=None) -> Gigs:
        """
        Menyimpan data hasil AI langsung ke database Django (Venue, Artists, Genres, Gigs, GigsLineup, GigsTicketTier).
        """
        # 1. Venue
        venue_name = normalized_data["venue_name"]
        city = normalized_data["city"]
        address = normalized_data.get("address") or f"{venue_name}, {city}"
        
        venue = Venue.objects.filter(name__iexact=venue_name, city__iexact=city).first()
        if not venue:
            venue = Venue.objects.create(
                name=venue_name,
                city=city,
                address=address,
                province=f"Provinsi {city}",
                is_active=True
            )

        # 2. Genres
        genre_objs = []
        genre_colors = ["#FF3366", "#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#06B6D4"]
        for idx, g_name in enumerate(normalized_data.get("genres", [])):
            genre = Genre.objects.filter(name__iexact=g_name).first()
            if not genre:
                genre = Genre.objects.create(
                    name=g_name.title(),
                    color=genre_colors[idx % len(genre_colors)]
                )
            genre_objs.append(genre)

        # 3. Artists
        artist_objs = []
        for a_name in normalized_data.get("artists", []):
            artist = Artist.objects.filter(name__iexact=a_name).first()
            if not artist:
                artist = Artist.objects.create(
                    name=a_name,
                    hometown=city,
                    is_active=True
                )
            if genre_objs:
                artist.genres.set(genre_objs)
            artist_objs.append(artist)

        # 4. Gigs
        start_datetime = datetime.fromisoformat(normalized_data["start_datetime_iso"])
        if timezone.is_naive(start_datetime):
            start_datetime = timezone.make_aware(start_datetime)

        title = normalized_data["title"]
        slug_candidate = slugify(f"{title}-{start_datetime.strftime('%Y%m%d')}")
        
        Gigs = Gigs.objects.filter(slug=slug_candidate).first()
        if not Gigs:
            Gigs = Gigs.objects.create(
                slug=slug_candidate,
                title=title,
                venue=venue,
                start_datetime=start_datetime,
                doors_open=normalized_data.get("doors_open", "TBA"),
                ticket_price=normalized_data.get("ticket_price", 0),
                is_free=normalized_data.get("is_free", False),
                ticket_url=normalized_data.get("ticket_url", ""),
                description=normalized_data.get("description", ""),
                status=GigsStatus.SCHEDULED,
                is_featured=True
            )
        else:
            Gigs.title = title
            Gigs.venue = venue
            Gigs.start_datetime = start_datetime
            Gigs.doors_open = normalized_data.get("doors_open", Gigs.doors_open)
            Gigs.ticket_price = normalized_data.get("ticket_price", Gigs.ticket_price)
            Gigs.is_free = normalized_data.get("is_free", Gigs.is_free)
            Gigs.ticket_url = normalized_data.get("ticket_url", Gigs.ticket_url)
            Gigs.description = normalized_data.get("description", Gigs.description)

        if poster_file:
            Gigs.poster = poster_file
        
        Gigs.save()

        # 5. Lineups (dengan dukungan multi-day & rundown waktu)
        lineups_meta = normalized_data.get("lineups", [])
        lineup_dict = {l["artist_name"].lower(): l for l in lineups_meta if isinstance(l, dict) and l.get("artist_name")}
        headliner_name = normalized_data.get("headliner", "")

        for order, artist in enumerate(artist_objs, start=1):
            artist_meta = lineup_dict.get(artist.name.lower(), {})
            day_val = artist_meta.get("day", "")
            set_time_val = artist_meta.get("set_time") or f"{(17 + (order % 6)):02d}:00 WIB"
            is_hl = artist_meta.get("is_headliner", (headliner_name and headliner_name.lower() in artist.name.lower()) or (order == 1))

            lineup_obj = GigsLineup.objects.filter(Gigs=Gigs, artist=artist).first()
            if not lineup_obj:
                GigsLineup.objects.create(
                    Gigs=Gigs,
                    artist=artist,
                    order=order,
                    day=day_val,
                    is_headliner=is_hl,
                    set_time=set_time_val
                )
            else:
                if day_val:
                    lineup_obj.day = day_val
                if set_time_val and set_time_val != "TBA":
                    lineup_obj.set_time = set_time_val
                lineup_obj.is_headliner = is_hl
                lineup_obj.order = order
                lineup_obj.save()

        # 6. Ticket Tiers
        for tier_data in normalized_data.get("ticket_tiers", []):
            tier_name = tier_data["tier_name"]
            tier_obj = GigsTicketTier.objects.filter(Gigs=Gigs, tier_name__iexact=tier_name).first()
            if not tier_obj:
                GigsTicketTier.objects.create(
                    Gigs=Gigs,
                    tier_name=tier_name,
                    price=tier_data.get("price", 0),
                    is_sold_out=tier_data.get("is_sold_out", False),
                    description=tier_data.get("description", ""),
                    order=tier_data.get("order", 1)
                )
            else:
                tier_obj.price = tier_data.get("price", tier_obj.price)
                tier_obj.is_sold_out = tier_data.get("is_sold_out", tier_obj.is_sold_out)
                tier_obj.description = tier_data.get("description", tier_obj.description)
                tier_obj.save()

        # 7. Ticket Links (Multi-platform)
        platforms = normalized_data.get("ticket_platforms", [])
        if platforms:
            for idx, p_name in enumerate(platforms, start=1):
                p_clean = str(p_name).strip()
                p_url = normalized_data.get("ticket_url") or f"https://www.google.com/search?q={title}+{p_clean}"
                if not GigsTicketLink.objects.filter(Gigs=Gigs, platform_name__iexact=p_clean).exists():
                    GigsTicketLink.objects.create(
                        Gigs=Gigs,
                        platform_name=p_clean,
                        url=p_url,
                        order=idx
                    )

        return Gigs


