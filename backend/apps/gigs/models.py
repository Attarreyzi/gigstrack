from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from apps.venues.models import Venue
from apps.artists.models import Artist, Genre

class GigsStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Dijadwalkan'
    LIVE_NOW = 'live_now', 'Sedang Berlangsung'
    COMPLETED = 'completed', 'Selesai'
    POSTPONED = 'postponed', 'Ditunda'
    CANCELLED = 'cancelled', 'Dibatalkan'

class Gigs(models.Model):
    title = models.CharField(max_length=250, verbose_name="Nama Acara / Gigs")
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="Gigss", verbose_name="Lokasi / Venue")
    start_datetime = models.DateTimeField(db_index=True, verbose_name="Waktu Mulai Acara")
    end_datetime = models.DateTimeField(null=True, blank=True, verbose_name="Waktu Selesai (Opsional)")
    doors_open = models.CharField(max_length=50, blank=True, default="18:30 WIB", verbose_name="Open Gate / Doors Open")
    description = models.TextField(blank=True, verbose_name="Deskripsi Acara")
    poster = models.ImageField(upload_to="posters/", blank=True, null=True, verbose_name="Upload Poster")
    poster_url = models.URLField(blank=True, null=True, verbose_name="URL Poster (Fallback)")
    ticket_price = models.IntegerField(default=0, verbose_name="Harga Tiket (Rp)")
    is_free = models.BooleanField(default=False, verbose_name="Gratis / Free Entry")
    ticket_url = models.URLField(blank=True, verbose_name="Link Pembelian Tiket / RSVP")
    referral_code = models.CharField(max_length=50, blank=True, default="", verbose_name="Kode Referral / Promo")
    status = models.CharField(max_length=20, choices=GigsStatus.choices, default=GigsStatus.SCHEDULED, db_index=True, verbose_name="Status Acara")
    is_featured = models.BooleanField(default=False, verbose_name="Tampilkan di Banner Utama (Featured)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gigs_gig'
        ordering = ['start_datetime']
        verbose_name = "Gigs / Acara Musik"
        verbose_name_plural = "Daftar Gigs / Acara Musik"

    def save(self, *args, **kwargs):
        if not self.slug:
            dt_str = 'event'
            if self.start_datetime:
                if hasattr(self.start_datetime, 'strftime'):
                    dt_str = self.start_datetime.strftime('%Y%m%d')
                else:
                    dt_str = str(self.start_datetime)[:10].replace('-', '')
            base_slug = slugify(f"{self.title}-{dt_str}") or "Gigs-event"
            slug = base_slug
            counter = 1
            while Gigs.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)


    @property
    def display_poster(self):
        if self.poster:
            return self.poster.url
        return self.poster_url or "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80"

    @property
    def is_happening_today(self):
        local_today = timezone.localdate()
        Gigs_date = timezone.localtime(self.start_datetime).date()
        return Gigs_date == local_today

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
        if self.is_free:
            return "GRATIS / Free Entry"
        tiers = self.ticket_tiers.all()
        if tiers.exists():
            prices = [t.price for t in tiers if t.price > 0]
            if prices:
                min_p = min(prices)
                return f"Mulai Rp {min_p:,.0f}".replace(',', '.')
        if self.ticket_price > 0:
            return f"Mulai Rp {self.ticket_price:,.0f}".replace(',', '.')
        return "Cek Platform Tiket"

    @property
    def price_full_range_display(self):
        if self.is_free:
            return "GRATIS / Free Entry"
        tiers = self.ticket_tiers.all()
        if tiers.exists():
            prices = [t.price for t in tiers if t.price > 0]
            if prices:
                min_p = min(prices)
                max_p = max(prices)
                if min_p == max_p:
                    return f"Rp {min_p:,.0f}".replace(',', '.')
                return f"Rp {min_p:,.0f} - Rp {max_p:,.0f}".replace(',', '.')
        if self.ticket_price > 0:
            return f"Rp {self.ticket_price:,.0f}".replace(',', '.')
        return "Berbayar (Cek Info Tiket)"


    def __str__(self):
        return f"{self.title} @ {self.venue.name} ({self.start_datetime.strftime('%d %b %Y')})"


