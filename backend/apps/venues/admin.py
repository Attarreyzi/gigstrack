from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Venue

@admin.register(Venue)
class VenueAdmin(ModelAdmin):
    list_display = ('thumbnail_preview', 'name', 'city', 'province', 'capacity_display', 'is_active', 'created_at', 'edit_action')
    list_display_links = ('name', 'edit_action')
    list_filter = ('city', 'province', 'is_active')
    search_fields = ('name', 'address', 'city')
    prepopulated_fields = {'slug': ('name',)}
    list_filter_submit = True

    @display(description="Aksi")
    def edit_action(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk])
        return format_html(
            '<a href="{}" style="display: inline-flex; align-items: center; gap: 5px; padding: 4px 12px; background: rgba(0, 240, 255, 0.15); border: 1px solid rgba(0, 240, 255, 0.4); color: #00F0FF; border-radius: 6px; font-weight: 700; text-decoration: none; font-size: 12px;">'
            '✏️ Edit'
            '</a>',
            url
        )

    @display(description="Foto Venue")
    def thumbnail_preview(self, obj):
        return format_html(
            '<img src="{}" style="width: 46px; height: 46px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.3);" />',
            obj.display_image
        )

    @display(description="Kapasitas")
    def capacity_display(self, obj):
        if obj.capacity:
            return f"{obj.capacity:,} penonton".replace(',', '.')
        return "-"

