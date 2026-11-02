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

# Palet warna genre untuk badge UI
GENRE_COLOR_MAP = {
    'Rock': '#E63946',
    'Indie Rock': '#FF3366',
    'Alternative Rock': '#F77F00',
    'Pop': '#FF70A6',
    'Indie Pop': '#FF9770',
    'Jazz': '#70D6FF',
    'Electronic': '#7928CA',
    'Dance': '#9D4EDD',
    'Hip-Hop/Rap': '#E0AAFF',
    'R&B': '#F72585',
    'Metal': '#D00000',
    'Folk': '#2A9D8F',
}

class TicketmasterService:
    """
    Service client untuk berinteraksi dengan Ticketmaster Discovery API (v2).
    Didesain untuk menarik konser musik, venue, line-up musisi, dan harga tiket
    secara valid serta dapat disinkronkan berkala (real-time background sync).
    """

    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or getattr(settings, 'TICKETMASTER_API_KEY', '')
        self.base_url = (base_url or getattr(settings, 'TICKETMASTER_BASE_URL', 'https://app.ticketmaster.com/discovery/v2')).rstrip('/')

    def fetch_events(self, keyword=None, city=None, country_code='ID', size=20, start_date=None, classification_name='music'):
        """
        Mengambil jadwal konser musik dari Ticketmaster Discovery API v2:
        GET /discovery/v2/events.json
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Missing API Key",
                "message": "Ticketmaster API Key belum disetel. Gunakan argumen --mock untuk pengujian tanpa kredensial atau daftarkan API key di developer.ticketmaster.com"
            }

        url = f"{self.base_url}/events.json"
        params = {
            "apikey": self.api_key,
            "classificationName": classification_name,
            "size": min(max(int(size), 1), 200),
            "sort": "date,asc",
        }

        if country_code:
            params["countryCode"] = country_code.strip()
        if city:
            params["city"] = city.strip()
        if keyword:
            params["keyword"] = keyword.strip()
        if start_date:
            # Format ISO 8601 UTC: YYYY-MM-DDTHH:mm:ssZ
            if isinstance(start_date, (datetime.date, datetime.datetime)):
                params["startDateTime"] = start_date.strftime("%Y-%m-%dT00:00:00Z")
            else:
                params["startDateTime"] = str(start_date)

        try:
            logger.info(f"Mengirim permintaan ke Ticketmaster API: {url} params: {params}")
            response = requests.get(url, params=params, timeout=12)

            if response.status_code == 200:
                data = response.json()
                events = data.get("_embedded", {}).get("events", [])
                page_info = data.get("page", {})
                return {
                    "success": True,
                    "events": events,
                    "total_elements": page_info.get("totalElements", len(events)),
                    "total_pages": page_info.get("totalPages", 1),
                }
            elif response.status_code == 401 or response.status_code == 403:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code} Unauthorized",
                    "message": "API Key Ticketmaster tidak valid atau belum diaktifkan."
                }
            elif response.status_code == 429:
                return {
                    "success": False,
                    "error": "HTTP 429 Rate Limit Exceeded",
                    "message": "Limit request Ticketmaster terlampaui (maks 5 req/detik, 5000 req/hari)."
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": response.text[:200]
                }
        except requests.RequestException as e:
            logger.error(f"Koneksi ke Ticketmaster API gagal: {e}")
            return {
                "success": False,
                "error": "Network Error",
                "message": str(e)
            }

    def _select_best_image(self, images):
        """Memilih poster gambar dengan resolusi terbaik dan rasio 16:9 atau 4:3."""
        if not images:
            return "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80"

        # Prioritaskan rasio 16_9 dengan lebar tertinggi
        images_16_9 = [img for img in images if img.get("ratio") == "16_9"]
        if images_16_9:
            images_16_9.sort(key=lambda x: x.get("width", 0), reverse=True)
            return images_16_9[0].get("url")

        # Fallback ke gambar dengan lebar tertinggi
        sorted_by_width = sorted(images, key=lambda x: x.get("width", 0), reverse=True)
        return sorted_by_width[0].get("url")

    def parse_event_data(self, raw_event):
        """
        Melakukan normalisasi data mentah JSON Ticketmaster ke struktur GigsSTRACK.
        """
        tm_id = raw_event.get("id", "")
        title = raw_event.get("name", "Konser Musik")
        ticket_url = raw_event.get("url", "")
        info = raw_event.get("info") or raw_event.get("pleaseNote") or f"Konser musik live resmi '{title}'."

        # 1. Parsing Tanggal & Waktu
        dates_data = raw_event.get("dates", {})
        start_data = dates_data.get("start", {})
        dt_str = start_data.get("dateTime")
        local_date = start_data.get("localDate")
        local_time = start_data.get("localTime") or "19:00:00"

        start_datetime = None
        if dt_str:
            try:
                # e.g. "2026-10-24T12:00:00Z"
                cleaned_dt = dt_str.replace("Z", "+00:00")
                parsed_dt = datetime.datetime.fromisoformat(cleaned_dt)
                start_datetime = timezone.localtime(parsed_dt) if timezone.is_aware(parsed_dt) else timezone.make_aware(parsed_dt)
            except Exception:
                pass

        if not start_datetime and local_date:
            try:
                combined_str = f"{local_date} {local_time}"
                parsed_dt = datetime.datetime.strptime(combined_str, "%Y-%m-%d %H:%M:%S")
                start_datetime = timezone.make_aware(parsed_dt)
            except Exception:
                pass

        if not start_datetime:
            start_datetime = timezone.now() + datetime.timedelta(days=7)

        # 2. Parsing Status
        status_code = dates_data.get("status", {}).get("code", "onsale").lower()
        if status_code in ["cancelled", "canceled"]:
            Gigs_status = GigsStatus.CANCELLED
        elif status_code in ["postponed", "rescheduled"]:
            Gigs_status = GigsStatus.POSTPONED
        else:
            Gigs_status = GigsStatus.SCHEDULED

        # 3. Parsing Harga Tiket
        price_ranges = raw_event.get("priceRanges", [])
        ticket_price = 0
        is_free = False
        if price_ranges:
            min_price = price_ranges[0].get("min", 0)
            currency = price_ranges[0].get("currency", "IDR")
            if min_price == 0:
                is_free = True
            elif currency == "USD":
                # Estimasi konversi USD ke IDR jika internasional
                ticket_price = int(min_price * 16000)
            else:
                ticket_price = int(min_price)
        else:
            # Default estimasi tiket konser terverifikasi
            ticket_price = 150000

        # 4. Poster Image
        poster_url = self._select_best_image(raw_event.get("images", []))

        # 5. Parsing Venue
        embedded = raw_event.get("_embedded", {})
        venues_list = embedded.get("venues", [])
        venue_info = {
            "name": "Live Stage Arena",
            "city": "Jakarta",
            "province": "DKI Jakarta",
            "address": "Jakarta, Indonesia",
            "maps_url": "",
            "image_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80"
        }

        if venues_list:
            v = venues_list[0]
            v_name = v.get("name") or "Live Stage Arena"
            v_city = v.get("city", {}).get("name") or "Jakarta"
            v_state = v.get("state", {}).get("name") or "DKI Jakarta"
            v_address = v.get("address", {}).get("line1") or f"{v_name}, {v_city}"

            loc = v.get("location", {})
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            maps_url = ""
            if lat and lon:
                maps_url = f"https://www.google.com/maps?q={lat},{lon}"
            else:
                maps_url = f"https://maps.google.com/?q={requests.utils.quote(v_name)}+{requests.utils.quote(v_city)}"

            v_image = self._select_best_image(v.get("images", []))

            venue_info = {
                "name": v_name,
                "city": v_city,
                "province": v_state,
                "address": v_address,
                "maps_url": maps_url,
                "image_url": v_image or venue_info["image_url"]
            }

        # 6. Parsing Musisi / Lineup (Attractions)
        attractions_list = embedded.get("attractions", [])
        attractions_info = []

        for att in attractions_list:
            att_name = att.get("name")
            if not att_name:
                continue

            # Klasifikasi Genre
            genres = []
            for classification in att.get("classifications", []):
                genre_obj = classification.get("genre", {})
                sub_genre_obj = classification.get("subGenre", {})
                if genre_obj.get("name") and genre_obj.get("name") not in ["Undefined", "Music"]:
                    genres.append(genre_obj.get("name"))
                if sub_genre_obj.get("name") and sub_genre_obj.get("name") not in ["Undefined", "Music"]:
                    genres.append(sub_genre_obj.get("name"))

            att_img = self._select_best_image(att.get("images", []))
            spotify_url = att.get("externalLinks", {}).get("spotify", [{}])[0].get("url", "")
            instagram_url = att.get("externalLinks", {}).get("instagram", [{}])[0].get("url", "")

            attractions_info.append({
                "name": att_name,
                "genres": list(dict.fromkeys(genres)),  # deduplicate
                "image_url": att_img,
                "spotify_url": spotify_url,
                "instagram_url": instagram_url,
            })

        return {
            "tm_id": tm_id,
            "title": title,
            "description": info,
            "ticket_url": ticket_url,
            "poster_url": poster_url,
            "start_datetime": start_datetime,
            "doors_open": f"{(start_datetime - datetime.timedelta(hours=1)).strftime('%H:%M')} WIB",
            "status": Gigs_status,
            "ticket_price": ticket_price,
            "is_free": is_free,
            "venue": venue_info,
            "attractions": attractions_info,
        }

    def sync_events_to_db(self, raw_events):
        """
        Menyimpan daftar event mentah Ticketmaster ke database Django GigsSTRACK
        secara aman tanpa duplikasi (idempotent).
        """
        Gigss_created = 0
        Gigss_updated = 0
        processed_Gigss = []

        for raw in raw_events:
            parsed = self.parse_event_data(raw)
            tm_id = parsed["tm_id"]
            title = parsed["title"]
            start_dt = parsed["start_datetime"]

            # 1. Sync Venue
            v_info = parsed["venue"]
            venue_slug = slugify(f"{v_info['name']}-{v_info['city']}")
            venue_obj, _ = Venue.objects.get_or_create(
                slug=venue_slug,
                defaults={
                    "name": v_info["name"],
                    "city": v_info["city"],
                    "province": v_info["province"],
                    "address": v_info["address"],
                    "maps_url": v_info["maps_url"],
                    "image_url": v_info["image_url"],
                }
            )

            # 2. Sync Gigs (Gunakan tm_id atau slug judul+tanggal untuk mencegah duplikasi)
            if tm_id:
                Gigs_slug = slugify(f"tm-{tm_id}-{title}")[:240]
            else:
                Gigs_slug = slugify(f"{title}-{start_dt.strftime('%Y%m%d')}")[:240]

            Gigs_defaults = {
                "title": title,
                "venue": venue_obj,
                "start_datetime": start_dt,
                "doors_open": parsed["doors_open"],
                "description": parsed["description"],
                "poster_url": parsed["poster_url"],
                "ticket_price": parsed["ticket_price"],
                "is_free": parsed["is_free"],
                "ticket_url": parsed["ticket_url"],
                "status": parsed["status"],
            }

            Gigs_obj, created = Gigs.objects.update_or_create(
                slug=Gigs_slug,
                defaults=Gigs_defaults
            )

            if created:
                Gigss_created += 1
            else:
                Gigss_updated += 1

            # 3. Sync Lineups & Artists
            attractions = parsed["attractions"]
            if not attractions:
                # Jika tidak ada attractions eksplisit, gunakan judul event sebagai band
                attractions = [{
                    "name": title.split(" - ")[0].split(" Live")[0].strip(),
                    "genres": ["Live Music"],
                    "image_url": parsed["poster_url"],
                    "spotify_url": "",
                    "instagram_url": ""
                }]

            for idx, att in enumerate(attractions, start=1):
                artist_name = att["name"]
                artist_slug = slugify(artist_name)

                artist_obj, _ = Artist.objects.get_or_create(
                    slug=artist_slug,
                    defaults={
                        "name": artist_name,
                        "bio": f"Artis resmi konser '{title}' terverifikasi Ticketmaster.",
                        "image_url": att.get("image_url") or parsed["poster_url"],
                        "spotify_url": att.get("spotify_url", ""),
                        "instagram_url": att.get("instagram_url", ""),
                    }
                )

                # Sync Genres
                for g_name in att.get("genres", []):
                    g_slug = slugify(g_name)
                    color = GENRE_COLOR_MAP.get(g_name, '#FF3366')
                    genre_obj, _ = Genre.objects.get_or_create(
                        slug=g_slug,
                        defaults={"name": g_name, "color": color}
                    )
                    artist_obj.genres.add(genre_obj)

                # Hubungkan ke GigsLineup
                GigsLineup.objects.update_or_create(
                    Gigs=Gigs_obj,
                    artist=artist_obj,
                    defaults={
                        "is_headliner": (idx == 1),
                        "order": idx,
                        "set_time": f"{(start_dt + datetime.timedelta(minutes=30 * (idx - 1))).strftime('%H:%M')} WIB"
                    }
                )

            processed_Gigss.append({
                "id": Gigs_obj.id,
                "title": Gigs_obj.title,
                "venue": venue_obj.name,
                "city": venue_obj.city,
                "date": start_dt.strftime("%Y-%m-%d %H:%M"),
                "status": Gigs_obj.status,
                "ticket_price": Gigs_obj.ticket_price,
                "ticket_url": Gigs_obj.ticket_url,
                "action": "created" if created else "updated"
            })

        return {
            "success": True,
            "total_events_processed": len(raw_events),
            "Gigss_created": Gigss_created,
            "Gigss_updated": Gigss_updated,
            "synced_Gigss": processed_Gigss
        }

    def generate_mock_events(self, city='Jakarta', keyword=None):
        """
        Menghasilkan dataset simulasi konser Ticketmaster berformat JSON resmi
        untuk pengujian tanpa API key.
        """
        now = timezone.localtime(timezone.now())
        base_date = now.date()

        mock_data = [
            {
                "id": "vvG17Z9f7bKpQ8",
                "name": "Arctic Monkeys - Asia Arena Tour 2026",
                "url": "https://www.ticketmaster.com/arctic-monkeys-tickets/artist/1004121",
                "info": "Arctic Monkeys kembali mengguncang Jakarta dalam rangkaian tur Asia Arena 2026 membawakan album legendaris dan lagu-lagu hits.",
                "images": [
                    {
                        "ratio": "16_9",
                        "url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=1200&auto=format&fit=crop&q=80",
                        "width": 1200,
                        "height": 675
                    }
                ],
                "dates": {
                    "start": {
                        "localDate": (base_date + datetime.timedelta(days=14)).strftime("%Y-%m-%d"),
                        "localTime": "19:30:00",
                        "dateTime": f"{(base_date + datetime.timedelta(days=14)).strftime('%Y-%m-%d')}T12:30:00Z"
                    },
                    "status": {"code": "onsale"}
                },
                "priceRanges": [
                    {"min": 1250000, "max": 3500000, "currency": "IDR"}
                ],
                "_embedded": {
                    "venues": [
                        {
                            "name": "Indonesia Arena GBK Senayan",
                            "city": {"name": "Jakarta Pusat"},
                            "state": {"name": "DKI Jakarta"},
                            "address": {"line1": "Kawasan Gelora Bung Karno, Jl. Pintu Satu Senayan"},
                            "location": {"latitude": "-6.2185", "longitude": "106.8024"}
                        }
                    ],
                    "attractions": [
                        {
                            "name": "Arctic Monkeys",
                            "classifications": [
                                {"genre": {"name": "Rock"}, "subGenre": {"name": "Indie Rock"}}
                            ]
                        }
                    ]
                }
            },
            {
                "id": "vvG17Z941xNpR1",
                "name": "Java Jazz Festival 2026 - Special Live Experience",
                "url": "https://www.ticketmaster.com/java-jazz-festival-tickets/event/2026JJF",
                "info": "Festival Jazz terbesar di belahan bumi selatan menyajikan kolaborasi musisi jazz dunia dan maestro musik Indonesia.",
                "images": [
                    {
                        "ratio": "16_9",
                        "url": "https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=1200&auto=format&fit=crop&q=80",
                        "width": 1200,
                        "height": 675
                    }
                ],
                "dates": {
                    "start": {
                        "localDate": (base_date + datetime.timedelta(days=21)).strftime("%Y-%m-%d"),
                        "localTime": "16:00:00",
                        "dateTime": f"{(base_date + datetime.timedelta(days=21)).strftime('%Y-%m-%d')}T09:00:00Z"
                    },
                    "status": {"code": "onsale"}
                },
                "priceRanges": [
                    {"min": 850000, "max": 2000000, "currency": "IDR"}
                ],
                "_embedded": {
                    "venues": [
                        {
                            "name": "JIExpo Kemayoran Arena",
                            "city": {"name": "Jakarta Pusat"},
                            "state": {"name": "DKI Jakarta"},
                            "address": {"line1": "Gedung Pusat Niaga Arena JIEXPO Kemayoran"},
                            "location": {"latitude": "-6.1492", "longitude": "106.8528"}
                        }
                    ],
                    "attractions": [
                        {
                            "name": "Java Jazz Superband",
                            "classifications": [
                                {"genre": {"name": "Jazz"}, "subGenre": {"name": "Contemporary Jazz"}}
                            ]
                        }
                    ]
                }
            },
            {
                "id": "vvG17Z9f22AbC3",
                "name": "Hammersonic Live - Metal & Hardcore Summit 2026",
                "url": "https://www.ticketmaster.com/hammersonic-festival-tickets/event/2026HS",
                "info": "Pesta musik rock dan cadas terbesar Asia Tenggara kembali menghadirkan line-up internasional legendaris.",
                "images": [
                    {
                        "ratio": "16_9",
                        "url": "https://images.unsplash.com/photo-1464375117522-1311d6a5b81f?w=1200&auto=format&fit=crop&q=80",
                        "width": 1200,
                        "height": 675
                    }
                ],
                "dates": {
                    "start": {
                        "localDate": (base_date + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                        "localTime": "15:00:00",
                        "dateTime": f"{(base_date + datetime.timedelta(days=30)).strftime('%Y-%m-%d')}T08:00:00Z"
                    },
                    "status": {"code": "onsale"}
                },
                "priceRanges": [
                    {"min": 1000000, "max": 2500000, "currency": "IDR"}
                ],
                "_embedded": {
                    "venues": [
                        {
                            "name": "Carnaval Ancol Circuit Stage",
                            "city": {"name": "Jakarta Utara"},
                            "state": {"name": "DKI Jakarta"},
                            "address": {"line1": "Pantai Carnaval Ancol, Pademangan"},
                            "location": {"latitude": "-6.1218", "longitude": "106.8456"}
                        }
                    ],
                    "attractions": [
                        {
                            "name": "Avhath & Heavyweights",
                            "classifications": [
                                {"genre": {"name": "Metal"}, "subGenre": {"name": "Heavy Metal"}}
                            ]
                        }
                    ]
                }
            },
            {
                "id": "vvG17Z9f88XxY4",
                "name": "Joyland Festival Weekend Experience 2026",
                "url": "https://www.ticketmaster.com/joyland-festival-tickets/event/2026JL",
                "info": "Festival musik multi-genre bernuansa taman hijau ramah keluarga dengan panggung musik indie internasional dan nasional.",
                "images": [
                    {
                        "ratio": "16_9",
                        "url": "https://images.unsplash.com/photo-1506157786151-b8491531f063?w=1200&auto=format&fit=crop&q=80",
                        "width": 1200,
                        "height": 675
                    }
                ],
                "dates": {
                    "start": {
                        "localDate": (base_date + datetime.timedelta(days=45)).strftime("%Y-%m-%d"),
                        "localTime": "14:00:00",
                        "dateTime": f"{(base_date + datetime.timedelta(days=45)).strftime('%Y-%m-%d')}T07:00:00Z"
                    },
                    "status": {"code": "onsale"}
                },
                "priceRanges": [
                    {"min": 650000, "max": 1400000, "currency": "IDR"}
                ],
                "_embedded": {
                    "venues": [
                        {
                            "name": "GBK Baseball Stadium & Plains",
                            "city": {"name": "Jakarta Pusat"},
                            "state": {"name": "DKI Jakarta"},
                            "address": {"line1": "Gelora Bung Karno, Senayan"},
                            "location": {"latitude": "-6.2162", "longitude": "106.8018"}
                        }
                    ],
                    "attractions": [
                        {
                            "name": "The Adams & International Friends",
                            "classifications": [
                                {"genre": {"name": "Indie Pop"}, "subGenre": {"name": "Alternative Rock"}}
                            ]
                        }
                    ]
                }
            }
        ]

        if keyword:
            kw = keyword.lower()
            mock_data = [d for d in mock_data if kw in d["name"].lower() or kw in d["info"].lower()]

        return mock_data

    def sync(self, keyword=None, city=None, country_code='ID', size=20, use_mock=False):
        """
        Alur sinkronisasi lengkap:
        1. Fetch data dari Ticketmaster (atau generate mock jika mode simulasi/tidak ada key).
        2. Simpan dan update ke database GigsSTRACK.
        """
        events = []
        source = "ticketmaster_live_api"

        if use_mock or not self.api_key:
            logger.info("Menjalankan sinkronisasi Ticketmaster menggunakan dataset simulasi (mock mode).")
            events = self.generate_mock_events(city=city or 'Jakarta', keyword=keyword)
            source = "ticketmaster_mock_simulation"
        else:
            fetch_result = self.fetch_events(
                keyword=keyword,
                city=city,
                country_code=country_code,
                size=size
            )
            if not fetch_result.get("success"):
                logger.warning(f"Gagal mengambil event dari Ticketmaster API: {fetch_result.get('message')}")
                return fetch_result
            events = fetch_result.get("events", [])

        sync_result = self.sync_events_to_db(events)
        sync_result["source"] = source
        return sync_result