class GigsLineup(models.Model):
    Gigs = models.ForeignKey(Gigs, on_delete=models.CASCADE, related_name="lineups", db_column="gig_id")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="Gigs_appearances")
    day = models.CharField(max_length=60, blank=True, default="", help_text="Hari / Day festival (contoh: Day 1, Day 2, Day 3)", verbose_name="Hari / Day")
    set_time = models.CharField(max_length=100, blank=True, help_text="Contoh: 19:30 - 20:15 WIB", verbose_name="Jadwal Tampil")
    is_headliner = models.BooleanField(default=False, verbose_name="Headliner")
    order = models.PositiveIntegerField(default=1, verbose_name="Urutan Tampil")

    @property
    def gig(self):
        return self.Gigs

    @gig.setter
    def gig(self, val):
        self.Gigs = val

    class Meta:
        db_table = 'gigs_giglineup'
        ordering = ['order', 'id']
        unique_together = ('Gigs', 'artist')
        verbose_name = "Line-up Band"
        verbose_name_plural = "Line-up Band"

    def __str__(self):
        return f"{self.artist.name} ({self.Gigs.title})"


class GigsTicketTier(models.Model):
    Gigs = models.ForeignKey(Gigs, on_delete=models.CASCADE, related_name="ticket_tiers", db_column="gig_id", verbose_name="Konser / Acara")
    tier_name = models.CharField(max_length=150, verbose_name="Nama Kategori / Tier Tiket")
    price = models.IntegerField(default=0, verbose_name="Harga Tiket (Rp)")
    is_sold_out = models.BooleanField(default=False, verbose_name="Habis / Sold Out")
    description = models.CharField(max_length=250, blank=True, verbose_name="Keterangan (contoh: 3-Day Pass / Daily Pass)")
    ticket_url = models.URLField(blank=True, verbose_name="Link Tiket Khusus Tier Ini (Opsional)")
    order = models.PositiveIntegerField(default=1, verbose_name="Urutan")

    @property
    def gig(self):
        return self.Gigs

    @gig.setter
    def gig(self, val):
        self.Gigs = val

    class Meta:
        db_table = 'gigs_gigtickettier'
        ordering = ['order', 'price', 'id']
        verbose_name = "Kategori / Tier Tiket"
        verbose_name_plural = "Daftar Kategori / Tier Tiket"

    def __str__(self):
        status = " [SOLD OUT]" if self.is_sold_out else ""
        return f"{self.tier_name} - Rp {self.price:,}{status}"


class GigsTicketLink(models.Model):
    Gigs = models.ForeignKey(Gigs, on_delete=models.CASCADE, related_name="ticket_links", db_column="gig_id", verbose_name="Konser / Acara")
    platform_name = models.CharField(max_length=100, verbose_name="Nama Platform", help_text="Contoh: Goers, Loket.com, Tiket.com, TipTip, Artatix")
    url = models.URLField(max_length=500, verbose_name="URL Pembelian Tiket")
    order = models.PositiveIntegerField(default=1, verbose_name="Urutan")

    @property
    def gig(self):
        return self.Gigs

    @gig.setter
    def gig(self, val):
        self.Gigs = val

    class Meta:
        db_table = 'gigs_gigticketlink'
        ordering = ['order', 'id']
        verbose_name = "Tautan Platform Tiket"
        verbose_name_plural = "Daftar Tautan Platform Tiket"

    def __str__(self):
        return f"{self.platform_name}: {self.url}"

# Aliases for compatibility
Gig = Gigs
GigStatus = GigsStatus
GigLineup = GigsLineup
GigTicketTier = GigsTicketTier
GigTicketLink = GigsTicketLink

