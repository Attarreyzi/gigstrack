import os
import time
import uuid
import logging
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from apps.gigs.models import Gig
from apps.gigs.services.poster_ai import PosterAIService

logger = logging.getLogger(__name__)

class TelegramPosterBot:
    def __init__(self, token: str = None):
        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN') or getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN belum diset di .env atau settings.")
        
        self.api_base = f"https://api.telegram.org/bot{self.token}"
        self.file_base = f"https://api.telegram.org/file/bot{self.token}"
        # {session_id: {"data": dict, "photo_bytes": bytes, "file_name": str, "chat_id": int}}
        self.pending_scans = {}
        # {chat_id: session_id}
        self.active_chat_sessions = {}

    def send_request(self, method: str, data: dict = None, files: dict = None, timeout: int = 10) -> dict:
        url = f"{self.api_base}/{method}"
        try:
            r = requests.post(url, json=data if not files else None, data=data if files else None, files=files, timeout=timeout)
            return r.json()
        except Exception as e:
            logger.error(f"Telegram API request error ({method}): {e}")
            return {"ok": False, "error": str(e)}

    def send_message(self, chat_id: int, text: str, reply_markup: dict = None, parse_mode: str = "HTML") -> dict:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self.send_request("sendMessage", data=payload)

    def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: dict = None, parse_mode: str = "HTML") -> dict:
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self.send_request("editMessageText", data=payload)

    def answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = False):
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
            payload["show_alert"] = show_alert
        return self.send_request("answerCallbackQuery", data=payload)

    def download_file_bytes(self, file_id: str) -> tuple[bytes, str]:
        res = self.send_request("getFile", data={"file_id": file_id})
        if not res.get("ok"):
            raise ValueError("Gagal mengambil file info dari Telegram.")
        
        file_path = res["result"]["file_path"]
        download_url = f"{self.file_base}/{file_path}"
        
        r = requests.get(download_url, timeout=20)
        if r.status_code != 200:
            raise ValueError(f"Gagal download file: HTTP {r.status_code}")
        
        file_name = os.path.basename(file_path)
        return r.content, file_name

    def format_review_card(self, extracted: dict, is_corrected: bool = False) -> tuple[str, dict]:
        price_str = "<b>GRATIS / Free Entry</b>" if extracted.get("is_free") else f"<b>Rp {extracted.get('ticket_price', 0):,}</b>"
        lineup_str = ", ".join(extracted.get("artists", [])) or "Belum terdeteksi"
        confidence = int(extracted.get("confidence_score", 0.9) * 100)

        header = "✏️ <b>DATA BERHASIL DIPERBARUI:</b>\n\n" if is_corrected else "✨ <b>HASIL DETEKSI POSTER IG:</b>\n\n"

        review_text = (
            f"{header}"
            f"🎸 <b>Acara:</b> {extracted.get('title')}\n"
            f"👥 <b>Lineup:</b> {lineup_str}\n"
            f"📍 <b>Venue:</b> {extracted.get('venue_name')}, {extracted.get('city')}\n"
            f"📅 <b>Tanggal:</b> {extracted.get('date')} ({extracted.get('time', '19:00')} WIB)\n"
            f"🚪 <b>Open Gate:</b> {extracted.get('doors_open')}\n"
            f"🎟️ <b>HTM:</b> {price_str}\n"
            f"🔗 <b>Tiket:</b> {extracted.get('ticket_url')}\n"
            f"🎯 <b>AI Confidence:</b> {confidence}%\n\n"
            "💡 <i>Ada yang salah? Ketik saja langsung koreksinya di chat ini!\n"
            "Contoh: <code>ubah tanggal jadi 25 Nov</code> atau <code>ganti venue ke GBK Senayan</code></i>"
        )

        return review_text

    def handle_update(self, update: dict):
        if "callback_query" in update:
            self.handle_callback(update["callback_query"])
            return

        message = update.get("message")
        if not message:
            return

        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        # Command /start or /help
        if text.startswith("/start") or text.startswith("/help"):
            welcome_text = (
                "👋 <b>Selamat datang di GigTrack Scanner Bot!</b>\n\n"
                "📸 <b>Cara Penggunaan:</b>\n"
                "1. Kirim screenshot / foto <b>poster konser musik</b> ke sini.\n"
                "2. AI Gemini Vision akan otomatis membaca data konser.\n"
                "3. Jika ada yang salah, <b>cukup ketik koreksinya</b> (misal: <i>ubah tanggal jadi 20 Okt</i>).\n"
                "4. Klik tombol <b>Simpan ke GigTrack</b> untuk mempublikasikannya.\n\n"
                "📋 <b>Command Lain:</b>\n"
                "• <code>/list</code> : Melihat daftar konser terbaru di GigTrack\n"
                "• <code>/delete &lt;id&gt;</code> : Menghapus konser dari database"
            )
            self.send_message(chat_id, welcome_text)
            return

        # Command /list
        if text.startswith("/list"):
            recent_gigs = Gig.objects.select_related('venue').order_by('-id')[:5]
            if not recent_gigs.exists():
                self.send_message(chat_id, "ℹ️ Belum ada konser tersimpan di database GigTrack.")
                return

            list_text = "📋 <b>DAFTAR KONSER TERBARU DI GIGTRACK:</b>\n\n"
            inline_keyboard = []
            for g in recent_gigs:
                list_text += f"• <b>[ID: {g.id}]</b> {g.title} @ {g.venue.name} ({g.start_datetime.strftime('%d %b %Y')})\n"
                inline_keyboard.append([
                    {"text": f"🗑️ Hapus ID {g.id} ({g.title[:15]}...)", "callback_data": f"delgig:{g.id}"}
                ])
            
            self.send_message(chat_id, list_text, reply_markup={"inline_keyboard": inline_keyboard})
            return

        # Command /delete <id>
        if text.startswith("/delete"):
            parts = text.split()
            if len(parts) > 1 and parts[1].isdigit():
                gig_id = int(parts[1])
                deleted, _ = Gig.objects.filter(id=gig_id).delete()
                if deleted:
                    self.send_message(chat_id, f"✅ Konser <b>ID {gig_id}</b> berhasil dihapus dari GigTrack.")
                else:
                    self.send_message(chat_id, f"❌ Konser <b>ID {gig_id}</b> tidak ditemukan.")
            else:
                self.send_message(chat_id, "⚠️ Format salah. Gunakan: <code>/delete 123</code>")
            return

        # Handle Photo
        if "photo" in message:
            photos = message["photo"]
            best_photo = photos[-1]
            file_id = best_photo["file_id"]
            self.process_incoming_poster(chat_id, file_id)
            return

        # Handle Document (uncompressed image)
        if "document" in message and message["document"].get("mime_type", "").startswith("image/"):
            file_id = message["document"]["file_id"]
            self.process_incoming_poster(chat_id, file_id)
            return

        # Handle Text Correction if there is an active session
        session_id = self.active_chat_sessions.get(chat_id)
        if session_id and session_id in self.pending_scans and text:
            self.apply_user_text_correction(chat_id, session_id, text)
            return

        # Default reply if unknown text
        if text:
            self.send_message(
                chat_id,
                "📸 Silakan kirimkan <b>foto poster konser</b> untuk memulai scan,\n"
                "atau ketik <code>/list</code> untuk melihat konser yang sudah tersimpan."
            )

    def process_incoming_poster(self, chat_id: int, file_id: str):
        wait_msg = self.send_message(
            chat_id,
            "🔍 <b>Menganalisis poster dengan Gemini Vision AI...</b>\n<i>Mohon tunggu sebentar...</i>"
        )
        wait_msg_id = wait_msg.get("result", {}).get("message_id")

        try:
            image_bytes, file_name = self.download_file_bytes(file_id)
            
            ai_service = PosterAIService()
            extracted = ai_service.analyze_poster(image_bytes=image_bytes)

            if not extracted.get("success"):
                err_text = f"❌ <b>Gagal membaca poster:</b>\n{extracted.get('error', 'Format tidak terbaca')}"
                if wait_msg_id:
                    self.edit_message(chat_id, wait_msg_id, err_text)
                else:
                    self.send_message(chat_id, err_text)
                return

            session_id = str(uuid.uuid4())[:8]
            self.pending_scans[session_id] = {
                "data": extracted,
                "photo_bytes": image_bytes,
                "file_name": file_name,
                "chat_id": chat_id
            }
            self.active_chat_sessions[chat_id] = session_id

            review_text = self.format_review_card(extracted, is_corrected=False)

            inline_keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ Simpan ke GigTrack", "callback_data": f"save:{session_id}"},
                        {"text": "❌ Batal", "callback_data": f"cancel:{session_id}"}
                    ]
                ]
            }

            if wait_msg_id:
                self.edit_message(chat_id, wait_msg_id, review_text, reply_markup=inline_keyboard)
            else:
                self.send_message(chat_id, review_text, reply_markup=inline_keyboard)

        except Exception as e:
            logger.error(f"Error processing poster on Telegram: {e}")
            err_msg = f"⚠️ <b>Terjadi kesalahan:</b>\n<code>{str(e)}</code>"
            if wait_msg_id:
                self.edit_message(chat_id, wait_msg_id, err_msg)
            else:
                self.send_message(chat_id, err_msg)

    def apply_user_text_correction(self, chat_id: int, session_id: str, correction_text: str):
        scan_item = self.pending_scans.get(session_id)
        if not scan_item:
            return

        wait_msg = self.send_message(
            chat_id,
            f"🤖 <i>Menerapkan koreksi: \"{correction_text}\"...</i>"
        )
        wait_msg_id = wait_msg.get("result", {}).get("message_id")

        try:
            ai_service = PosterAIService()
            updated_data = ai_service.apply_corrections(scan_item["data"], correction_text)
            
            scan_item["data"] = updated_data
            self.pending_scans[session_id] = scan_item

            review_text = self.format_review_card(updated_data, is_corrected=True)

            inline_keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ Simpan ke GigTrack", "callback_data": f"save:{session_id}"},
                        {"text": "❌ Batal", "callback_data": f"cancel:{session_id}"}
                    ]
                ]
            }

            if wait_msg_id:
                self.edit_message(chat_id, wait_msg_id, review_text, reply_markup=inline_keyboard)
            else:
                self.send_message(chat_id, review_text, reply_markup=inline_keyboard)

        except Exception as e:
            logger.error(f"Error applying text correction: {e}")
            if wait_msg_id:
                self.edit_message(chat_id, wait_msg_id, f"⚠️ Gagal menerapkan koreksi: {e}")

    def handle_callback(self, callback_query: dict):
        cq_id = callback_query["id"]
        data = callback_query.get("data", "")
        message = callback_query.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        message_id = message.get("message_id")

        if not data or ":" not in data:
            self.answer_callback_query(cq_id, "Aksi tidak valid.")
            return

        action, payload = data.split(":", 1)

        # Handle Delete Gig from list
        if action == "delgig":
            if payload.isdigit():
                gig_id = int(payload)
                Gig.objects.filter(id=gig_id).delete()
                self.answer_callback_query(cq_id, f"Konser ID {gig_id} dihapus!", show_alert=True)
                self.edit_message(chat_id, message_id, f"🗑️ <b>Konser ID {gig_id} telah dihapus dari GigTrack.</b>")
            return

        session_id = payload
        scan_item = self.pending_scans.get(session_id)
        if not scan_item:
            self.answer_callback_query(cq_id, "Sesi ini sudah selesai atau kadaluarsa.", show_alert=True)
            self.edit_message(chat_id, message_id, "⚠️ <i>Sesi scan ini sudah selesai atau telah diproses.</i>")
            return

        if action == "cancel":
            self.answer_callback_query(cq_id, "Scan dibatalkan.")
            self.pending_scans.pop(session_id, None)
            self.active_chat_sessions.pop(chat_id, None)
            self.edit_message(chat_id, message_id, "❌ <b>Proses dibatalkan.</b> Poster tidak disimpan.")
            return

        if action == "save":
            self.answer_callback_query(cq_id, "Menyimpan ke database...")
            try:
                ai_service = PosterAIService()
                poster_file = ContentFile(scan_item["photo_bytes"], name=scan_item["file_name"])
                gig = ai_service.save_gig_to_database(scan_item["data"], poster_file=poster_file)
                
                self.pending_scans.pop(session_id, None)
                self.active_chat_sessions.pop(chat_id, None)

                success_text = (
                    "🎉 <b>BERHASIL DITAMBAHKAN KE GIGTRACK!</b>\n\n"
                    f"🎸 <b>Acara:</b> {gig.title}\n"
                    f"📍 <b>Venue:</b> {gig.venue.name} ({gig.venue.city})\n"
                    f"📅 <b>Jadwal:</b> {gig.start_datetime.strftime('%d %B %Y - %H:%M WIB')}\n"
                    f"👥 <b>Total Lineup:</b> {gig.lineups.count()} Band\n"
                    f"🎟️ <b>HTM:</b> {'GRATIS' if gig.is_free else f'Rp {gig.ticket_price:,}'}\n\n"
                    f"🌐 <i>Konser sekarang sudah aktif dan tayang di radar GigTrack!</i>\n"
                    f"💡 <i>Ketik <code>/list</code> untuk melihat atau mengelola daftar konser.</i>"
                )
                self.edit_message(chat_id, message_id, success_text)

            except Exception as e:
                logger.error(f"Error saving gig from Telegram callback: {e}")
                self.edit_message(chat_id, message_id, f"❌ <b>Gagal menyimpan ke database:</b>\n<code>{str(e)}</code>")

    def run_polling(self):
        logger.info("Memulai polling Telegram Bot...")
        offset = None

        me = self.send_request("getMe")
        if me.get("ok"):
            bot_info = me["result"]
            print(f"[OK] Telegram Bot Aktif: @{bot_info.get('username')} ({bot_info.get('first_name')})")
            print("[*] Fitur Koreksi Teks & Edit Konser Aktif!")
            print("[*] Siap menerima screenshot poster dari HP...")
        else:
            print(f"[!] Gagal inisialisasi Bot: {me}")
            return

        while True:
            try:
                params = {"timeout": 25}
                if offset:
                    params["offset"] = offset

                res = self.send_request("getUpdates", data=params, timeout=30)
                if res.get("ok"):
                    updates = res.get("result", [])
                    for update in updates:
                        offset = update["update_id"] + 1
                        self.handle_update(update)
                else:
                    time.sleep(2)
            except KeyboardInterrupt:
                print("\n[!] Polling dihentikan oleh user.")
                break
            except Exception as e:
                logger.error(f"Polling loop exception: {e}")
                time.sleep(3)
