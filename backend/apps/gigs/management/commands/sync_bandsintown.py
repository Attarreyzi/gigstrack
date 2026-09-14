from django.core.management.base import BaseCommand
from apps.artists.models import Artist
from apps.gigs.services.bandsintown import BandsintownService, INDONESIA_POPULAR_ARTISTS

class Command(BaseCommand):
    help = "Sinkronisasi jadwal konser musisi wilayah Jabodetabek & sekitarnya dari Bandsintown API"

    def add_arguments(self, parser):
        parser.add_argument(
            '--artist',
            type=str,
            help='Nama artis / band tertentu (misal: "Reality Club", "Pamungkas", "The Adams")',
        )
        parser.add_argument(
            '--indonesia',
            '--jabodetabek',
            action='store_true',
            dest='indonesia',
            help='Sinkronkan seluruh band kurasi skena musik Jabodetabek & Indonesia (The Adams, .Feast, Hindia, Bernadya, dll)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sinkronkan seluruh artis yang ada di database GigTrack',
        )
        parser.add_argument(
            '--app-id',
            type=str,
            help='Kunci Bandsintown app_id (opsional, jika ingin meng-override settings)',
        )
        parser.add_argument(
            '--mock',
            action='store_true',
            help='Gunakan mode simulasi/mock untuk pengujian tanpa credential API resmi',
        )

    def handle(self, *args, **options):
        artist_name = options.get('artist')
        sync_indonesia = options.get('indonesia')
        sync_all = options.get('all')
        app_id = options.get('app_id')
        use_mock = options.get('mock')

        service = BandsintownService(app_id=app_id, indonesia_only=True)

        self.stdout.write(self.style.MIGRATE_HEADING("=== [GigTrack] Skena Musik Jabodetabek - Bandsintown Sync Engine ==="))

        if not artist_name and not sync_all and not sync_indonesia:
            # Default ke skena Indonesia jika tidak ada argumen khusus
            sync_indonesia = True

        artists_to_sync = []
        if artist_name:
            artists_to_sync.append(artist_name.strip())
        elif sync_indonesia:
            artists_to_sync = INDONESIA_POPULAR_ARTISTS
            self.stdout.write(f"Menyinkronkan kurasi {len(artists_to_sync)} band skena musik Indonesia...")
        elif sync_all:
            db_artists = list(Artist.objects.values_list('name', flat=True))
            if not db_artists:
                self.stdout.write(self.style.WARNING("Belum ada artis tersimpan di database untuk disinkronkan."))
                return
            artists_to_sync = db_artists
            self.stdout.write(f"Ditemukan {len(artists_to_sync)} artis di database untuk disinkronkan.")

        total_gigs_created = 0
        total_gigs_updated = 0

        for name in artists_to_sync:
            self.stdout.write(f"\nMenyinkronkan jadwal untuk: {name}...")
            result = service.sync_artist_events(name, app_id=app_id, use_mock=use_mock)

            if result.get("success"):
                source_label = "[LIVE API]" if result.get("source") == "live_api" else "[SIMULASI MOCK]"
                created = result.get("gigs_created", 0)
                updated = result.get("gigs_updated", 0)
                total_gigs_created += created
                total_gigs_updated += updated

                self.stdout.write(self.style.SUCCESS(
                    f"  {source_label} Ditemukan {result.get('events_count', 0)} konser. "
                    f"({created} gig baru dibuat, {updated} diperbarui)"
                ))

                for g in result.get("synced_gigs", []):
                    self.stdout.write(f"    * {g['title']} @ {g['venue']} ({g['city']}) - {g['datetime']}")
            else:
                self.stdout.write(self.style.ERROR(f"  [GAGAL] {result.get('message', 'Terjadi kesalahan.')}"))

        self.stdout.write(self.style.SUCCESS(
            f"\n[OK] Selesai! Total {total_gigs_created} gig dibuat, {total_gigs_updated} gig diperbarui di database."
        ))
