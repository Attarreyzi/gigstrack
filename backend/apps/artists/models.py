from django.db import models
from django.utils.text import slugify

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nama Genre")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    color = models.CharField(max_length=20, default="#FF3366", help_text="Hex color code untuk badge UI (misal: #FF3366)", verbose_name="Warna Badge")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Genre"
        verbose_name_plural = "Daftar Genre"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "genre"
            slug = base_slug
            counter = 1
            while Genre.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nama Artis / Band")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name="artists", blank=True, verbose_name="Genre Musik")
    bio = models.TextField(blank=True, verbose_name="Biografi Singkat")
    image = models.ImageField(upload_to="artists/", blank=True, null=True, verbose_name="Upload Foto Band")
    image_url = models.URLField(blank=True, null=True, help_text="URL gambar eksternal (fallback jika tidak upload)", verbose_name="URL Foto")
    hometown = models.CharField(max_length=150, blank=True, verbose_name="Kota Asal")
    instagram_url = models.URLField(blank=True, verbose_name="Link Instagram")
    spotify_url = models.URLField(blank=True, verbose_name="Link Spotify")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Artis / Band"
        verbose_name_plural = "Daftar Artis / Band"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "artist"
            slug = base_slug
            counter = 1
            while Artist.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url or "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=600&auto=format&fit=crop&q=80"

    def __str__(self):
        return self.name
