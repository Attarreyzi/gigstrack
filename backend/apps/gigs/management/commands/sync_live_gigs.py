import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from apps.artists.models import Artist, Genre
from apps.venues.models import Venue
from apps.gigs.models import Gig, GigLineup, GigStatus

class Command(BaseCommand):
    help = "Sync and automatically populate live gigs, tour schedules, and band line-ups"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Hapus semua gig lama sebelum sinkronisasi data baru',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== [GigTrack] Memulai Mesin Sinkronisasi Gig Otomatis ==="))

        if options['clear']:
            self.stdout.write(self.style.WARNING("Membersihkan data gig lama..."))
            Gig.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("[OK] Data gig lama berhasil dibersihkan."))

        # 1. Sinkronisasi Genre Musik
        genres_data = [
            {"name": "Indie Rock", "color": "#FF3366"},
            {"name": "Post-Punk", "color": "#9B51E0"},
            {"name": "Alternative Rock", "color": "#00F0FF"},
            {"name": "Synthpop", "color": "#FF007A"},
            {"name": "Hardcore / Metal", "color": "#FF4500"},
            {"name": "Folk / Acoustic", "color": "#00FF66"},
            {"name": "Pop / Neo-Soul", "color": "#FFB800"},
        ]

        genre_map = {}
        for g in genres_data:
            genre_obj, _ = Genre.objects.get_or_create(
                name=g["name"],
                defaults={"color": g["color"], "slug": slugify(g["name"])}
            )
            genre_map[g["name"]] = genre_obj

        self.stdout.write(f"[OK] Berhasil memverifikasi {len(genre_map)} genre musik.")

        # 2. Sinkronisasi Artis & Band
        artists_data = [
            {
                "name": "The Adams",
                "genres": ["Indie Rock", "Alternative Rock"],
                "hometown": "Jakarta",
                "bio": "Kuintet power pop / indie rock legendaris asal Jakarta yang terkenal dengan harmonisasi vokal tajam.",
                "image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80",
                "instagram_url": "https://instagram.com/theadamsband",
                "spotify_url": "https://open.spotify.com/artist/4cKylsKk60Z0M8k2C4RzP6",
            },
            {
                "name": ".Feast",
                "genres": ["Alternative Rock", "Indie Rock"],
                "hometown": "Jakarta",
                "bio": "Band rock dengan lirik sosial-politik yang tajam dan distorsi sonik eksplosif.",
                "image_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80",
                "instagram_url": "https://instagram.com/ffeastt",
                "spotify_url": "https://open.spotify.com/artist/4ZgYxVbB2tK30Zt7G6h8r9",
            },
            {
                "name": "Hindia",
                "genres": ["Indie Rock", "Pop / Neo-Soul"],
                "hometown": "Jakarta",
                "bio": "Solois dan vokalis Baskara Putra yang mengeksplorasi kecemasan urban dan kisah hidup personal.",
                "image_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80",
                "instagram_url": "https://instagram.com/wordfangs",
                "spotify_url": "https://open.spotify.com/artist/6Zg9rC3q7eZ3L7D1Y9sN8",
            },
            {
                "name": "Reality Club",
                "genres": ["Indie Rock", "Synthpop"],
                "hometown": "Jakarta",
                "bio": "Grup indie rock sinematik pemenang AMI Awards dengan tur global dan fanbase internasional masif.",
                "image_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800&auto=format&fit=crop&q=80",
                "instagram_url": "https://instagram.com/realityclub",
                "spotify_url": "https://open.spotify.com/artist/7z5G9LhXQ4w3k9Y7z1e5P",
            },
            {
                "name": "Efek Rumah Kaca",
                "genres": ["Indie Rock", "Alternative Rock"],
                "hometown": "Jakarta",
                "bio": "Trio art-rock pionir pergerakan musik independen Indonesia dengan lirik puitis sarat kritik sosial.",
                "image_url": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800&auto=format&fit=crop&q=80",
                "instagram_url": "https://instagram.com/sebelahmata_erk",
                "spotify_url": "https://open.spotify.com/artist/3K2Z5G9LhXQ4w3k9Y7z1e4",
            },
            {
                "name": "White Shoes & The Couples Company",
                "genres": ["Pop / Neo-Soul", "Synthpop"],
                "hometown": "Jakarta",
                "bio": "Ansambel retro pop 70-an bernuansa vintage bioskop tempo doeloe yang mempesona.",
                "image_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800&auto=format&fit=crop&q=80",
                "instagram_url": "https://instagram.com/wsatcc",
                "spotify_url": "https://open.spotify.com/artist/2Zg9rC3q7eZ3L7D1Y9sN7",
            },
            {
                "name": "Morfem",
                "genres": ["Indie Rock", "Alternative Rock"],
                "hometown": "Jakarta",
                "bio": "Kuartet fuzzy indie rock besutan Jimi Multhazam dengan distorsi garang dan energi panggung liar.",
                "image_url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&auto=format&fit=crop&q=80",
                "instagram_url": "https://instagram.com/morfem_band",
                "spotify_url": "https://open.spotify.com/artist/1Zg9rC3q7eZ3L7D1Y9sN6",
            },
            {
                "name": "Avhath",
                "genres": ["Hardcore / Metal", "Post-Punk"],
                "hometown": "Jakarta",
                "bio": "Kolektif black metal / post-hardcore kontemporer terdepan di skena underground Asia Tenggara.",
                "image_url": "https://images.unsplash.com/photo-1464375117522-1311d6a5b81f?w=800&auto=format&fit=crop&q=80",
                "instagram_url": "https://instagram.com/avhath",
                "spotify_url": "https://open.spotify.com/artist/0Zg9rC3q7eZ3L7D1Y9sN5",
            },
            {
                "name": "Skandal",
                "genres": ["Indie Rock", "Alternative Rock"],
                "hometown": "Yogyakarta",
                "bio": "Kuartet indie pop/rock asal Yogyakarta dengan riff catchy 90-an dan semangat panggung hangat.",
                "image_url": "https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=800&auto=format&fit=crop&q=80",
                "instagram_url": "https://instagram.com/skandal_yk",
                "spotify_url": "https://open.spotify.com/artist/8Zg9rC3q7eZ3L7D1Y9sN4",
            },
            {
                "name": "Grrrl Gang",
                "genres": ["Indie Rock", "Post-Punk"],
                "hometown": "Yogyakarta",
                "bio": "Trio indie pop / jangle rock energetik yang telah merambah tur internasional Eropa dan Asia.",
                "image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80",
                "instagram_url": "https://instagram.com/grrrlgang",
                "spotify_url": "https://open.spotify.com/artist/9Zg9rC3q7eZ3L7D1Y9sN3",
            }
        ]

        artist_map = {}
        for a in artists_data:
            artist_obj, _ = Artist.objects.get_or_create(
                name=a["name"],
                defaults={
                    "hometown": a["hometown"],
                    "bio": a["bio"],
                    "image_url": a["image_url"],
                    "instagram_url": a["instagram_url"],
                    "spotify_url": a["spotify_url"],
                    "slug": slugify(a["name"])
                }
            )
            for g_name in a["genres"]:
                if g_name in genre_map:
                    artist_obj.genres.add(genre_map[g_name])
            artist_map[a["name"]] = artist_obj

        self.stdout.write(f"[OK] Berhasil memverifikasi {len(artist_map)} artis / band.")

        # 3. Sinkronisasi Venue / Tempat
        venues_data = [
            {
                "name": "M Bloc Live House",
                "city": "Jakarta",
                "province": "DKI Jakarta",
                "address": "Jl. Panglima Polim No.37, Melawai, Kebayoran Baru, Jakarta Selatan",
                "maps_url": "https://maps.google.com/?q=M+Bloc+Space+Jakarta",
                "image_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80"
            },
            {
                "name": "Rossi Musik Fatmawati",
                "city": "Jakarta",
                "province": "DKI Jakarta",
                "address": "Jl. RS. Fatmawati Raya No.30, Cilandak Bar., Jakarta Selatan",
                "maps_url": "https://maps.google.com/?q=Rossi+Musik+Fatmawati",
                "image_url": "https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=800&auto=format&fit=crop&q=80"
            },
            {
                "name": "Spasial Bandung",
                "city": "Bandung",
                "province": "Jawa Barat",
                "address": "Jl. Gudang Selatan No.22, Merdeka, Kec. Sumur Bandung, Kota Bandung",
                "maps_url": "https://maps.google.com/?q=Spasial+Bandung",
                "image_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80"
            },
            {
                "name": "Jogja National Museum (JNM)",
                "city": "Yogyakarta",
                "province": "D.I. Yogyakarta",
                "address": "Jl. Prof. DR. Ki Amri Yahya No.1, Pakuncen, Wirobrajan, Yogyakarta",
                "maps_url": "https://maps.google.com/?q=Jogja+National+Museum",
                "image_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800&auto=format&fit=crop&q=80"
            },
            {
                "name": "Amphitheater Balai Pemuda",
                "city": "Surabaya",
                "province": "Jawa Timur",
                "address": "Jl. Gubernur Suryo No.15, Embong Kaliasin, Genteng, Surabaya",
                "maps_url": "https://maps.google.com/?q=Balai+Pemuda+Surabaya",
                "image_url": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800&auto=format&fit=crop&q=80"
            },
            {
                "name": "Desa Potato Head Bali",
                "city": "Bali",
                "province": "Bali",
                "address": "Jl. Petitenget No.51B, Seminyak, Kuta Utara, Badung, Bali",
                "maps_url": "https://maps.google.com/?q=Potato+Head+Seminyak+Bali",
                "image_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800&auto=format&fit=crop&q=80"
            }
        ]

        venue_map = {}
        for v in venues_data:
            venue_obj, _ = Venue.objects.get_or_create(
                name=v["name"],
                defaults={
                    "city": v["city"],
                    "province": v["province"],
                    "address": v["address"],
                    "maps_url": v["maps_url"],
                    "image_url": v["image_url"],
                    "slug": slugify(f"{v['name']}-{v['city']}")
                }
            )
            venue_map[v["name"]] = venue_obj

        self.stdout.write(f"[OK] Berhasil memverifikasi {len(venue_map)} venue di berbagai kota.")

        # 4. Sinkronisasi Jadwal Acara / Gigs (Live Realtime Context)
        now = timezone.now()
        local_today = timezone.localdate()

        # Target jadwal:
        # 1. Hari Ini (Hari Ini) -> live radar!
        # 2. Besok
        # 3. Akhir pekan (Sabtu ini / Minggu ini)
        # 4. Minggu depan

        gigs_schedule = [
            {
                "title": "M Bloc Noise & Soundwave Showcase",
                "venue_name": "M Bloc Live House",
                "days_offset": 0, # HARI INI!
                "time_str": "19:30",
                "doors_open": "18:30 WIB",
                "ticket_price": 150000,
                "is_featured": True,
                "description": "Malam puncak showcase musik indie alternatif di jantung Blok M. Mempertemukan distorsi berani dan aransemen vokal harmonis.",
                "poster_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80",
                "ticket_url": "https://tiket.com/event/mbloc-soundwave",
                "lineup": [
                    {"artist": "The Adams", "set_time": "21:15 - 22:30 WIB", "is_headliner": True, "order": 2},
                    {"artist": ".Feast", "set_time": "19:45 - 20:45 WIB", "is_headliner": False, "order": 1},
                ]
            },
            {
                "title": "Underground Fuzz & Noise Riot",
                "venue_name": "Rossi Musik Fatmawati",
                "days_offset": 0, # HARI INI!
                "time_str": "20:00",
                "doors_open": "19:00 WIB",
                "ticket_price": 75000,
                "is_featured": False,
                "description": "Pesta rilisan independen bawah tanah dengan atmosfer intim dan sonik tanpa kompromi.",
                "poster_url": "https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=800&auto=format&fit=crop&q=80",
                "ticket_url": "",
                "lineup": [
                    {"artist": "Avhath", "set_time": "21:30 - 22:45 WIB", "is_headliner": True, "order": 2},
                    {"artist": "Morfem", "set_time": "20:00 - 21:00 WIB", "is_headliner": False, "order": 1},
                ]
            },
            {
                "title": "Bandung Dystopia & Poetic Echoes",
                "venue_name": "Spasial Bandung",
                "days_offset": 1, # BESOK!
                "time_str": "19:00",
                "doors_open": "18:00 WIB",
                "ticket_price": 125000,
                "is_featured": True,
                "description": "Kolaborasi megah dua raksasa musik naratif Indonesia dalam ruang akustik industrial Spasial Bandung.",
                "poster_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800&auto=format&fit=crop&q=80",
                "ticket_url": "https://loket.com/event/spasial-echoes",
                "lineup": [
                    {"artist": "Efek Rumah Kaca", "set_time": "21:00 - 22:30 WIB", "is_headliner": True, "order": 2},
                    {"artist": "Hindia", "set_time": "19:30 - 20:30 WIB", "is_headliner": False, "order": 1},
                ]
            },
            {
                "title": "Jogja Jangle Pop & Retro Night",
                "venue_name": "Jogja National Museum (JNM)",
                "days_offset": 3, # AKHIR PEKAN!
                "time_str": "18:30",
                "doors_open": "17:30 WIB",
                "ticket_price": 0, # FREE ENTRY!
                "is_featured": False,
                "description": "Pesta dansa terbuka di pelataran JNM. Terbuka gratis untuk semua penikmat musik Yogyakarta.",
                "poster_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800&auto=format&fit=crop&q=80",
                "ticket_url": "https://eventbrite.com/jnm-retro-night",
                "lineup": [
                    {"artist": "White Shoes & The Couples Company", "set_time": "20:30 - 22:00 WIB", "is_headliner": True, "order": 3},
                    {"artist": "Grrrl Gang", "set_time": "19:30 - 20:15 WIB", "is_headliner": False, "order": 2},
                    {"artist": "Skandal", "set_time": "18:30 - 19:15 WIB", "is_headliner": False, "order": 1},
                ]
            },
            {
                "title": "Reality Club: Cinema Tour Surabaya",
                "venue_name": "Amphitheater Balai Pemuda",
                "days_offset": 5, # MINGGU DEPAN
                "time_str": "19:30",
                "doors_open": "18:30 WIB",
                "ticket_price": 185000,
                "is_featured": True,
                "description": "Rangkaian tur album panggung megah Reality Club membawakan aransemen orkestral di kota pahlawan.",
                "poster_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80",
                "ticket_url": "https://goersapp.com/events/reality-club-surabaya",
                "lineup": [
                    {"artist": "Reality Club", "set_time": "20:00 - 22:00 WIB", "is_headliner": True, "order": 1},
                ]
            },
            {
                "title": "Sunset Sonic Waves Bali",
                "venue_name": "Desa Potato Head Bali",
                "days_offset": 7, # MINGGU DEPAN
                "time_str": "17:00",
                "doors_open": "16:00 WIB",
                "ticket_price": 250000,
                "is_featured": False,
                "description": "Sesi konser tepi pantai menyambut matahari terbenam dengan paduan pop eksperimental dan synthwave.",
                "poster_url": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800&auto=format&fit=crop&q=80",
                "ticket_url": "https://seminyakmusic.com/sunset-waves",
                "lineup": [
                    {"artist": "The Adams", "set_time": "19:30 - 21:00 WIB", "is_headliner": True, "order": 2},
                    {"artist": "Hindia", "set_time": "17:30 - 18:45 WIB", "is_headliner": False, "order": 1},
                ]
            }
        ]

        synced_count = 0
        for item in gigs_schedule:
            venue = venue_map.get(item["venue_name"])
            if not venue:
                continue

            target_date = local_today + datetime.timedelta(days=item["days_offset"])
            hour, minute = map(int, item["time_str"].split(":"))
            start_dt = timezone.make_aware(datetime.datetime.combine(target_date, datetime.time(hour, minute)))

            slug_base = slugify(f"{item['title']}-{target_date.strftime('%Y%m%d')}")

            gig, created = Gig.objects.update_or_create(
                slug=slug_base,
                defaults={
                    "title": item["title"],
                    "venue": venue,
                    "start_datetime": start_dt,
                    "doors_open": item["doors_open"],
                    "ticket_price": item["ticket_price"],
                    "is_free": (item["ticket_price"] == 0),
                    "is_featured": item["is_featured"],
                    "description": item["description"],
                    "poster_url": item["poster_url"],
                    "ticket_url": item["ticket_url"],
                    "status": GigStatus.SCHEDULED
                }
            )

            # Update / Buat Lineup
            for lineup_data in item["lineup"]:
                artist = artist_map.get(lineup_data["artist"])
                if artist:
                    GigLineup.objects.update_or_create(
                        gig=gig,
                        artist=artist,
                        defaults={
                            "set_time": lineup_data["set_time"],
                            "is_headliner": lineup_data["is_headliner"],
                            "order": lineup_data["order"]
                        }
                    )

            synced_count += 1
            action_label = "Dibuat baru" if created else "Diperbarui"
            self.stdout.write(f"  [+] {gig.title} @ {venue.name} ({target_date.strftime('%d %b %Y')}) -> {action_label}")

        self.stdout.write(self.style.SUCCESS(f"\n[OK] Sinkronisasi Berhasil! {synced_count} gig live aktif dan terjadwal."))
        self.stdout.write(self.style.SUCCESS("[OK] Data radar Hari Ini, Besok, dan Akhir Pekan sudah terisi otomatis.\n"))
