from django.core.management.base import BaseCommand
from apps.gigs.services.telegram_bot import TelegramPosterBot

class Command(BaseCommand):
    help = "Menjalankan GigTrack Telegram Bot Polling untuk menerima dan memproses poster konser dari HP"

    def add_arguments(self, parser):
        parser.add_argument(
            '--token',
            type=str,
            help='Override Telegram Bot Token (opsional, default membaca TELEGRAM_BOT_TOKEN dari .env)',
        )

    def handle(self, *args, **options):
        token = options.get('token')
        self.stdout.write(self.style.SUCCESS("="*55))
        self.stdout.write(self.style.SUCCESS("[*] GIGTRACK TELEGRAM BOT SCANNER WORKER"))
        self.stdout.write(self.style.SUCCESS("="*55))
        
        try:
            bot = TelegramPosterBot(token=token)
            self.stdout.write(self.style.NOTICE("Menghubungkan ke server Telegram..."))
            bot.run_polling()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nBot dimatikan."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error menjalankan bot: {e}"))

