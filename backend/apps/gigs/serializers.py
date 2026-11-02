from rest_framework import serializers
from .models import Gigs, GigsLineup, GigsTicketTier, GigsTicketLink
from apps.venues.serializers import VenueSerializer
from apps.artists.serializers import ArtistSerializer

class GigsTicketLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = GigsTicketLink
        fields = ['id', 'platform_name', 'url', 'order']


class GigsTicketTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = GigsTicketTier
        fields = ['id', 'tier_name', 'price', 'is_sold_out', 'description', 'ticket_url', 'order']


class GigsLineupSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=GigsLineup.artist.field.related_model.objects.all(),
        source='artist',
        write_only=True
    )

    class Meta:
        model = GigsLineup
        fields = ['id', 'artist', 'artist_id', 'day', 'set_time', 'is_headliner', 'order']


class GigsListSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    venue_city = serializers.CharField(source='venue.city', read_only=True)
    ticket_url = serializers.CharField(source='resolved_ticket_url', read_only=True)
    display_poster = serializers.SerializerMethodField()
    is_happening_today = serializers.ReadOnlyField()
    price_range_display = serializers.ReadOnlyField()
    ticket_tiers = GigsTicketTierSerializer(many=True, read_only=True)
    referral_code = serializers.SerializerMethodField()
    artists = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()

    class Meta:
        model = Gigs
        fields = [
            'id', 'title', 'slug', 'venue_name', 'venue_city',
            'start_datetime', 'doors_open', 'ticket_price', 'is_free',
            'price_range_display', 'ticket_tiers', 'referral_code',
            'ticket_url', 'status', 'is_featured', 'display_poster', 'is_happening_today',
            'artists', 'genres'
        ]

    def get_referral_code(self, obj):
        return obj.referral_code or ""

    def get_display_poster(self, obj):
        url = obj.display_poster
        if not url:
            return "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80"
        if url.startswith('/media/'):
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(url)
            return f"http://localhost:8000{url}"
        return url

    def get_artists(self, obj):
        return [
            {
                'id': lineup.artist.id,
                'name': lineup.artist.name,
                'is_headliner': lineup.is_headliner,
                'image': lineup.artist.display_image
            }
            for lineup in obj.lineups.select_related('artist').order_by('order', 'id')
        ]

    def get_genres(self, obj):
        genres_set = set()
        genre_list = []
        for lineup in obj.lineups.prefetch_related('artist__genres').all():
            for genre in lineup.artist.genres.all():
                if genre.name not in genres_set:
                    genres_set.add(genre.name)
                    genre_list.append({
                        'id': genre.id,
                        'name': genre.name,
                        'color': genre.color
                    })
        return genre_list


class GigsDetailSerializer(serializers.ModelSerializer):
    venue = VenueSerializer(read_only=True)
    lineups = serializers.SerializerMethodField()
    ticket_tiers = GigsTicketTierSerializer(many=True, read_only=True)
    ticket_links = GigsTicketLinkSerializer(many=True, read_only=True)
    display_poster = serializers.SerializerMethodField()
    is_happening_today = serializers.ReadOnlyField()
    price_range_display = serializers.ReadOnlyField()
    price_full_range_display = serializers.ReadOnlyField()
    referral_code = serializers.SerializerMethodField()
    ticket_url = serializers.CharField(source='resolved_ticket_url', read_only=True)
    genres = serializers.SerializerMethodField()

    class Meta:
        model = Gigs
        fields = [
            'id', 'title', 'slug', 'venue', 'start_datetime', 'end_datetime',
            'doors_open', 'description', 'poster', 'poster_url', 'display_poster',
            'ticket_price', 'is_free', 'price_range_display', 'price_full_range_display', 'ticket_tiers',
            'ticket_links', 'ticket_url', 'referral_code', 'status', 'is_featured',
            'is_happening_today', 'lineups', 'genres', 'created_at'
        ]

    def get_referral_code(self, obj):
        return obj.referral_code or ""

    def get_display_poster(self, obj):
        url = obj.display_poster
        if not url:
            return "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&auto=format&fit=crop&q=80"
        if url.startswith('/media/'):
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(url)
            return f"http://localhost:8000{url}"
        return url

    def get_genres(self, obj):
        genres_set = set()
        genre_list = []
        for lineup in obj.lineups.prefetch_related('artist__genres').all():
            for genre in lineup.artist.genres.all():
                if genre.name not in genres_set:
                    genres_set.add(genre.name)
                    genre_list.append({
                        'id': genre.id,
                        'name': genre.name,
                        'color': genre.color
                    })
        return genre_list

    def get_lineups(self, obj):
        ordered_lineups = obj.lineups.select_related('artist').order_by('order', 'id')
        return GigsLineupSerializer(ordered_lineups, many=True, context=self.context).data


# Aliases for compatibility
GigTicketLinkSerializer = GigsTicketLinkSerializer
GigTicketTierSerializer = GigsTicketTierSerializer
GigLineupSerializer = GigsLineupSerializer
GigListSerializer = GigsListSerializer
GigDetailSerializer = GigsDetailSerializer

