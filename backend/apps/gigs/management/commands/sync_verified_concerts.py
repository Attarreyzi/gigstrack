from django.core.management.base import BaseCommand
from apps.gigs.services.real_concert_scraper import RealConcertScraperService

class Command(BaseCommand):
    help = 'Sinkronisasi konser dan festival musik nyata terverifikasi di Indonesia (dengan opsi hapus dummy).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Hapus seluruh data gig dummy/simulasi lama sebelum memasukkan data nyata.',
        )

    def handle(self, *args, **options):
        clean_dummy = options.get('clean', False)
        self.stdout.write(self.style.WARNING(f"Memulai sinkronisasi konser nyata (clean_dummy={clean_dummy})..."))

        service = RealConcertScraperService()
        result = service.sync_all_verified(clean_dummy=clean_dummy)

        if clean_dummy:
            self.stdout.write(self.style.SUCCESS(f"[OK] Berhasil membersihkan {result['deleted_dummy_count']} data gig dummy lama."))

        self.stdout.write(self.style.SUCCESS(f"[OK] Berhasil menyinkronkan {result['total_synced']} konser nyata terverifikasi!"))
        for g in result['gigs']:
            self.stdout.write(f"  * [{g['date']}] {g['title']} @ {g['venue']} ({g['city']}) -> {g['ticket_url']}")
