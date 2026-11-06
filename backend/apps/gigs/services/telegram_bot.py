import os
import time
import uuid
import html
import logging
import threading
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from apps.gigs.models import Gigs
from apps.gigs.services.poster_ai import PosterAIService

logger = logging.getLogger(__name__)

class TelegramPosterBot:
    def __init__(self, token: str = None):
        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN') or getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN belum diset di .env atau settings.")
        
        self.api_base = f"https://api.telegram.org/bot{self.token}"
        self.file_base = f"https://api.telegram.org/file/bot{self.token}"
        self.session = requests.Session()
        
        # {session_id: {"data": dict, "photo_bytes": bytes, "file_name": str, "chat_id": int}}
        self.pending_scans = {}
        # {chat_id: session_id}
        self.active_chat_sessions = {}

        # Multi-photo / Album buffering: {chat_id: [{"file_id": str, "message_id": int}, ...]}
        self.photo_buffers = {}
        self.buffer_timers = {}
        self.buffer_lock = threading.Lock()

    def send_request(self, method: str, data: dict = None, files: dict = None, timeout: int = 10) -> dict:
        url = f"{self.api_base}/{method}"
        try:
            r = self.session.post(url, json=data if not files else None, data=data if files else None, files=files, timeout=timeout)
            return r.json()
        except Exception as e:
            logger.error(f"Telegram API request error ({method}): {e}")
            return {"ok": False, "error": str(e)}

    def send_chat_action(self, chat_id: int, action: str = "typing") -> dict:
        return self.send_request("sendChatAction", data={"chat_id": chat_id, "action": action})

    def send_message(self, chat_id: int, text: str, reply_markup: dict = None, parse_mode: str = "HTML") -> dict:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        res = self.send_request("sendMessage", data=payload)
        if not res.get("ok") and parse_mode:
            payload["parse_mode"] = None
            res = self.send_request("sendMessage", data=payload)
        return res

    def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: dict = None, parse_mode: str = "HTML") -> dict:
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        res = self.send_request("editMessageText", data=payload)
        if not res.get("ok") and parse_mode:
            payload["parse_mode"] = None
            res = self.send_request("editMessageText", data=payload)
        return res

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
        
        r = self.session.get(download_url, timeout=20)
        if r.status_code != 200:
            raise ValueError(f"Gagal download file: HTTP {r.status_code}")
        
        file_name = os.path.basename(file_path)
        return r.content, file_name

    def format_review_card(self, extracted: dict, is_corrected: bool = False, photo_count: int = 1) -> str:
        def esc(val):
            return html.escape(str(val)) if val is not None else ""

        # 1. Kategori Tiket & HTM (Ringkas: Rentang Harga)
        tiers = extracted.get("ticket_tiers", [])
        prices = [t.get("price", 0) for t in tiers if isinstance(t, dict) and t.get("price", 0) > 0]
        if prices:
            min_p = min(prices)
            max_p = max(prices)
            if min_p == max_p:
                price_str = f"<b>Rp {min_p:,}</b>"
            else:
                price_str = f"<b>Rp {min_p:,} - Rp {max_p:,}</b>"
        elif extracted.get("is_free"):
            price_str = "<b>GRATIS / Free Entry</b>"
        elif extracted.get("ticket_price", 0) > 0:
            price_str = f"<b>Rp {extracted.get('ticket_price', 0):,}</b>"
        else:
            platforms = extracted.get("ticket_platforms", [])
            if platforms:
                p_text = esc(", ".join(platforms))
                price_str = f"<b>Berbayar (Tiket via {p_text})</b>"
            else:
                price_str = "<b>Berbayar (Cek Tiket di Platform Resmi)</b>"

        # 2. Open Gate
        doors = str(extracted.get("doors_open") or "TBA").strip()
        if not doors or doors.upper() in ["TBA", "NONE", "NULL", "BELUM ADA", "BELUM DIUMUMKAN"]:
            doors_display = "<i>TBA</i>"
        else:
            doors_display = esc(doors)

        # 3. Waktu Jam Mulai
        time_val = extracted.get("time")
        time_display = f" ({esc(time_val)} WIB)" if time_val and str(time_val).upper() != "TBA" else ""
        date_display = f"{esc(extracted.get('date'))}{time_display}"

        # 4. Lineup & Rundown Festival (Multi-day Support)
        lineups = extracted.get("lineups", [])
        days_dict = {}
        if isinstance(lineups, list) and len(lineups) > 0:
            for l in lineups:
                if isinstance(l, dict) and l.get("artist_name"):
                    d = l.get("day") or "Lineup"
                    days_dict.setdefault(d, []).append(l)

        if len(days_dict) > 1 or any(k.lower().startswith("day") for k in days_dict.keys()):
            lineup_section = "👥 <b>Lineup & Rundown:</b>\n"
            for day_title, items in days_dict.items():
                lineup_section += f"  <b>{esc(day_title)}:</b>\n"
                for item in items:
                    t_str = f" ({esc(item['set_time'])})" if item.get('set_time') and item['set_time'] != 'TBA' else ""
                    hl_str = " ⭐" if item.get('is_headliner') else ""
                    lineup_section += f"  - {esc(item['artist_name'])}{t_str}{hl_str}\n"
        else:
            raw_artists = extracted.get("artists", [])
            lineup_str = esc(", ".join(raw_artists)) if raw_artists else "Belum terdeteksi"
            lineup_section = f"👥 <b>Lineup:</b> {lineup_str}\n"

        confidence = int(extracted.get("confidence_score", 0.9) * 100)

        if is_corrected:
            header = "✏️ <b>DATA BERHASIL DIPERBARUI:</b>\n\n"
        elif photo_count > 1:
            header = f"✨ <b>HASIL DETEKSI {photo_count} FOTO POSTER (GABUNGAN):</b>\n\n"
        else:
            header = "✨ <b>HASIL DETEKSI POSTER:</b>\n\n"

        review_text = (
            f"{header}"
            f"🎸 <b>Acara:</b> {esc(extracted.get('title'))}\n"
            f"{lineup_section}"
            f"📍 <b>Venue:</b> {esc(extracted.get('venue_name'))}, {esc(extracted.get('city'))}\n"
            f"📅 <b>Tanggal:</b> {date_display}\n"
            f"🚪 <b>Open Gate:</b> {doors_display}\n"
            f"🎟️ <b>HTM / Tiket:</b> {price_str}\n"
            f"🔗 <b>Tiket:</b> {esc(extracted.get('ticket_url'))}\n"
            f"🎯 <b>AI Confidence:</b> {confidence}%\n\n"
            "💡 <i>Ada yang salah? Ketik saja langsung koreksinya di chat ini!\n"
            "Contoh: <code>tiket beli di aplikasi BBO</code> atau <code>ubah tanggal jadi 25 Des</code></i>"
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
                "👋 <b>Selamat datang di GigsSTRACK Scanner Bot!</b>\n\n"
                "📸 <b>Cara Penggunaan:</b>\n"
                "1. Kirim foto poster (1 foto atau multi-foto / album Instagram sekaligus).\n"
                "2. AI Gemini Vision akan otomatis membaca poster utama + rincian tiket.\n"
                "3. Foto pertama yang Anda kirim otomatis menjadi <b>foto cover utama di website</b>.\n"
                "4. Jika ada koreksi, <b>cukup ketik pesan di chat ini</b> (misal: <i>tiket beli di aplikasi BBO</i>).\n"
                "5. Klik tombol <b>Simpan ke GigsSTRACK</b> untuk langsung menampilkannya di website.\n\n"
                "📋 <b>Command Lain:</b>\n"
                "• <code>/list</code> : Melihat daftar konser terbaru di GigsSTRACK\n"
                "• <code>/delete &lt;id&gt;</code> : Menghapus konser dari database"
            )
            self.send_message(chat_id, welcome_text)
            return

        # Command /list
        if text.startswith("/list"):
            recent_Gigss = Gigs.objects.select_related('venue').order_by('-id')[:5]
            if not recent_Gigss.exists():
                self.send_message(chat_id, "ℹ️ Belum ada konser tersimpan di database GigsSTRACK.")
                return

            list_text = "📋 <b>DAFTAR KONSER TERBARU DI GigsSTRACK:</b>\n\n"
            inline_keyboard = []
            for g in recent_Gigss:
                list_text += f"• <b>[ID: {g.id}]</b> {g.title} @ {g.venue.name} ({g.start_datetime.strftime('%d %b %Y')})\n"
                inline_keyboard.append([
                    {"text": f"🗑️ Hapus ID {g.id} ({g.title[:15]}...)", "callback_data": f"delGigs:{g.id}"}
                ])
            
            self.send_message(chat_id, list_text, reply_markup={"inline_keyboard": inline_keyboard})
            return

        # Command /delete <id>
        if text.startswith("/delete"):
            parts = text.split()
            if len(parts) > 1 and parts[1].isdigit():
                Gigs_id = int(parts[1])
                deleted, _ = Gigs.objects.filter(id=Gigs_id).delete()
                if deleted:
                    self.send_message(chat_id, f"✅ Konser <b>ID {Gigs_id}</b> berhasil dihapus dari GigsSTRACK.")
                else:
                    self.send_message(chat_id, f"❌ Konser <b>ID {Gigs_id}</b> tidak ditemukan.")
            else:
                self.send_message(chat_id, "⚠️ Format salah. Gunakan: <code>/delete 123</code>")
            return

        # Handle Photo (Single or Multi-Photo Album)
        if "photo" in message:
            best_photo = message["photo"][-1]
            file_id = best_photo["file_id"]
            self.queue_incoming_photo(chat_id, file_id)
            return

        # Handle Document (uncompressed image)
        if "document" in message and message["document"].get("mime_type", "").startswith("image/"):
            file_id = message["document"]["file_id"]
            self.queue_incoming_photo(chat_id, file_id)
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
                "📸 Silakan kirimkan <b>foto poster konser</b> (atau beberapa foto sekaligus) untuk memulai scan,\n"
                "atau ketik <code>/list</code> untuk melihat konser yang sudah tersimpan."
            )

    def queue_incoming_photo(self, chat_id: int, file_id: str):
        """
        Buffer photos for 0.5 seconds to group multiple photos (carousel album)
        into a single unified AI analysis request.
        """
        self.send_chat_action(chat_id, "upload_photo")
        with self.buffer_lock:
            if chat_id not in self.photo_buffers:
                self.photo_buffers[chat_id] = []
            
            self.photo_buffers[chat_id].append(file_id)

            # Cancel existing timer if any
            if chat_id in self.buffer_timers:
                self.buffer_timers[chat_id].cancel()

            # Debounce timer 0.5s to capture all photos in the album
            t = threading.Timer(0.5, self.flush_photo_buffer, args=[chat_id])
            self.buffer_timers[chat_id] = t
            t.start()

    def flush_photo_buffer(self, chat_id: int):
        with self.buffer_lock:
            file_ids = self.photo_buffers.pop(chat_id, [])
            self.buffer_timers.pop(chat_id, None)

        if not file_ids:
            return

        photo_count = len(file_ids)
        if photo_count > 1:
            msg_text = f"🔍 <b>Menganalisis {photo_count} foto poster sekaligus dengan Gemini Vision AI...</b>\n<i>Foto pertama ditetapkan sebagai cover utama. Mohon tunggu...</i>"
        else:
            msg_text = "🔍 <b>Menganalisis poster dengan Gemini Vision AI...</b>\n<i>Mohon tunggu sebentar...</i>"

        wait_msg = self.send_message(chat_id, msg_text)
        wait_msg_id = wait_msg.get("result", {}).get("message_id")

        try:
            downloaded_images = []
            for fid in file_ids:
                b_data, f_name = self.download_file_bytes(fid)
                downloaded_images.append((b_data, f_name))

            # Cover Photo is STRICTLY the FIRST image sent
            primary_photo_bytes, primary_file_name = downloaded_images[0]

            # Send all downloaded images to Gemini Vision
            ai_service = PosterAIService()
            raw_img_list = [img[0] for img in downloaded_images]
            extracted = ai_service.analyze_poster(images_list=raw_img_list)

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
                "photo_bytes": primary_photo_bytes,
                "file_name": primary_file_name,
                "chat_id": chat_id,
                "photo_count": photo_count
            }
            # Lock active session to this new unified scan
            self.active_chat_sessions[chat_id] = session_id

            review_text = self.format_review_card(extracted, is_corrected=False, photo_count=photo_count)

            inline_keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ Simpan ke GigsSTRACK", "callback_data": f"save:{session_id}"},
                        {"text": "❌ Batal", "callback_data": f"cancel:{session_id}"}
                    ]
                ]
            }

            if wait_msg_id:
                self.edit_message(chat_id, wait_msg_id, review_text, reply_markup=inline_keyboard)
            else:
                self.send_message(chat_id, review_text, reply_markup=inline_keyboard)

        except Exception as e:
            logger.error(f"Error processing buffered poster on Telegram: {e}")
            err_msg = "⚠️ <b>Terjadi kendala saat memproses gambar.</b> Silakan coba kirim ulang fotonya."
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

            review_text = self.format_review_card(updated_data, is_corrected=True, photo_count=scan_item.get("photo_count", 1))

            inline_keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ Simpan ke GigsSTRACK", "callback_data": f"save:{session_id}"},
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
                self.edit_message(chat_id, wait_msg_id, "⚠️ <i>Gagal menerapkan koreksi. Silakan ketik dengan format sederhana, contoh: <code>ubah tiket jadi di BBO</code></i>")

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

        # Handle Delete Gigs from list
        if action == "delGigs":
            if payload.isdigit():
                Gigs_id = int(payload)
                Gigs.objects.filter(id=Gigs_id).delete()
                self.answer_callback_query(cq_id, f"Konser ID {Gigs_id} dihapus!", show_alert=True)
                self.edit_message(chat_id, message_id, f"🗑️ <b>Konser ID {Gigs_id} telah dihapus dari GigsSTRACK.</b>")
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
            if self.active_chat_sessions.get(chat_id) == session_id:
                self.active_chat_sessions.pop(chat_id, None)
            self.edit_message(chat_id, message_id, "❌ <b>Proses dibatalkan.</b> Poster tidak disimpan.")
            return

        if action == "save":
            self.answer_callback_query(cq_id, "Menyimpan ke database...")
            try:
                ai_service = PosterAIService()
                poster_file = ContentFile(scan_item["photo_bytes"], name=scan_item["file_name"])
                gig_saved = ai_service.save_Gigs_to_database(scan_item["data"], poster_file=poster_file)
                
                self.pending_scans.pop(session_id, None)
                if self.active_chat_sessions.get(chat_id) == session_id:
                    self.active_chat_sessions.pop(chat_id, None)

                success_text = (
                    "🎉 <b>BERHASIL DITAMBAHKAN KE GigsSTRACK!</b>\n\n"
                    f"🎸 <b>Acara:</b> {html.escape(gig_saved.title)}\n"
                    f"📍 <b>Venue:</b> {html.escape(gig_saved.venue.name)} ({html.escape(gig_saved.venue.city)})\n"
                    f"📅 <b>Jadwal:</b> {gig_saved.start_datetime.strftime('%d %B %Y')}\n"
                    f"👥 <b>Total Lineup:</b> {gig_saved.lineups.count()} Band\n"
                    f"🎟️ <b>HTM:</b> {html.escape(gig_saved.price_range_display)}\n\n"
                    f"🌐 <i>Konser sekarang sudah aktif dan tayang di website GigsSTRACK!</i>\n"
                    f"🔗 <b>Lihat di Website:</b> http://localhost:5173\n"
                    f"💡 <i>Ketik <code>/list</code> untuk melihat atau mengelola daftar konser.</i>"
                )
                self.edit_message(chat_id, message_id, success_text)

            except Exception as e:
                logger.error(f"Error saving Gigs from Telegram callback: {e}")
                err_str = str(e).lower()
                if "duplicate" in err_str or "unique" in err_str or "integrityerror" in err_str:
                    msg = "ℹ️ <b>Konser sudah ada di database.</b> Data berhasil disinkronkan dengan pembaruan terbaru!"
                else:
                    msg = "⚠️ <b>Terjadi kendala saat menyimpan.</b> Silakan coba klik tombol <b>✅ Simpan ke GigsSTRACK</b> sekali lagi."
                self.edit_message(chat_id, message_id, msg)

    def run_polling(self):
        logger.info("Memulai polling Telegram Bot...")
        offset = None

        me = self.send_request("getMe")
        if me.get("ok"):
            bot_info = me["result"]
            print(f"[OK] Telegram Bot Aktif: @{bot_info.get('username')} ({bot_info.get('first_name')})")
            print("[*] Fitur Multi-Foto Album Carousel & Koreksi Teks Aktif!")
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
