from django.contrib import admin
from django.utils.html import format_html
from .models import Gig, GigLineup, GigTicketTier

class GigLineupInline(admin.TabularInline):
    model = GigLineup
    extra = 2
    autocomplete_fields = ['artist']
    fields = ('order', 'artist', 'set_time', 'is_headliner')
    ordering = ('order',)


class GigTicketTierInline(admin.TabularInline):
    model = GigTicketTier
    extra = 1
    fields = ('order', 'tier_name', 'price', 'is_sold_out', 'description', 'ticket_url')
    ordering = ('order', 'price')


@admin.register(Gig)
class GigAdmin(admin.ModelAdmin):
    list_display = (
        'poster_preview', 'title', 'venue', 'start_datetime',
        'doors_open', 'price_display', 'status_badge', 'is_featured', 'today_badge'
    )
    list_filter = ('status', 'venue__city', 'is_featured', 'start_datetime')
    search_fields = ('title', 'venue__name', 'venue__city', 'lineups__artist__name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GigLineupInline, GigTicketTierInline]
    date_hierarchy = 'start_datetime'


    def poster_preview(self, obj):
        return format_html(
            '<img src="{}" style="width: 50px; height: 65px; object-fit: cover; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);" />',
            obj.display_poster
        )
    poster_preview.short_description = "Poster"

    def price_display(self, obj):
        if obj.is_free or obj.ticket_price == 0:
            return format_html('<span style="color: #00E676; font-weight: bold;">FREE</span>')
        return f"Rp {obj.ticket_price:,.0f}".replace(',', '.')
    price_display.short_description = "Harga Tiket"

    def status_badge(self, obj):
        colors = {
            'scheduled': '#2196F3',
            'live_now': '#FF1744',
            'completed': '#9E9E9E',
            'postponed': '#FF9100',
            'cancelled': '#D50000',
        }
        color = colors.get(obj.status, '#757575')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px; text-transform: uppercase;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def today_badge(self, obj):
        if obj.is_happening_today:
            return format_html('<span style="background: #FF0055; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px;">🔥 HARI INI</span>')
        return "-"
    today_badge.short_description = "Live Hari Ini"
