from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.gigs.models import Gig, GigStatus
from apps.venues.models import Venue
from apps.artists.models import Artist
from apps.gigs.services.ticketmaster import TicketmasterService

class TicketmasterIntegrationTests(TestCase):
    """
    Unit & Integration tests untuk Ticketmaster Discovery API v2 Service & Endpoint.
    """

    def setUp(self):
        self.client = APIClient()
        self.service = TicketmasterService(api_key="TEST_API_KEY")

        self.sample_event_raw = {
            "id": "tmTestEvent123",
            "name": "Radiohead - Live at Gelora Arena 2026",
            "url": "https://www.ticketmaster.com/radiohead-tickets/event/123",
            "info": "Official live concert tour in Jakarta.",
            "images": [
                {
                    "ratio": "16_9",
                    "url": "https://example.com/radiohead_16_9.jpg",
                    "width": 1024,
                    "height": 576
                }
            ],
            "dates": {
                "start": {
                    "localDate": "2026-11-20",
                    "localTime": "20:00:00",
                    "dateTime": "2026-11-20T13:00:00Z"
                },
                "status": {"code": "onsale"}
            },
            "priceRanges": [
                {"min": 500000, "max": 1500000, "currency": "IDR"}
            ],
            "_embedded": {
                "venues": [
                    {
                        "name": "Stadion Madya GBK",
                        "city": {"name": "Jakarta Pusat"},
                        "state": {"name": "DKI Jakarta"},
                        "address": {"line1": "Jl. Asia Afrika, Senayan"},
                        "location": {"latitude": "-6.2150", "longitude": "106.8010"}
                    }
                ],
                "attractions": [
                    {
                        "name": "Radiohead",
                        "classifications": [
                            {"genre": {"name": "Alternative Rock"}, "subGenre": {"name": "Art Rock"}}
                        ],
                        "images": [
                            {"ratio": "16_9", "url": "https://example.com/rh_artist.jpg", "width": 800}
                        ]
                    }
                ]
            }
        }

    def test_parse_event_data(self):
        """Uji apakah normalisasi data JSON Ticketmaster bekerja dengan benar."""
        parsed = self.service.parse_event_data(self.sample_event_raw)

        self.assertEqual(parsed["tm_id"], "tmTestEvent123")
        self.assertEqual(parsed["title"], "Radiohead - Live at Gelora Arena 2026")
        self.assertEqual(parsed["ticket_price"], 500000)
        self.assertFalse(parsed["is_free"])
        self.assertEqual(parsed["status"], GigStatus.SCHEDULED)
        self.assertEqual(parsed["venue"]["name"], "Stadion Madya GBK")
        self.assertEqual(parsed["venue"]["city"], "Jakarta Pusat")
        self.assertIn("106.8010", parsed["venue"]["maps_url"])
        self.assertEqual(len(parsed["attractions"]), 1)
        self.assertEqual(parsed["attractions"][0]["name"], "Radiohead")
        self.assertIn("Alternative Rock", parsed["attractions"][0]["genres"])

    def test_sync_events_to_db_and_deduplication(self):
        """Uji penyimpanan ke database dan pastikan tidak ada duplikasi data (idempotency)."""
        # Sinkronisasi pertama: harus membuat baris baru
        result1 = self.service.sync_events_to_db([self.sample_event_raw])
        self.assertEqual(result1["gigs_created"], 1)
        self.assertEqual(result1["gigs_updated"], 0)

        gig = Gig.objects.get(title="Radiohead - Live at Gelora Arena 2026")
        self.assertEqual(gig.venue.name, "Stadion Madya GBK")
        self.assertEqual(gig.lineups.count(), 1)
        self.assertEqual(gig.lineups.first().artist.name, "Radiohead")

        # Sinkronisasi kedua dengan data yang sama: harus update, BUKAN duplikat
        result2 = self.service.sync_events_to_db([self.sample_event_raw])
        self.assertEqual(result2["gigs_created"], 0)
        self.assertEqual(result2["gigs_updated"], 1)

        # Total baris di database tetap 1
        self.assertEqual(Gig.objects.filter(title="Radiohead - Live at Gelora Arena 2026").count(), 1)

    def test_mock_sync_workflow(self):
        """Uji mode simulasi/mock dapat berjalan tanpa error."""
        res = self.service.sync(use_mock=True)
        self.assertTrue(res["success"])
        self.assertGreater(res["total_events_processed"], 0)
        self.assertGreater(Gig.objects.count(), 0)

    def test_api_endpoint_sync_ticketmaster(self):
        """Uji endpoint API POST /api/gigs/sync-ticketmaster/."""
        response = self.client.post('/api/gigs/sync-ticketmaster/', {
            "city": "Jakarta",
            "use_mock": True
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("total_events_processed", data)
