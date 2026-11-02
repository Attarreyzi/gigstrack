import os
import mimetypes
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from apps.gigs.services.poster_ai import PosterAIService

class Command(BaseCommand):
    help = "Ekstrak dan import data konser musik Indonesia dari screenshot/foto poster Instagram menggunakan Gemini Vision AI"

    def add_arguments(self, parser):
        parser.add_argument(
            'image_path',
            type=str,
            help='Path file gambar poster di lokal (contoh: "C:\\path\\ke\\poster.jpg" atau "poster.png")',
        )
        parser.add_argument(
            '--preview',
            action='store_true',
            help='Hanya tampilkan hasil ekstraksi AI di terminal tanpa menyimpannya ke database',
        )
        parser.add_argument(
            '--api-key',
            type=str,
            help='Override Gemini API key (opsional, default membaca GEMINI_API_KEY dari .env)',
        )

    def handle(self, *args, **options):
        image_path = options['image_path']
        preview_only = options.get('preview', False)
        api_key = options.get('api_key')

        if not os.path.exists(image_path):
            raise CommandError(f"File gambar tidak ditemukan di path: '{image_path}'")

        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith('image/'):
            mime_type = 'image/jpeg'

        self.stdout.write(self.style.NOTICE(f"\n[1/3] 🔍 Membaca file poster: {os.path.basename(image_path)}"))
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        self.stdout.write(self.style.NOTICE(f"[2/3] 🤖 Memproses OCR & Visual Understanding dengan Gemini Vision AI..."))
        
        try:
            service = PosterAIService(api_key=api_key)
            result = service.analyze_poster(image_bytes=image_bytes, mime_type=mime_type)
        except Exception as e:
            raise CommandError(f"Gagal memproses gambar dengan AI: {e}")

        if not result.get("success"):
            raise CommandError(f"AI gagal mengekstrak data: {result.get('error', 'Format tidak dikenali')}")

        # Tampilkan ringkasan ekstraksi
        self.stdout.write(self.style.SUCCESS("\n" + "="*50))
        self.stdout.write(self.style.SUCCESS("✨ HASIL EKSTRAKSI POSTER (AI GEMINI VISION)"))
        self.stdout.write(self.style.SUCCESS("="*50))
        self.stdout.write(f" 🎸 Nama Acara   : {result.get('title')}")
        self.stdout.write(f" 👥 Lineup Band   : {', '.join(result.get('artists', []))}")
        if result.get('headliner'):
            self.stdout.write(f" ⭐ Headliner     : {result.get('headliner')}")
        self.stdout.write(f" 📍 Venue         : {result.get('venue_name')}, {result.get('city')}")
        self.stdout.write(f" 📅 Tanggal & Jam : {result.get('date')} ({result.get('time', '19:00')} WIB)")
        self.stdout.write(f" 🚪 Open Gate     : {result.get('doors_open')}")
        
        price_text = "GRATIS / FREE ENTRY" if result.get('is_free') else f"Rp {result.get('ticket_price', 0):,}"
        self.stdout.write(f" 🎟️  Harga Tiket   : {price_text}")
        self.stdout.write(f" 🔗 Link Tiket    : {result.get('ticket_url')}")
        self.stdout.write(f" 🏷️  Genre Musik   : {', '.join(result.get('genres', []))}")
        self.stdout.write(f" 🎯 AI Confidence : {int(result.get('confidence_score', 0.9) * 100)}%")
        self.stdout.write("="*50 + "\n")

        if preview_only:
            self.stdout.write(self.style.WARNING("ℹ️  Mode --preview aktif: Data TIDAK disimpan ke database.\n"))
            return

        # Simpan ke database
        self.stdout.write(self.style.NOTICE(f"[3/3] 💾 Menyimpan konser, venue, dan lineup ke database Django..."))
        try:
            poster_content = ContentFile(image_bytes, name=os.path.basename(image_path))
            Gigs = service.save_Gigs_to_database(result, poster_file=poster_content)
            self.stdout.write(self.style.SUCCESS(
                f"\n🎉 BERHASIL! Konser '{Gigs.title}' (ID: {Gigs.id}) berhasil ditambahkan ke GigsSTRACK.\n"
                f"   - Database Venue : {Gigs.venue.name} ({Gigs.venue.city})\n"
                f"   - Total Lineup   : {Gigs.lineups.count()} band/musisi\n"
                f"   - Status         : {Gigs.get_status_display()}\n"
            ))
        except Exception as e:
            raise CommandError(f"Gagal menyimpan ke database Django: {e}")
