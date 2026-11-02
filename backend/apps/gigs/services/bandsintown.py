import logging
import requests
import datetime
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from apps.artists.models import Artist, Genre
from apps.venues.models import Venue
from apps.Gigss.models import Gigs, GigsLineup, GigsStatus

logger = logging.getLogger(__name__)

# Daftar kurasi artis dan band skena musik Indonesia
INDONESIA_POPULAR_ARTISTS = [
    "The Adams", ".Feast", "Hindia", "Reality Club", "Efek Rumah Kaca",
    "White Shoes & The Couples Company", "Morfem", "Avhath", "Grrrl Gang",
    "Skandal", "Pamungkas", "Barasuara", "The Sigit", "Bernadya",
    "Sal Priadi", "Nadin Amizah", "Bilal Indrajaya", "Danilla", "Kunto Aji"
]

# Daftar venue terkurasi khusus wilayah JABODETABEK (+ Bandung sebagai skena tetangga)
JABODETABEK_CITIES = [
    'Jakarta Selatan', 'Jakarta Pusat', 'Jakarta Utara', 'Jakarta Barat',
    'Tangerang', 'Tangerang Selatan', 'Depok', 'Bogor', 'Bekasi', 'Bandung'
]

JABODETABEK_VENUES_POOL = [
    # Jakarta Selatan (Jantung Skena Gigs & Live House)
    {
        "name": "M Bloc Live House",
        "city": "Jakarta Selatan",
        "region": "DKI Jakarta",
        "country": "Indonesia",
        "address": "Jl. Panglima Polim No.37, Melawai, Blok M, Jakarta Selatan",
        "latitude": "-6.2435",
        "longitude": "106.7979",
        "offset_days": 0, # Hari Ini!
        "time": "19:30:00",
        "price": 150000
    },
    {
        "name": "Rossi Musik Fatmawati",
        "city": "Jakarta Selatan",
        "region": "DKI Jakarta",
        "country": "Indonesia",
        "address": "Jl. RS. Fatmawati Raya No.30, Cilandak, Jakarta Selatan",
        "latitude": "-6.2842",
        "longitude": "106.7971",
        "offset_days": 0, # Hari Ini!
        "time": "20:00:00",
        "price": 75000
    },
    {
        "name": "Duck Down Pizza Party",
        "city": "Jakarta Selatan",
        "region": "DKI Jakarta",
        "country": "Indonesia",
        "address": "Jl. Senopati No.44, Selong, Kebayoran Baru, Jakarta Selatan",
        "latitude": "-6.2341",
        "longitude": "106.8105",
        "offset_days": 0, # Hari Ini (Free Entry)!
        "time": "21:00:00",
        "price": 0
    },
    {
        "name": "Krapela Blok M",
        "city": "Jakarta Selatan",
        "region": "DKI Jakarta",
        "country": "Indonesia",
        "address": "Jl. Panglima Polim No.22, Melawai, Kebayoran Baru, Jakarta Selatan",
        "latitude": "-6.2440",
        "longitude": "106.7985",
        "offset_days": 1, # Besok
        "time": "19:00:00",
        "price": 85000
    },

    # Jakarta Pusat & Utara (Konser Besar & Hall Teater)
    {
        "name": "Tennis Indoor Senayan",
        "city": "Jakarta Pusat",
        "region": "DKI Jakarta",
        "country": "Indonesia",
        "address": "Jl. Pintu Satu Senayan, Gelora, Tanah Abang, Jakarta Pusat",
        "latitude": "-6.2163",
        "longitude": "106.8016",
        "offset_days": 2, # 2 hari lagi
        "time": "19:30:00",
        "price": 350000
    },
    {
        "name": "Graha Bhakti Budaya (TIM)",
        "city": "Jakarta Pusat",
        "region": "DKI Jakarta",
        "country": "Indonesia",
        "address": "Taman Ismail Marzuki, Jl. Cikini Raya No.73, Menteng, Jakarta Pusat",
        "latitude": "-6.1903",
        "longitude": "106.8398",
        "offset_days": 3, # Akhir pekan
        "time": "19:00:00",
        "price": 200000
    },
    {
        "name": "JIExpo Hall B Kemayoran",
        "city": "Jakarta Pusat",
        "region": "DKI Jakarta",
        "country": "Indonesia",
        "address": "Gedung Pusat Niaga, Arena JIExpo Kemayoran, Jakarta Pusat",
        "latitude": "-6.1483",
        "longitude": "106.8482",
        "offset_days": 5, # Akhir pekan
        "time": "18:30:00",
        "price": 250000
    },

    # Tangerang & Tangerang Selatan (BSD / Bintaro)
    {
        "name": "ICE BSD City Hall 1",
        "city": "Tangerang",
        "region": "Banten",
        "country": "Indonesia",
        "address": "Jl. BSD Grand Boulevard No.1, Pagedangan, Tangerang",
        "latitude": "-6.3015",
        "longitude": "106.6372",
        "offset_days": 4, # 4 hari lagi
        "time": "19:00:00",
        "price": 400000
    },
    {
        "name": "Bintaro Creative District",
        "city": "Tangerang Selatan",
        "region": "Banten",
        "country": "Indonesia",
        "address": "Jl. Bintaro Utama 3A, Pondok Karya, Pondok Aren, Tangerang Selatan",
        "latitude": "-6.2750",
        "longitude": "106.7280",
        "offset_days": 3, # Akhir pekan
        "time": "18:30:00",
        "price": 100000
    },

    # Depok & Bogor
    {
        "name": "Balairung UI Depok Stage",
        "city": "Depok",
        "region": "Jawa Barat",
        "country": "Indonesia",
        "address": "Kampus UI Depok, Pondok Cina, Beji, Kota Depok",
        "latitude": "-6.3628",
        "longitude": "106.8272",
        "offset_days": 1, # Besok
        "time": "18:00:00",
        "price": 50000
    },
    {
        "name": "Kopi Nako Sangrai Live Stage",
        "city": "Bogor",
        "region": "Jawa Barat",
        "country": "Indonesia",
        "address": "Jl. Pajajaran Indah V No.7, Baranangsiang, Kota Bogor",
        "latitude": "-6.6083",
        "longitude": "106.8122",
        "offset_days": 2, # 2 hari lagi
        "time": "19:30:00",
        "price": 0
    },

    # Bekasi
    {
        "name": "Revo Town Rooftop Ground",
        "city": "Bekasi",
        "region": "Jawa Barat",
        "country": "Indonesia",
        "address": "Jl. Ahmad Yani No.Kav. 1, Pekayon Jaya, Bekasi Selatan",
        "latitude": "-6.2520",
        "longitude": "106.9925",
        "offset_days": 4, # Akhir pekan
        "time": "19:00:00",
        "price": 75000
    },

    # Bandung (Weekend Hub Tetangga)
    {
        "name": "Spasial / Gudang Selatan 22",
        "city": "Bandung",
        "region": "Jawa Barat",
        "country": "Indonesia",
        "address": "Jl. Gudang Selatan No.22, Malabar, Lengkong, Bandung",
        "latitude": "-6.9214",
        "longitude": "107.6071",
        "offset_days": 5, # Akhir pekan
        "time": "19:00:00",
        "price": 125000
    }
]

