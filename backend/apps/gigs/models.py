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
            self.slug = slugify(f"{self.title}-{self.start_datetime.strftime('%Y%m%d') if self.start_datetime else 'event'}")
        if self.ticket_price == 0:
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
