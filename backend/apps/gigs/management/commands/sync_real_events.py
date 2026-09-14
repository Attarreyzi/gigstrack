from django.core.management.base import BaseCommand
from apps.gigs.services.real_events import RealEventService
from apps.gigs.services.ticket_scraper import TicketScraperService

class Command(BaseCommand):
    help = "Sinkronisasi jadwal konser nyata resmi di Jabodetabek (Pestapora, Synchronize, M Bloc, Loket, dll.)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--text',
            type=str,
            help='Teks pengumuman konser dari Instagram/WhatsApp/Twitter untuk diekstrak otomatis',
        )
        parser.add_argument(
            '--scrape-tickets',
            action='store_true',
            help='Tarik juga tiket live dari platform tiket online',
        )

    def handle(self, *args, **options):
        text_announcement = options.get('text')
        scrape_tickets = options.get('scrape_tickets')

        service = RealEventService()

        self.stdout.write(self.style.MIGRATE_HEADING("=== [GigTrack] Real Concerts Ingestion Engine ==="))

        if text_announcement:
            self.stdout.write("Mengekstrak pengumuman konser teks...")
            result = service.parse_text_announcement(text_announcement)
            self.stdout.write(self.style.SUCCESS(
                f"[OK] Berhasil memasukkan konser: {result['title']} @ {result['venue']} ({result['city']}) - {result['datetime']}"
            ))
            return

        self.stdout.write("\n1. Memasukkan Jadwal Konser Nyata Resmi Jabodetabek...")
        synced_list = service.sync_verified_concerts()
        for ev in synced_list:
            self.stdout.write(f"  * {ev['title']} @ {ev['venue']} ({ev['city']}) - {ev['date']} [{ev['status']}]")

        self.stdout.write(self.style.SUCCESS(f"\n[OK] Berhasil menyinkronkan {len(synced_list)} konser resmi nyata!"))

        if scrape_tickets:
            self.stdout.write("\n2. Menarik data tiket live dari web tiket...")
            scraper = TicketScraperService()
            tickets = scraper.fetch_megatix_events()
            self.stdout.write(f"Ditemukan {len(tickets)} event tiket live dari platform.")

        self.stdout.write(self.style.SUCCESS("\n[OK] Database GigTrack kini terisi konser-konser nyata di Jabodetabek!"))
