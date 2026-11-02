import time
import sys
from django.core.management.base import BaseCommand
from apps.Gigss.services.ticketmaster import TicketmasterService

class Command(BaseCommand):
    help = "Sinkronisasi jadwal konser & tiket resmi dari Ticketmaster Discovery API v2 ke database GigsSTRACK"

    def add_arguments(self, parser):
        parser.add_argument(
            '--keyword',
            type=str,
            help='Cari nama artis, band, atau festival tertentu (contoh: "Arctic Monkeys", "Coldplay", "Jazz")',
        )
        parser.add_argument(
            '--city',
            type=str,
            default=None,
            help='Filter berdasarkan nama kota (opsional, contoh: "London", "Singapore")',
        )
        parser.add_argument(
            '--country',
            type=str,
            default='ID',
            help='Kode negara ISO-3166 (default: "ID" untuk Indonesia, atau "US", "SG", dll)',
        )
        parser.add_argument(
            '--size',
            type=int,
            default=20,
            help='Jumlah maksimum event yang ditarik per request (default: 20, maks 200)',
        )
        parser.add_argument(
            '--api-key',
            type=str,
            help='Kunci API Ticketmaster (opsional, jika ingin meng-override settings)',
        )
        parser.add_argument(
            '--mock',
            action='store_true',
            help='Gunakan mode simulasi/mock untuk pengujian tanpa memerlukan kredensial API resmi',
        )
        parser.add_argument(
            '--watch',
            action='store_true',
            help='Jalankan dalam mode daemon/background loop untuk pemantauan data real-time berkala',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='Interval pengecekan berkala dalam detik jika mode --watch aktif (default: 300 detik / 5 menit)',
        )

    def handle(self, *args, **options):
        keyword = options.get('keyword')
        city = options.get('city')
        country = options.get('country')
        size = options.get('size')
        api_key = options.get('api_key')
        use_mock = options.get('mock')
        watch_mode = options.get('watch')
        interval = options.get('interval')

        service = TicketmasterService(api_key=api_key)

        self.stdout.write(self.style.MIGRATE_HEADING("=== [GigsSTRACK] Ticketmaster Discovery API Engine ==="))
        self.stdout.write(f"Parameter: Kota='{city}', Negara='{country}', Keyword='{keyword or '-'}'")

        def run_sync_cycle():
            self.stdout.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Mengambil data dari Ticketmaster...")
            res = service.sync(
                keyword=keyword,
                city=city,
                country_code=country,
                size=size,
                use_mock=use_mock
            )

            if not res.get("success"):
                self.stdout.write(self.style.ERROR(f"[-] Gagal: {res.get('error')} - {res.get('message')}"))
                return False

            source = res.get("source", "ticketmaster")
            total = res.get("total_events_processed", 0)
            created = res.get("Gigss_created", 0)
            updated = res.get("Gigss_updated", 0)

            self.stdout.write(self.style.SUCCESS(
                f"[+] Berhasil menyinkronkan {total} event (Sumber: {source}) | Baru: {created}, Diperbarui: {updated}"
            ))

            for g in res.get("synced_Gigss", []):
                price_str = "Gratis" if g['ticket_price'] == 0 else f"Rp {g['ticket_price']:,}"
                self.stdout.write(
                    f"    * [{g['action'].upper()}] {g['title']} @ {g['venue']} ({g['city']}) | "
                    f"Tgl: {g['date']} | Tiket: {price_str}"
                )
            return True

        # Eksekusi siklus pertama
        run_sync_cycle()

        # Mode watch (Real-time monitoring daemon)
        if watch_mode:
            self.stdout.write(self.style.WARNING(
                f"\n[Real-time Watcher Aktif] Memantau perubahan data setiap {interval} detik. Tekan Ctrl+C untuk berhenti.\n"
            ))
            try:
                while True:
                    time.sleep(interval)
                    run_sync_cycle()
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS("\n[+] Pemantau real-time Ticketmaster dihentikan oleh pengguna."))
                sys.exit(0)
