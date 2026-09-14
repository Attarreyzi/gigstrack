from django.contrib import admin
from django.utils.html import format_html
from .models import Genre, Artist

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_badge', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def color_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 10px; border-radius: 4px; font-weight: bold;">{}</span>',
            obj.color, obj.color
        )
    color_badge.short_description = "Color Preview"


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'name', 'hometown', 'get_genres', 'is_active', 'created_at')
    list_filter = ('is_active', 'genres', 'hometown')
    search_fields = ('name', 'bio', 'hometown')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('genres',)

    def get_genres(self, obj):
        return ", ".join([g.name for g in obj.genres.all()])
    get_genres.short_description = "Genres"

    def thumbnail_preview(self, obj):
        return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 50%;" />', obj.display_image)
    thumbnail_preview.short_description = "Foto"
