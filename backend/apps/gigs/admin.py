from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Gigs, GigsLineup, GigsTicketTier, GigsTicketLink

class GigsLineupInline(TabularInline):
    model = GigsLineup
    extra = 1
    autocomplete_fields = ['artist']
    fields = ('order', 'artist', 'day', 'set_time', 'is_headliner')
    ordering = ('order',)


@admin.register(GigsLineup)
class GigsLineupAdmin(ModelAdmin):
    list_display = ('Gigs', 'artist', 'day', 'set_time', 'is_headliner', 'order')
    list_filter = ('day', 'is_headliner', 'Gigs')
    search_fields = ('artist__name', 'Gigs__title', 'day')
    autocomplete_fields = ['artist']
    ordering = ('Gigs', 'order')


class GigsTicketTierInline(TabularInline):
    model = GigsTicketTier
    extra = 0
    fields = ('order', 'tier_name', 'price', 'is_sold_out', 'description', 'ticket_url')
    ordering = ('order', 'price')


class GigsTicketLinkInline(TabularInline):
    model = GigsTicketLink
    extra = 1
    fields = ('order', 'platform_name', 'url')
    ordering = ('order',)


@admin.register(Gigs)
class GigsAdmin(ModelAdmin):
    list_display = (
        'poster_preview', 'title', 'venue', 'start_datetime',
        'doors_open', 'price_display', 'status_badge', 'is_featured', 'edit_action'
    )
    list_display_links = ('title', 'edit_action')
    list_filter = ('status', 'venue__city', 'is_featured', 'start_datetime', 'is_free')
    search_fields = ('title', 'venue__name', 'venue__city', 'lineups__artist__name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GigsTicketLinkInline, GigsLineupInline, GigsTicketTierInline]
    date_hierarchy = 'start_datetime'
    list_filter_submit = True

    fieldsets = (
        ("Informasi Acara", {
            "fields": (
                "title", "slug", "venue",
                ("start_datetime", "end_datetime"),
                ("doors_open", "status"),
                "is_featured",
            ),
        }),
        ("Pengaturan Harga & Tiket", {
            "fields": (
                ("is_free", "ticket_price"),
                "ticket_url",
            ),
            "description": "Jika acara berbayar namun nominal di poster tidak tertera, biarkan 'Gratis' tidak dicentang dan isi 'Link Pembelian Tiket'.",
        }),
        ("Media & Deskripsi", {
            "fields": (
                "poster", "poster_url", "description",
            ),
        }),
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

    @display(description="Poster")
    def poster_preview(self, obj):
        return format_html(
            '<img src="{}" style="width: 44px; height: 56px; object-fit: cover; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.3);" />',
            obj.display_poster
        )

    @display(description="Harga Tiket")
    def price_display(self, obj):
        if obj.is_free:
            return format_html('<span style="color: #00E676; font-weight: 700; background: rgba(0,230,118,0.15); padding: 3px 8px; border-radius: 6px;">GRATIS</span>')
        if obj.ticket_price and obj.ticket_price > 0:
            return f"Rp {obj.ticket_price:,.0f}".replace(',', '.')
        return format_html('<span style="color: #FFB300; font-weight: 600; background: rgba(255,179,0,0.15); padding: 3px 8px; border-radius: 6px;">Berbayar / Cek Tiket</span>')

    @display(
        description="Status",
        label={
            "scheduled": "info",
            "live_now": "danger",
            "completed": "success",
            "postponed": "warning",
            "cancelled": "danger",
        }
    )
    def status_badge(self, obj):
        return obj.status
