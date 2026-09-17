from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from apps.venues.models import Venue
from apps.artists.models import Artist, Genre

class GigStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Dijadwalkan'
    LIVE_NOW = 'live_now', 'Sedang Berlangsung'
    COMPLETED = 'completed', 'Selesai'
    POSTPONED = 'postponed', 'Ditunda'
    CANCELLED = 'cancelled', 'Dibatalkan'

class Gig(models.Model):
    title = models.CharField(max_length=250, verbose_name="Nama Acara / Gig")
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="gigs", verbose_name="Lokasi / Venue")
    start_datetime = models.DateTimeField(db_index=True, verbose_name="Waktu Mulai Acara")
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name="Waktu Selesai (Opsional)")
    doors_open = models.CharField(max_length=50, blank=True, default="18:30 WIB", verbose_name="Open Gate / Doors Open")
    description = models.TextField(blank=True, verbose_name="Deskripsi Acara")
    poster = models.ImageField(upload_to="posters/", blank=True, null=True, verbose_name="Upload Poster")
    poster_url = models.URLField(blank=True, null=True, verbose_name="URL Poster (Fallback)")
    ticket_price = models.IntegerField(default=0, verbose_name="Harga Tiket (Rp)")
    is_free = models.BooleanField(default=False, verbose_name="Gratis / Free Entry")
    ticket_url = models.URLField(blank=True, verbose_name="Link Pembelian Tiket / RSVP")
    status = models.CharField(max_length=20, choices=GigStatus.choices, default=GigStatus.SCHEDULED, db_index=True, verbose_name="Status Acara")
    is_featured = models.BooleanField(default=False, verbose_name="Tampilkan di Banner Utama (Featured)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_datetime']
        verbose_name = "Gig / Acara Musik"
        verbose_name_plural = "Daftar Gig / Acara Musik"

    def save(self, *args, **kwargs):
        if not self.slug:
            dt_str = 'event'
            if self.start_datetime:
                if hasattr(self.start_datetime, 'strftime'):
                    dt_str = self.start_datetime.strftime('%Y%m%d')
                else:
                    dt_str = str(self.start_datetime)[:10].replace('-', '')
            base_slug = slugify(f"{self.title}-{dt_str}") or "gig-event"
            slug = base_slug
            counter = 1
            while Gig.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.ticket_price == 0 and not self.ticket_tiers.exists():
            self.is_free = True
        super().save(*args, **kwargs)


    @property
    def display_poster(self):
        if self.poster:
            return self.poster.url
        return self.poster_url or "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80"

    @property
    def is_happening_today(self):
        local_today = timezone.localdate()
        gig_date = timezone.localtime(self.start_datetime).date()
        return gig_date == local_today

    @property
    def resolved_ticket_url(self):
        """
        Mengembalikan URL tiket yang valid dan anti-404.
        Jika URL berupa tebakan slug loket/tiket/goers yang rawan 404,
        otomatis dialihkan ke halaman pencarian resmi platform terkait
        menggunakan nama headliner band / event agar user langsung diarahkan
        ke tiket pembelian resmi tanpa pernah menemui error 404 Not Found.
        """
        import urllib.parse
        import re

        # Acara gratis murni tanpa tautan registrasi tiket tidak memerlukan tautan
        if self.is_free and not self.ticket_url:
            return ""

        # Dapatkan kata kunci pencarian paling akurat
        search_term = ""
        lower_title = self.title.lower() if self.title else ""
        if "pestapora" in lower_title:
            search_term = "Pestapora"
        elif "synchronize" in lower_title:
            return "https://synchronizefestival.com/tickets"
        elif "joyland" in lower_title:
            search_term = "Joyland Festival"
        else:
            try:
                headliner = self.lineups.filter(is_headliner=True).select_related('artist').first()
                if headliner and headliner.artist:
                    search_term = headliner.artist.name
                elif self.lineups.exists():
                    first_artist = self.lineups.select_related('artist').first()
                    if first_artist and first_artist.artist:
                        search_term = first_artist.artist.name
            except Exception:
                pass

            if not search_term:
                base = re.split(r'\b(live|at|in|feat|special)\b', self.title, flags=re.IGNORECASE)[0]
                base = base.split(':')[0].split('(')[0].strip()
                search_term = base if len(base) > 2 else (self.title or "Konser")

        q = urllib.parse.quote(search_term.strip())
        u = (self.ticket_url or "").strip()

        # Jika sudah berupa halaman pencarian resmi atau link festival resmi aktif
        if "loket.com/search" in u or "tiket.com/to-do/search" in u or "goersapp.com/search" in u or "synchronizefestival.com" in u:
            return u

        # Cegah link slug fiktif yang pasti 404 di loket/tiket/goers/megatix
        if "goersapp.com" in u:
            return f"https://goersapp.com/search?keyword={q}"
        elif "tiket.com" in u:
            return f"https://www.tiket.com/to-do/search?q={q}"
        elif "loket.com" in u or "megatix" in u or not u:
            return f"https://www.loket.com/search?q={q}"

        return u

    @property
    def price_range_display(self):
        tiers = self.ticket_tiers.all()
        if tiers.exists():
            prices = [t.price for t in tiers if t.price > 0]
            if not prices:
                return "GRATIS / Free Entry"
            min_p = min(prices)
            max_p = max(prices)
            if min_p == max_p:
                return f"Rp {min_p:,.0f}".replace(',', '.')
            return f"Mulai Rp {min_p:,.0f}".replace(',', '.')
        if self.is_free or self.ticket_price == 0:
            return "GRATIS / Free Entry"
        return f"Rp {self.ticket_price:,.0f}".replace(',', '.')

    @property
    def price_full_range_display(self):
        tiers = self.ticket_tiers.all()
        if tiers.exists():
            prices = [t.price for t in tiers if t.price > 0]
            if not prices:
                return "GRATIS / Free Entry"
            min_p = min(prices)
            max_p = max(prices)
            if min_p == max_p:
                return f"Rp {min_p:,.0f}".replace(',', '.')
            return f"Rp {min_p:,.0f} - Rp {max_p:,.0f}".replace(',', '.')
        if self.is_free or self.ticket_price == 0:
            return "GRATIS / Free Entry"
        return f"Rp {self.ticket_price:,.0f}".replace(',', '.')

    def __str__(self):
        return f"{self.title} @ {self.venue.name} ({self.start_datetime.strftime('%d %b %Y')})"


class GigLineup(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name="lineups")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="gig_appearances")
    set_time = models.CharField(max_length=100, blank=True, help_text="Contoh: 19:30 - 20:15 WIB", verbose_name="Jadwal Tampil")
    is_headliner = models.BooleanField(default=False, verbose_name="Headliner")
    order = models.PositiveIntegerField(default=1, verbose_name="Urutan Tampil")

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('gig', 'artist')
        verbose_name = "Line-up Band"
        verbose_name_plural = "Line-up Band"

    def __str__(self):
        return f"{self.artist.name} ({self.gig.title})"


class GigTicketTier(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name="ticket_tiers", verbose_name="Konser / Acara")
    tier_name = models.CharField(max_length=150, verbose_name="Nama Kategori / Tier Tiket")
    price = models.IntegerField(default=0, verbose_name="Harga Tiket (Rp)")
    is_sold_out = models.BooleanField(default=False, verbose_name="Habis / Sold Out")
    description = models.CharField(max_length=250, blank=True, verbose_name="Keterangan (contoh: 3-Day Pass / Daily Pass)")
    ticket_url = models.URLField(blank=True, verbose_name="Link Tiket Khusus Tier Ini (Opsional)")
    order = models.PositiveIntegerField(default=1, verbose_name="Urutan")

    class Meta:
        ordering = ['order', 'price', 'id']
        verbose_name = "Kategori / Tier Tiket"
        verbose_name_plural = "Daftar Kategori / Tier Tiket"

    def __str__(self):
        status = " [SOLD OUT]" if self.is_sold_out else ""
        return f"{self.tier_name} - Rp {self.price:,}{status}"

