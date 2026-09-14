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
