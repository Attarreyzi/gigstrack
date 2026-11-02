import json
import logging
import threading
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.gigs.services.telegram_bot import TelegramPosterBot

logger = logging.getLogger(__name__)

# Reusable bot instance for webhook
_bot_instance = None

def get_bot():
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = TelegramPosterBot()
    return _bot_instance


@csrf_exempt
def telegram_webhook(request):
    """
    Endpoint yang menerima kiriman pesan / foto otomatis dari server Telegram secara real-time.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed. Use POST."}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception as e:
        logger.error(f"Gagal parse webhook body: {e}")
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    try:
        bot = get_bot()
        # Eksekusi pemrosesan update di thread terpisah agar Telegram segera menerima respon 200 OK
        threading.Thread(target=bot.handle_update, args=(data,), daemon=True).start()
        return JsonResponse({"ok": True, "message": "Update queued successfully"})
    except Exception as e:
        logger.error(f"Error handling webhook update: {e}")
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


def set_webhook(request):
    """
    Helper untuk mendaftarkan URL webhook ke server Telegram dengan satu klik di browser.
    Contoh: https://attar.pythonanywhere.com/api/telegram/set-webhook/
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    if not token:
        return JsonResponse({"ok": False, "error": "TELEGRAM_BOT_TOKEN belum diset di server."}, status=400)

    # Deteksi URL otomatis jika tidak ada parameter ?url=
    custom_url = request.GET.get('url')
    if custom_url:
        webhook_url = custom_url
    else:
        host = request.get_host()
        webhook_url = f"https://{host}/api/telegram/webhook/"

    tg_api = f"https://api.telegram.org/bot{token}/setWebhook"
    try:
        res = requests.post(tg_api, json={"url": webhook_url}, timeout=15)
        result = res.json()
        result["registered_url"] = webhook_url
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


def webhook_info(request):
    """
    Mengecek status webhook Telegram saat ini.
    Contoh: https://attar.pythonanywhere.com/api/telegram/webhook-info/
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    if not token:
        return JsonResponse({"ok": False, "error": "TELEGRAM_BOT_TOKEN belum diset di server."}, status=400)

    tg_api = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    try:
        res = requests.get(tg_api, timeout=15)
        return JsonResponse(res.json())
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


def delete_webhook(request):
    """
    Menghapus webhook Telegram jika ingin kembali menggunakan polling di CMD.
    Contoh: https://attar.pythonanywhere.com/api/telegram/delete-webhook/
    """
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    if not token:
        return JsonResponse({"ok": False, "error": "TELEGRAM_BOT_TOKEN belum diset di server."}, status=400)

    tg_api = f"https://api.telegram.org/bot{token}/deleteWebhook"
    try:
        res = requests.post(tg_api, timeout=15)
        return JsonResponse(res.json())
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)

