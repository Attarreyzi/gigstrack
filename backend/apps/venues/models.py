from django.db import models
from django.utils.text import slugify

class Venue(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nama Venue / Tempat")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    address = models.TextField(verbose_name="Alamat Lengkap")
    city = models.CharField(max_length=100, default="Jakarta", db_index=True, verbose_name="Kota")
    province = models.CharField(max_length=100, blank=True, default="DKI Jakarta", verbose_name="Provinsi")
    maps_url = models.URLField(blank=True, verbose_name="Link Google Maps")
    capacity = models.PositiveIntegerField(null=True, blank=True, verbose_name="Kapasitas Penonton")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram Venue")
    image = models.ImageField(upload_to="venues/", blank=True, null=True, verbose_name="Upload Foto Venue")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL Foto Venue")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['city', 'name']
        verbose_name = "Venue"
        verbose_name_plural = "Daftar Venue"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "venue"
            slug = base_slug
            counter = 1
            while Venue.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600&auto=format&fit=crop&q=80"

    def __str__(self):
        return f"{self.name} ({self.city})"
