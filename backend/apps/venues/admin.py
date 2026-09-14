from django.contrib import admin
from django.utils.html import format_html
from .models import Venue

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'name', 'city', 'province', 'capacity', 'is_active', 'created_at')
    list_filter = ('city', 'province', 'is_active')
    search_fields = ('name', 'address', 'city')
    prepopulated_fields = {'slug': ('name',)}

    def thumbnail_preview(self, obj):
        return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 6px;" />', obj.display_image)
    thumbnail_preview.short_description = "Foto"
