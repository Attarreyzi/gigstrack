from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from apps.venues.models import Venue
from apps.artists.models import Artist, Genre
from apps.gigs.models import Gig, GigLineup, GigStatus

class GigTrackAPITests(TestCase):
    """
    Automated Unit & Integration Tests for GigTrack Backend API.
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

        # 3. Create Gigs: One TODAY, one TOMORROW
        now = timezone.localtime(timezone.now())
        today = now.date()
        today_time = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time())) + timedelta(hours=19)
        tomorrow_time = today_time + timedelta(days=1)

        # Gig Today in Jakarta with The Adams
        self.gig_today = Gig.objects.create(
            title="Jakarta Rock Night",
            venue=self.venue_jakarta,
            start_datetime=today_time,
            ticket_price=75000,
            status=GigStatus.SCHEDULED
        )
        GigLineup.objects.create(
            gig=self.gig_today,
            artist=self.artist_adams,
            set_time="20:00 WIB",
            is_headliner=True,
            order=1
        )

        # Gig Tomorrow in Bandung with .Feast
        self.gig_tomorrow = Gig.objects.create(
            title="Bandung Distortion",
            venue=self.venue_bandung,
            start_datetime=tomorrow_time,
            ticket_price=0,
            is_free=True,
            status=GigStatus.SCHEDULED
        )
        GigLineup.objects.create(
            gig=self.gig_tomorrow,
            artist=self.artist_feast,
            set_time="19:30 WIB",
            is_headliner=True,
            order=1
        )

    def test_get_all_gigs(self):
        """Verifies that /api/gigs/ returns HTTP 200 and lists all gigs."""
        response = self.client.get('/api/gigs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results should contain 2 gigs
        data = response.json()
        results = data.get('results', data)
        self.assertEqual(len(results), 2)

    def test_today_gigs_radar(self):
        """Verifies that /api/gigs/today/ correctly isolates only gigs happening today."""
        response = self.client.get('/api/gigs/today/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_gigs_today'], 1)
        self.assertEqual(data['gigs'][0]['title'], "Jakarta Rock Night")

    def test_filter_by_city(self):
        """Verifies that filtering by city (?city=Bandung) only returns Bandung gigs."""
        response = self.client.get('/api/gigs/?city=Bandung')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get('results', data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['venue_city'], "Bandung")

    def test_search_by_artist_name(self):
        """Verifies that searching for 'Adams' returns the gig featuring The Adams."""
        response = self.client.get('/api/gigs/?search=Adams')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get('results', data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Jakarta Rock Night")

    def test_cities_endpoint(self):
        """Verifies that /api/gigs/cities/ returns active cities."""
        response = self.client.get('/api/gigs/cities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cities = response.json()
        self.assertIn("Jakarta Selatan", cities)
        self.assertIn("Bandung", cities)

    def test_sync_live_endpoint(self):
        """Verifies that /api/gigs/sync_live/ triggers automated sync successfully."""
        response = self.client.get('/api/gigs/sync_live/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('Sinkronisasi', data['message'])

    def test_bandsintown_service_sync(self):
        """Verifies that BandsintownService dynamically creates Artist, Venues, Gigs, and Lineups."""
        from apps.gigs.services.bandsintown import BandsintownService
        service = BandsintownService()
        result = service.sync_artist_events("Pamungkas", use_mock=True)

        self.assertTrue(result['success'])
        self.assertEqual(result['artist'], "Pamungkas")
        self.assertGreater(result['gigs_created'], 0)

        # Check that artist exists in DB
        pamungkas = Artist.objects.filter(name="Pamungkas").first()
        self.assertIsNotNone(pamungkas)

        # Check that gigs were created with Pamungkas in lineup
        gigs = Gig.objects.filter(lineups__artist=pamungkas)
        self.assertGreater(gigs.count(), 0)

    def test_bandsintown_api_endpoint(self):
        """Verifies that POST /api/gigs/sync-bandsintown/ triggers sync via API."""
        payload = {"artist": "NIKI", "use_mock": True}
        response = self.client.post('/api/gigs/sync-bandsintown/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['total_artists_synced'], 1)
        self.assertEqual(data['results'][0]['artist'], "NIKI")

    def test_bandsintown_api_validation(self):
        """Verifies that POST /api/gigs/sync-bandsintown/ rejects missing artist/all."""
        response = self.client.post('/api/gigs/sync-bandsintown/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_past_gig_auto_filtered(self):
        """Verifies that past/yesterday gigs are automatically excluded from the main list."""
        yesterday_time = timezone.now() - timedelta(days=1)
        past_gig = Gig.objects.create(
            title="Yesterday Indie Fest",
            venue=self.venue_jakarta,
            start_datetime=yesterday_time,
            ticket_price=50000,
            status=GigStatus.COMPLETED
        )

        # 1. Default GET /api/gigs/ should NOT include yesterday's gig
        response = self.client.get('/api/gigs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get('results', data)
        titles = [g['title'] for g in results]
        self.assertNotIn("Yesterday Indie Fest", titles)

        # 2. GET /api/gigs/?include_past=true SHOULD include yesterday's gig
        response_all = self.client.get('/api/gigs/?include_past=true')
        self.assertEqual(response_all.status_code, status.HTTP_200_OK)
        data_all = response_all.json()
        results_all = data_all.get('results', data_all)
        titles_all = [g['title'] for g in results_all]
        self.assertIn("Yesterday Indie Fest", titles_all)

    def test_anti_404_resolved_ticket_url(self):
        """Verifies that generic 404-prone ticket URLs resolve to official search queries."""
        gig = Gig.objects.create(
            title="Morfem Live at Rossi Musik",
            venue=self.venue_jakarta,
            start_datetime=timezone.now() + timedelta(days=2),
            ticket_url="https://www.loket.com/event/morfem-jakarta-pusat"
        )
        self.assertIn("loket.com/search?q=Morfem", gig.resolved_ticket_url)

        # Also test in API serializer response
        response = self.client.get(f'/api/gigs/{gig.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("loket.com/search?q=Morfem", data['ticket_url'])

