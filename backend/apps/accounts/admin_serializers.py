"""
GigsSTRACK Admin API Serializers
Full CRUD serializers for admin panel use.
"""
from rest_framework import serializers
from apps.gigs.models import Gigs, GigsLineup, GigsTicketTier
from apps.artists.models import Artist, Genre
from apps.venues.models import Venue


# ─── Venue Serializers ─────────────────────────────────────────────────────────

class VenueAdminSerializer(serializers.ModelSerializer):
    display_image = serializers.ReadOnlyField()
    Gigss_count = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = '__all__'

    def get_Gigss_count(self, obj):
        return obj.Gigss.count()


# ─── Artist & Genre Serializers ────────────────────────────────────────────────

class GenreAdminSerializer(serializers.ModelSerializer):
    artists_count = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = '__all__'

    def get_artists_count(self, obj):
        return obj.artists.count()


class ArtistAdminSerializer(serializers.ModelSerializer):
    display_image = serializers.ReadOnlyField()
    genres_detail = GenreAdminSerializer(source='genres', many=True, read_only=True)
    Gigs_count = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = '__all__'

    def get_Gigs_count(self, obj):
        return obj.Gigs_appearances.count()


# ─── Gigs Serializers ──────────────────────────────────────────────────────────

class LineupAdminSerializer(serializers.ModelSerializer):
    artist_name = serializers.ReadOnlyField(source='artist.name')

    class Meta:
        model = GigsLineup
        fields = ('id', 'artist', 'artist_name', 'day', 'set_time', 'is_headliner', 'order')


class TicketTierAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = GigsTicketTier
        fields = '__all__'


class GigsAdminSerializer(serializers.ModelSerializer):
    venue_name = serializers.ReadOnlyField(source='venue.name')
    venue_city = serializers.ReadOnlyField(source='venue.city')
    display_poster = serializers.ReadOnlyField()
    price_range_display = serializers.ReadOnlyField()
    is_happening_today = serializers.ReadOnlyField()
    lineups = LineupAdminSerializer(many=True, read_only=True)
    ticket_tiers = TicketTierAdminSerializer(many=True, read_only=True)

    class Meta:
        model = Gigs
        fields = '__all__'