class BandsintownService:
    """
    Service client untuk berinteraksi dengan Bandsintown API.
    Disesuaikan secara spesifik untuk memantau jadwal konser band-band Indonesia
    dan venue lokal di berbagai kota di Indonesia.
    """

    def __init__(self, app_id=None, indonesia_only=True):
        self.app_id = app_id or getattr(settings, 'BANDSINTOWN_APP_ID', '')
        self.base_url = getattr(settings, 'BANDSINTOWN_BASE_URL', 'https://rest.bandsintown.com')
        self.indonesia_only = indonesia_only

    def fetch_artist_info(self, artist_name):
        """
        Mengambil metadata artis dari Bandsintown:
        GET /artists/{artist_name}?app_id={app_id}
        """
        if not self.app_id:
            return {"error": "Missing app_id", "message": "Bandsintown app_id is required."}

        url = f"{self.base_url}/artists/{requests.utils.quote(artist_name)}"
        params = {"app_id": self.app_id}

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {
                "error": f"HTTP {response.status_code}",
                "message": response.text
            }
        except requests.RequestException as e:
            logger.error(f"Error fetching artist info from Bandsintown: {e}")
            return {"error": "Network error", "message": str(e)}

    def fetch_artist_events(self, artist_name, date_filter="upcoming"):
        """
        Mengambil jadwal konser artis dari Bandsintown:
        GET /artists/{artist_name}/events?app_id={app_id}&date={date_filter}
        """
        if not self.app_id:
            return {"error": "Missing app_id", "message": "Bandsintown app_id is required."}

        url = f"{self.base_url}/artists/{requests.utils.quote(artist_name)}/events"
        params = {"app_id": self.app_id, "date": date_filter}

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return {"success": True, "events": data}
                elif isinstance(data, dict) and "errors" in data:
                    return {"error": "Bandsintown API error", "message": data.get("errors")}
                return {"success": True, "events": []}
            return {
                "error": f"HTTP {response.status_code}",
                "message": response.text
            }
        except requests.RequestException as e:
            logger.error(f"Error fetching events from Bandsintown: {e}")
            return {"error": "Network error", "message": str(e)}

    def generate_mock_events(self, artist_name):
        """
        Membuat dataset konser realistis mengikuti skema resmi Bandsintown
        khusus untuk panggung dan venue musik di wilayah JABODETABEK (+ Bandung).
        """
        local_today = timezone.localdate()
        # Pilih 3 venue terkurasi dari JABODETABEK_VENUES_POOL
        import hashlib
        h_val = int(hashlib.md5(artist_name.encode()).hexdigest(), 16)
        total_v = len(JABODETABEK_VENUES_POOL)
        selected_indices = [
            h_val % total_v,
            (h_val + 2) % total_v,
            (h_val + 4) % total_v
        ]
        # Pastikan offset days berurutan
        day_offsets = [0, 2, 4]

        events = []
        for i, idx in enumerate(selected_indices):
            v = JABODETABEK_VENUES_POOL[idx]
            event_date = local_today + datetime.timedelta(days=day_offsets[i])
            dt_str = f"{event_date.strftime('%Y-%m-%d')}T{v['time']}"
            event_id = f"bit-jabo-{slugify(artist_name)}-{i+1}"
            events.append({
                "id": event_id,
                "title": f"{artist_name} Live at {v['name']}",
                "datetime": dt_str,
                "description": f"Sesi konser live {artist_name} di {v['name']}, {v['city']}. Menghadirkan set list lengkap dan atmosfer intim.",
                "venue": {
                    "name": v["name"],
                    "city": v["city"],
                    "region": v["region"],
                    "country": "Indonesia",
                    "address": v["address"],
                    "latitude": v["latitude"],
                    "longitude": v["longitude"]
                },
                "offers": [
                    {
                        "type": "Tickets",
                        "url": f"https://loket.com/event/{slugify(artist_name)}-{slugify(v['city'])}",
                        "status": "available",
                        "price": v["price"]
                    }
                ],
                "lineup": [artist_name]
            })
        return events

    def sync_artist_events(self, artist_name, app_id=None, use_mock=False):
        """
        Metode utama untuk menyinkronkan data konser artis ke database Django.
        Mencari data ke Bandsintown, lalu otomatis membuat/mengupdate:
        - Artist
        - Venue
        - Gigs
        - GigsLineup
        """
        if app_id:
            self.app_id = app_id

        events = []
        source = "live_api"

        # 1. Coba fetch dari Live Bandsintown API jika app_id ada dan tidak dipaksa mock
        if not use_mock and self.app_id:
            api_res = self.fetch_artist_events(artist_name)
            if api_res.get("success"):
                raw_events = api_res.get("events", [])
                if self.indonesia_only:
                    indonesia_events = []
                    for ev in raw_events:
                        v = ev.get("venue", {})
                        country = (v.get("country") or "").lower()
                        city = (v.get("city") or "").lower()
                        if any(jc.lower() in city for jc in JABODETABEK_CITIES):
                            indonesia_events.append(ev)
                    events = indonesia_events
                else:
                    events = raw_events
            else:
                logger.warning(f"Bandsintown API call failed ({api_res.get('error')}). Using simulation fallback.")
                source = "mock_fallback"
                events = self.generate_mock_events(artist_name)
        else:
            source = "mock_simulation"
            events = self.generate_mock_events(artist_name)

        if not events:
            return {
                "success": True,
                "artist": artist_name,
                "source": source,
                "events_count": 0,
                "Gigss_created": 0,
                "Gigss_updated": 0,
                "message": f"Tidak ditemukan jadwal konser mendatang untuk {artist_name} di Bandsintown."
            }

        # 2. Sinkronkan ke Database GigsSTRACK
        # A. Pastikan Artist ada
        artist_obj, _ = Artist.objects.get_or_create(
            name=artist_name,
            defaults={
                "slug": slugify(artist_name),
                "bio": f"Profil resmi musisi {artist_name} tersinkronisasi via Bandsintown.",
                "hometown": "Indonesia",
                "image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80"
            }
        )

        Gigss_created = 0
        Gigss_updated = 0
        synced_Gigss_info = []

        for ev in events:
            # B. Venue Mapping
            v_data = ev.get("venue", {})
            v_name = v_data.get("name") or "Live Music Stage"
            v_city = v_data.get("city") or "Jakarta"
            v_region = v_data.get("region") or "DKI Jakarta"

            maps_url = ""
            if v_data.get("latitude") and v_data.get("longitude"):
                maps_url = f"https://www.google.com/maps?q={v_data['latitude']},{v_data['longitude']}"
            else:
                maps_url = f"https://maps.google.com/?q={requests.utils.quote(v_name)}+{requests.utils.quote(v_city)}"

            venue_obj, _ = Venue.objects.get_or_create(
                name=v_name,
                defaults={
                    "city": v_city,
                    "province": v_region,
                    "address": f"{v_name}, {v_city}, {v_region}",
                    "maps_url": maps_url,
                    "image_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80",
                    "slug": slugify(f"{v_name}-{v_city}")
                }
            )

            # C. Parse Datetime
            dt_raw = ev.get("datetime")
            try:
                # Bandsintown datetime format: "2026-10-15T19:30:00"
                if "T" in dt_raw:
                    dt_obj = datetime.datetime.fromisoformat(dt_raw)
                else:
                    dt_obj = datetime.datetime.strptime(dt_raw, "%Y-%m-%d %H:%M:%S")
                start_dt = timezone.make_aware(dt_obj) if timezone.is_naive(dt_obj) else dt_obj
            except Exception:
                start_dt = timezone.now() + datetime.timedelta(days=1)

            # D. Ticket and Offers
            offers = ev.get("offers", [])
            ticket_url = ""
            ticket_price = 150000
            if offers:
                first_offer = offers[0]
                ticket_url = first_offer.get("url", "")
                if "price" in first_offer:
                    ticket_price = int(first_offer["price"])

            event_title = ev.get("title") or f"{artist_name} Live at {v_name}"
            slug_val = slugify(f"{event_title}-{start_dt.strftime('%Y%m%d')}")

            Gigs_obj, created = Gigs.objects.update_or_create(
                slug=slug_val,
                defaults={
                    "title": event_title,
                    "venue": venue_obj,
                    "start_datetime": start_dt,
                    "doors_open": f"{(start_dt - datetime.timedelta(hours=1)).strftime('%H:%M')} WIB",
                    "ticket_price": ticket_price,
                    "is_free": (ticket_price == 0),
                    "ticket_url": ticket_url,
                    "description": ev.get("description") or f"Penampilan live spektakuler {artist_name} di {v_name}.",
                    "poster_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80",
                    "status": GigsStatus.SCHEDULED,
                    "is_featured": (Gigss_created + Gigss_updated == 0) # jadikan featured untuk acara pertama
                }
            )

            if created:
                Gigss_created += 1
            else:
                Gigss_updated += 1

            # E. Lineup Mapping
            lineup_artists = ev.get("lineup", [artist_name])
            for order_idx, l_name in enumerate(lineup_artists, start=1):
                l_artist, _ = Artist.objects.get_or_create(
                    name=l_name,
                    defaults={
                        "slug": slugify(l_name),
                        "bio": f"Artis pendukung tur {artist_name}.",
                        "hometown": "Indonesia"
                    }
                )
                GigsLineup.objects.update_or_create(
                    Gigs=Gigs_obj,
                    artist=l_artist,
                    defaults={
                        "set_time": f"{start_dt.strftime('%H:%M')} - {(start_dt + datetime.timedelta(hours=1, minutes=30)).strftime('%H:%M')} WIB",
                        "is_headliner": (l_name.lower() == artist_name.lower()),
                        "order": order_idx
                    }
                )

            synced_Gigss_info.append({
                "id": Gigs_obj.id,
                "title": Gigs_obj.title,
                "venue": venue_obj.name,
                "city": venue_obj.city,
                "datetime": start_dt.strftime("%d %b %Y, %H:%M"),
                "status": "Dibuat" if created else "Diperbarui"
            })

        return {
            "success": True,
            "artist": artist_name,
            "source": source,
            "events_count": len(events),
            "Gigss_created": Gigss_created,
            "Gigss_updated": Gigss_updated,
            "synced_Gigss": synced_Gigss_info,
            "message": f"Berhasil menyinkronkan {len(events)} jadwal konser untuk {artist_name} ({source})."
        }
