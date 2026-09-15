"""
Seed script for GigTrack.
Fills database with realistic music scene data (Indie, Rock, Pop, etc.)
including gigs happening TODAY, tomorrow, and upcoming dates.

Run with:
    python seed_data.py
"""
import os
import sys
import django
from datetime import timedelta

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from apps.artists.models import Genre, Artist
from apps.venues.models import Venue
from apps.gigs.models import Gig, GigLineup, GigStatus

def seed():
    print("🎸 Memulai seeding data GigTrack...")

    # 1. Genres
    genres_data = [
        {"name": "Indie Rock", "color": "#FF3366"},
        {"name": "City Pop / Retro", "color": "#FF9900"},
        {"name": "Post-Punk / Alternative", "color": "#7928CA"},
        {"name": "Dream Pop / Shoegaze", "color": "#00DFD8"},
        {"name": "Hardcore / Punk", "color": "#E53E3E"},
        {"name": "Folk / Acoustic", "color": "#38A169"},
        {"name": "Jazz / Neo-Soul", "color": "#D69E2E"},
        {"name": "Electronic / Synthwave", "color": "#0070F3"},
    ]
    genre_objs = {}
    for g in genres_data:
        obj, _ = Genre.objects.get_or_create(name=g["name"], defaults={"color": g["color"]})
        genre_objs[g["name"]] = obj
    print(f"✅ {len(genre_objs)} Genre berhasil dibuat.")

    # 2. Venues
    venues_data = [
        {
            "name": "M Bloc Space - Live House",
            "address": "Jl. Panglima Polim No.37, Melawai, Kebayoran Baru",
            "city": "Jakarta Selatan",
            "province": "DKI Jakarta",
            "capacity": 650,
            "maps_url": "https://maps.google.com/?q=M+Bloc+Space+Jakarta",
            "instagram_url": "https://instagram.com/mblocspace",
            "image_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Rossi Musik Fatmawati",
            "address": "Jl. RS. Fatmawati Raya No.30B, Cilandak Barat",
            "city": "Jakarta Selatan",
            "province": "DKI Jakarta",
            "capacity": 350,
            "maps_url": "https://maps.google.com/?q=Rossi+Musik+Fatmawati",
            "instagram_url": "https://instagram.com/rossimusik",
            "image_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Spasial / Gudang Selatan 22",
            "address": "Jl. Gudang Selatan No.22, Malabar, Lengkong",
            "city": "Bandung",
            "province": "Jawa Barat",
            "capacity": 500,
            "maps_url": "https://maps.google.com/?q=Gudang+Selatan+Bandung",
            "instagram_url": "https://instagram.com/spasial_",
            "image_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "The Orchard Bar & Restaurant",
            "address": "Jl. Nakula Gg. Baik-Baik No.99x, Seminyak",
            "city": "Bali",
            "province": "Bali",
            "capacity": 300,
            "maps_url": "https://maps.google.com/?q=The+Orchard+Bar+Bali",
            "instagram_url": "https://instagram.com/theorchardbali",
            "image_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800&auto=format&fit=crop&q=80"
        },
        {
            "name": "Duck Down Pizza Party",
            "address": "Jl. Senopati No.44, Selong, Kebayoran Baru",
            "city": "Jakarta Selatan",
            "province": "DKI Jakarta",
            "capacity": 200,
            "maps_url": "https://maps.google.com/?q=Duck+Down+Bar+Jakarta",
            "instagram_url": "https://instagram.com/duckdownbar",
            "image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80"
        }
    ]
    venue_objs = {}
    for v in venues_data:
        obj, _ = Venue.objects.get_or_create(name=v["name"], defaults=v)
        venue_objs[v["name"]] = obj
    print(f"✅ {len(venue_objs)} Venue berhasil dibuat.")

    # 3. Artists
    artists_data = [
        {
            "name": "The Adams",
            "bio": "Grup indie rock / power pop legendaris asal Jakarta yang terkenal dengan harmonisasi vokal empat bagian.",
            "hometown": "Jakarta",
            "image_url": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=600&auto=format&fit=crop&q=80",
            "spotify_url": "https://open.spotify.com/artist/the_adams",
            "genres": ["Indie Rock", "Post-Punk / Alternative"]
        },
        {
            "name": ".Feast",
            "bio": "Band rock alternatif asal Jakarta dengan lirik kritis sosial politik dan riff distorsi energik.",
            "hometown": "Jakarta",
            "image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&auto=format&fit=crop&q=80",
            "spotify_url": "https://open.spotify.com/artist/feast",
            "genres": ["Post-Punk / Alternative", "Indie Rock"]
        },
        {
            "name": "Hindia",
            "bio": "Proyek solo Baskara Putra yang memadukan spoken word, indie pop, dan introspeksi personal.",
            "hometown": "Jakarta",
            "image_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=600&auto=format&fit=crop&q=80",
            "spotify_url": "https://open.spotify.com/artist/hindia",
            "genres": ["Indie Rock", "Folk / Acoustic"]
        },
        {
            "name": "Reality Club",
            "bio": "Grup indie rock dengan melodi sinematik dan sentuhan pop 60-an bernuansa modern.",
            "hometown": "Jakarta",
            "image_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=600&auto=format&fit=crop&q=80",
            "spotify_url": "https://open.spotify.com/artist/reality_club",
            "genres": ["Indie Rock", "Dream Pop / Shoegaze"]
        },
        {
            "name": "Grrrl Gang",
            "bio": "Trio indie-pop berkecepatan tinggi asal Yogyakarta dengan hook catchy dan vokal raw.",
            "hometown": "Yogyakarta",
            "image_url": "https://images.unsplash.com/photo-1526478806334-5fd488fcaabc?w=600&auto=format&fit=crop&q=80",
            "spotify_url": "https://open.spotify.com/artist/grrrl_gang",
            "genres": ["Indie Rock", "Hardcore / Punk"]
        },
        {
            "name": "White Shoes & The Couples Company",
            "bio": "Ensemble retro pop / city pop dengan sentuhan swing jazz dan atmosfer sinema Indonesia tempo dulu.",
            "hometown": "Jakarta",
            "image_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600&auto=format&fit=crop&q=80",
            "spotify_url": "https://open.spotify.com/artist/wsatcc",
            "genres": ["City Pop / Retro", "Jazz / Neo-Soul"]
        },
        {
            "name": "Avhath",
            "bio": "Grup blackened hardcore / post-metal dari Jakarta dengan visual gelap dan performa panggung katarsis.",
            "hometown": "Jakarta",
            "image_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=600&auto=format&fit=crop&q=80",
            "spotify_url": "https://open.spotify.com/artist/avhath",
            "genres": ["Hardcore / Punk", "Post-Punk / Alternative"]
        }
    ]
    artist_objs = {}
    for a in artists_data:
        genre_names = a.pop("genres")
        obj, _ = Artist.objects.get_or_create(name=a["name"], defaults=a)
        for gname in genre_names:
            if gname in genre_objs:
                obj.genres.add(genre_objs[gname])
        artist_objs[a["name"]] = obj
    print(f"✅ {len(artist_objs)} Artis / Band berhasil dibuat.")

    # 4. Gigs (Today, Tomorrow, and Upcoming)
    now = timezone.localtime(timezone.now())
    today = now.date()

    # Dates:
    today_evening = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())) + timedelta(hours=19, minutes=0)
    today_night = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())) + timedelta(hours=20, minutes=30)
    tomorrow_evening = today_evening + timedelta(days=1)
    weekend_gig = today_evening + timedelta(days=3)
    next_week_gig = today_evening + timedelta(days=7)

    gigs_data = [
        # GIG HARI INI #1 (Featured Live Radar)
        {
            "title": "Subculture Sound Vol. 8: Midweek Noise",
            "venue": venue_objs["M Bloc Space - Live House"],
            "start_datetime": today_evening,
            "doors_open": "18:30 WIB",
            "ticket_price": 75000,
            "is_free": False,
            "status": GigStatus.SCHEDULED,
            "is_featured": True,
            "ticket_url": "https://loket.com/event/subculture-sound",
            "poster_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80",
            "description": "Pesta musik independen tengah pekan menampilkan perpaduan distorsi gitar energetik dan melodi alternatif di panggung utama M Bloc Live House!",
            "lineup": [
                {"artist": artist_objs["The Adams"], "set_time": "21:00 - 22:15 WIB", "is_headliner": True, "order": 1},
                {"artist": artist_objs["Reality Club"], "set_time": "19:45 - 20:45 WIB", "is_headliner": False, "order": 2},
                {"artist": artist_objs["Grrrl Gang"], "set_time": "19:00 - 19:35 WIB", "is_headliner": False, "order": 3}
            ]
        },
        # GIG HARI INI #2 (Free Entry Bar Gig)
        {
            "title": "Duck Down Secret Session",
            "venue": venue_objs["Duck Down Pizza Party"],
            "start_datetime": today_night,
            "doors_open": "20:00 WIB",
            "ticket_price": 0,
            "is_free": True,
            "status": GigStatus.SCHEDULED,
            "is_featured": False,
            "ticket_url": "",
            "poster_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80",
            "description": "Intimate show gratis tanpa tiket! Siapkan energimu untuk moshpit santai sambil menikmati pizza dan bir dingin.",
            "lineup": [
                {"artist": artist_objs[".Feast"], "set_time": "21:30 - 22:45 WIB", "is_headliner": True, "order": 1},
            ]
        },
        # GIG BESOK
        {
            "title": "Bandung Distortion Collective",
            "venue": venue_objs["Spasial / Gudang Selatan 22"],
            "start_datetime": tomorrow_evening,
            "doors_open": "18:00 WIB",
            "ticket_price": 60000,
            "is_free": False,
            "status": GigStatus.SCHEDULED,
            "is_featured": False,
            "ticket_url": "https://goersapp.com/e/bdg-distortion",
            "poster_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800&auto=format&fit=crop&q=80",
            "description": "Eksplorasi soundscape berat dan atmosferik di aula Gudang Selatan yang ikonik.",
            "lineup": [
                {"artist": artist_objs["Avhath"], "set_time": "21:00 - 22:00 WIB", "is_headliner": True, "order": 1},
                {"artist": artist_objs["Grrrl Gang"], "set_time": "19:30 - 20:30 WIB", "is_headliner": False, "order": 2}
            ]
        },
        # GIG WEEKEND
        {
            "title": "Sunset Grooves & Nostalgia Night",
            "venue": venue_objs["The Orchard Bar & Restaurant"],
            "start_datetime": weekend_gig,
            "doors_open": "17:30 WITA",
            "ticket_price": 120000,
            "is_free": False,
            "status": GigStatus.SCHEDULED,
            "is_featured": True,
            "ticket_url": "https://megatix.co.id/events/sunset-grooves",
            "poster_url": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=800&auto=format&fit=crop&q=80",
            "description": "Suasana tropis Bali berbalut irama retro jazz dan melodi city pop yang syahdu di bawah langit senja Seminyak.",
            "lineup": [
                {"artist": artist_objs["White Shoes & The Couples Company"], "set_time": "20:00 - 21:30 WITA", "is_headliner": True, "order": 1},
                {"artist": artist_objs["Hindia"], "set_time": "18:30 - 19:45 WITA", "is_headliner": False, "order": 2}
            ]
        },
        # GIG MINGGU DEPAN
        {
            "title": "Raw Underground Movement",
            "venue": venue_objs["Rossi Musik Fatmawati"],
            "start_datetime": next_week_gig,
            "doors_open": "19:00 WIB",
            "ticket_price": 50000,
            "is_free": False,
            "status": GigStatus.SCHEDULED,
            "is_featured": False,
            "ticket_url": "",
            "poster_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80",
            "description": "Panggung DIY legendaris Rossi Fatmawati kembali bergetar dengan band-band indie lokal terbaik ibukota.",
            "lineup": [
                {"artist": artist_objs["The Adams"], "set_time": "21:15 - 22:30 WIB", "is_headliner": True, "order": 1},
                {"artist": artist_objs[".Feast"], "set_time": "20:00 - 21:00 WIB", "is_headliner": False, "order": 2}
            ]
        }
    ]

    for g_data in gigs_data:
        lineup_data = g_data.pop("lineup")
        gig, created = Gig.objects.get_or_create(
            title=g_data["title"],
            defaults=g_data
        )
        if created:
            for item in lineup_data:
                GigLineup.objects.create(
                    gig=gig,
                    artist=item["artist"],
                    set_time=item["set_time"],
                    is_headliner=item["is_headliner"],
                    order=item["order"]
                )
    print("✅ Berhasil membuat 5 Gig realistis (termasuk 2 Gig untuk HARI INI)!")
    print("\n🎉 Seeding selesai! Database GigTrack siap digunakan.")

if __name__ == '__main__':
    seed()
