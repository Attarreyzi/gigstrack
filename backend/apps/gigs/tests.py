from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from apps.venues.models import Venue
from apps.artists.models import Artist, Genre
from apps.gigs.models import Gigs, GigsLineup, GigsStatus

class GigsSTRACKAPITests(TestCase):
    """
    Automated Unit & Integration Tests for GigsSTRACK Backend API.
    Ensures date tracking, city filters, and artist search work reliably.
    """

    def setUp(self):
        self.client = APIClient()

        # 1. Create Venue
        self.venue_jakarta = Venue.objects.create(
            name="M Bloc Space",
            address="Jl. Panglima Polim No.37",
            city="Jakarta Selatan",
            province="DKI Jakarta"
        )
        self.venue_bandung = Venue.objects.create(
            name="Spasial",
            address="Jl. Gudang Selatan No.22",
            city="Bandung",
            province="Jawa Barat"
        )

        # 2. Create Genre & Artist
        self.genre_rock = Genre.objects.create(name="Indie Rock", color="#FF3366")
        self.artist_adams = Artist.objects.create(name="The Adams", hometown="Jakarta")
        self.artist_adams.genres.add(self.genre_rock)

        self.artist_feast = Artist.objects.create(name=".Feast", hometown="Jakarta")
        self.artist_feast.genres.add(self.genre_rock)

        # 3. Create Gigss: One TODAY, one TOMORROW
        now = timezone.localtime(timezone.now())
        today = now.date()
        today_time = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())) + timedelta(hours=19)
        tomorrow_time = today_time + timedelta(days=1)

        # Gigs Today in Jakarta with The Adams
        self.Gigs_today = Gigs.objects.create(
            title="Jakarta Rock Night",
            venue=self.venue_jakarta,
            start_datetime=today_time,
            ticket_price=75000,
            status=GigsStatus.SCHEDULED
        )
        GigsLineup.objects.create(
            Gigs=self.Gigs_today,
            artist=self.artist_adams,
            set_time="20:00 WIB",
            is_headliner=True,
            order=1
        )

        # Gigs Tomorrow in Bandung with .Feast
        self.Gigs_tomorrow = Gigs.objects.create(
            title="Bandung Distortion",
            venue=self.venue_bandung,
            start_datetime=tomorrow_time,
            ticket_price=0,
            is_free=True,
            status=GigsStatus.SCHEDULED
        )
        GigsLineup.objects.create(
            Gigs=self.Gigs_tomorrow,
            artist=self.artist_feast,
            set_time="19:30 WIB",
            is_headliner=True,
            order=1
        )

    def test_get_all_Gigss(self):
        """Verifies that /api/Gigss/ returns HTTP 200 and lists all Gigss."""
        response = self.client.get('/api/Gigss/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results should contain 2 Gigss
        data = response.json()
        results = data.get('results', data)
        self.assertEqual(len(results), 2)

    def test_today_Gigss_radar(self):
        """Verifies that /api/Gigss/today/ correctly isolates only Gigss happening today."""
        response = self.client.get('/api/Gigss/today/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_Gigss_today'], 1)
        self.assertEqual(data['Gigss'][0]['title'], "Jakarta Rock Night")

    def test_filter_by_city(self):
        """Verifies that filtering by city (?city=Bandung) only returns Bandung Gigss."""
        response = self.client.get('/api/Gigss/?city=Bandung')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get('results', data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['venue_city'], "Bandung")

    def test_search_by_artist_name(self):
        """Verifies that searching for 'Adams' returns the Gigs featuring The Adams."""
        response = self.client.get('/api/Gigss/?search=Adams')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get('results', data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Jakarta Rock Night")

    def test_cities_endpoint(self):
        """Verifies that /api/Gigss/cities/ returns active cities."""
        response = self.client.get('/api/Gigss/cities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cities = response.json()
        self.assertIn("Jakarta Selatan", cities)
        self.assertIn("Bandung", cities)

    def test_sync_live_endpoint(self):
        """Verifies that /api/Gigss/sync_live/ triggers automated sync successfully."""
        response = self.client.get('/api/Gigss/sync_live/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('Sinkronisasi', data['message'])

    def test_bandsintown_service_sync(self):
        """Verifies that BandsintownService dynamically creates Artist, Venues, Gigss, and Lineups."""
        from apps.gigs.services.bandsintown import BandsintownService
        service = BandsintownService()
        result = service.sync_artist_events("Pamungkas", use_mock=True)

        self.assertTrue(result['success'])
        self.assertEqual(result['artist'], "Pamungkas")
        self.assertGreater(result['Gigss_created'], 0)

        # Check that artist exists in DB
        pamungkas = Artist.objects.filter(name="Pamungkas").first()
        self.assertIsNotNone(pamungkas)

        # Check that Gigss were created with Pamungkas in lineup
        Gigss = Gigs.objects.filter(lineups__artist=pamungkas)
        self.assertGreater(Gigss.count(), 0)

    def test_bandsintown_api_endpoint(self):
        """Verifies that POST /api/Gigss/sync-bandsintown/ triggers sync via API."""
        payload = {"artist": "NIKI", "use_mock": True}
        response = self.client.post('/api/Gigss/sync-bandsintown/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['total_artists_synced'], 1)
        self.assertEqual(data['results'][0]['artist'], "NIKI")

    def test_bandsintown_api_validation(self):
        """Verifies that POST /api/Gigss/sync-bandsintown/ rejects missing artist/all."""
        response = self.client.post('/api/Gigss/sync-bandsintown/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_past_Gigs_auto_filtered(self):
        """Verifies that past/yesterday Gigss are automatically excluded from the main list."""
        yesterday_time = timezone.now() - timedelta(days=1)
        past_Gigs = Gigs.objects.create(
            title="Yesterday Indie Fest",
            venue=self.venue_jakarta,
            start_datetime=yesterday_time,
            ticket_price=50000,
            status=GigsStatus.COMPLETED
        )

        # 1. Default GET /api/Gigss/ should NOT include yesterday's Gigs
        response = self.client.get('/api/Gigss/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get('results', data)
        titles = [g['title'] for g in results]
        self.assertNotIn("Yesterday Indie Fest", titles)

        # 2. GET /api/Gigss/?include_past=true SHOULD include yesterday's Gigs
        response_all = self.client.get('/api/Gigss/?include_past=true')
        self.assertEqual(response_all.status_code, status.HTTP_200_OK)
        data_all = response_all.json()
        results_all = data_all.get('results', data_all)
        titles_all = [g['title'] for g in results_all]
        self.assertIn("Yesterday Indie Fest", titles_all)

    def test_anti_404_resolved_ticket_url(self):
        """Verifies that generic 404-prone ticket URLs resolve to official search queries."""
        Gigs = Gigs.objects.create(
            title="Morfem Live at Rossi Musik",
            venue=self.venue_jakarta,
            start_datetime=timezone.now() + timedelta(days=2),
            ticket_url="https://www.loket.com/event/morfem-jakarta-pusat"
        )
        self.assertIn("loket.com/search?q=Morfem", Gigs.resolved_ticket_url)

        # Also test in API serializer response
        response = self.client.get(f'/api/Gigss/{Gigs.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("loket.com/search?q=Morfem", data['ticket_url'])

    def test_real_concert_scraper_sync(self):
        """Verifies that RealConcertScraperService syncs verified authentic concerts and can clean dummy data."""
        from apps.gigs.services.real_concert_scraper import RealConcertScraperService
        service = RealConcertScraperService()
        result = service.sync_all_verified(clean_dummy=True)

        self.assertTrue(result['success'])
        self.assertGreater(result['total_synced'], 0)

        # Check that Synchronize Fest exists
        sync_fest = Gigs.objects.filter(title__icontains="Synchronize Fest").first()
        self.assertIsNotNone(sync_fest)
        self.assertEqual(sync_fest.ticket_url, "https://synchronizefestival.com/tickets")
        self.assertEqual(sync_fest.resolved_ticket_url, "https://synchronizefestival.com/tickets")

        # Check that lineups were properly created
        self.assertGreater(sync_fest.lineups.count(), 0)

    def test_sync_verified_api_endpoint(self):
        """Verifies POST /api/Gigss/sync-verified/ executes sync via API."""
        response = self.client.post('/api/Gigss/sync-verified/', {'clean_dummy': False}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertGreater(data['total_synced'], 0)

    def test_ticket_platform_detection_without_numeric_price(self):
        """
        Verifies that posters mentioning ticket platforms (GOERS, Artatix, detikevent)
        without numeric prices are correctly marked as is_free=False (Paid/Berbayar).
        """
        from apps.gigs.services.poster_ai import PosterAIService
        service = PosterAIService(api_key="dummy")
        extracted = {
            "title": "Remember Fest 2026 x Cube Concert",
            "artists": ["Dewa 19", "Ada Band", "Padi Reborn", "Jamrud", "Hindia", "Tulus"],
            "venue_name": "Gambir Expo Kemayoran",
            "city": "Jakarta",
            "date": "2026-11-07",
            "doors_open": "TBA",
            "ticket_price": 0,
            "is_free": False,
            "ticket_url": "https://goersapp.com",
            "description": "Tiket dapat dibeli di GOERS, Artatix, detikevent"
        }
        normalized = service.normalize_extracted_data(extracted)
        self.assertFalse(normalized["is_free"])
        self.assertEqual(normalized["ticket_price"], 0)

        # Test saving to database
        Gigs = service.save_Gigs_to_database(normalized)
        self.assertFalse(Gigs.is_free)
        self.assertEqual(Gigs.price_range_display, "Cek Platform Tiket")



