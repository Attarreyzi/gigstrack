from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Genre, Artist

@admin.register(Genre)
class GenreAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'color_badge', 'created_at', 'edit_action')
    list_display_links = ('name', 'edit_action')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    @display(description="Warna Label")
    def color_badge(self, obj):
        return format_html(
            '<div style="display: inline-flex; align-items: center; gap: 8px;">'
            '<span style="width: 14px; height: 14px; border-radius: 50%; background-color: {}; box-shadow: 0 0 8px {};"></span>'
            '<span style="font-weight: 600; color: {}; font-family: monospace;">{}</span>'
            '</div>',
            obj.color, obj.color, obj.color, obj.color
        )

    @display(description="Aksi")
    def edit_action(self, obj):
        url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change', args=[obj.pk])
        return format_html(
            '<a href="{}" style="display: inline-flex; align-items: center; gap: 5px; padding: 4px 12px; background: rgba(0, 240, 255, 0.15); border: 1px solid rgba(0, 240, 255, 0.4); color: #00F0FF; border-radius: 6px; font-weight: 700; text-decoration: none; font-size: 12px;">'
            '✏️ Edit'
            '</a>',
            url
        )


@admin.register(Artist)
class ArtistAdmin(ModelAdmin):
    list_display = ('thumbnail_preview', 'name', 'hometown', 'get_genres', 'is_active', 'created_at', 'edit_action')
    list_display_links = ('name', 'edit_action')
    list_filter = ('is_active', 'genres', 'hometown')
    search_fields = ('name', 'bio', 'hometown')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('genres',)
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

    @display(description="Foto Profil")
    def thumbnail_preview(self, obj):
        return format_html(
            '<img src="{}" style="width: 44px; height: 44px; object-fit: cover; border-radius: 50%; box-shadow: 0 2px 6px rgba(0,0,0,0.3);" />',
            obj.display_image
        )

    @display(description="Genre")
    def get_genres(self, obj):
        chips = [
            f'<span style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); padding: 2px 8px; border-radius: 9999px; font-size: 11px; margin-right: 4px;">{g.name}</span>'
            for g in obj.genres.all()
        ]
        return format_html("".join(chips)) if chips else "-"

