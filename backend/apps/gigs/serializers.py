from rest_framework import serializers
from .models import Gig, GigLineup, GigTicketTier
from apps.venues.serializers import VenueSerializer
from apps.artists.serializers import ArtistSerializer

class GigTicketTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = GigTicketTier
        fields = ['id', 'tier_name', 'price', 'is_sold_out', 'description', 'ticket_url', 'order']


class GigLineupSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=GigLineup.artist.field.related_model.objects.all(),
        source='artist',
        write_only=True
    )

    class Meta:
        model = GigLineup
        fields = ['id', 'artist', 'artist_id', 'set_time', 'is_headliner', 'order']


class GigListSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    venue_city = serializers.CharField(source='venue.city', read_only=True)
    ticket_url = serializers.CharField(source='resolved_ticket_url', read_only=True)
    display_poster = serializers.ReadOnlyField()
    is_happening_today = serializers.ReadOnlyField()
    price_range_display = serializers.ReadOnlyField()
    ticket_tiers = GigTicketTierSerializer(many=True, read_only=True)
    artists = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()

    class Meta:
        model = Gig
        fields = [
            'id', 'title', 'slug', 'venue_name', 'venue_city',
            'start_datetime', 'doors_open', 'ticket_price', 'is_free',
            'price_range_display', 'ticket_tiers',
            'ticket_url', 'status', 'is_featured', 'display_poster', 'is_happening_today',
            'artists', 'genres'
        ]

    def get_artists(self, obj):
        return [
            {
                'id': lineup.artist.id,
                'name': lineup.artist.name,
                'is_headliner': lineup.is_headliner,
                'image': lineup.artist.display_image
            }
            for lineup in obj.lineups.select_related('artist').all()
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


class GigDetailSerializer(serializers.ModelSerializer):
    venue = VenueSerializer(read_only=True)
    lineups = GigLineupSerializer(many=True, read_only=True)
    ticket_tiers = GigTicketTierSerializer(many=True, read_only=True)
    display_poster = serializers.ReadOnlyField()
    is_happening_today = serializers.ReadOnlyField()
    price_range_display = serializers.ReadOnlyField()
    ticket_url = serializers.CharField(source='resolved_ticket_url', read_only=True)
    genres = serializers.SerializerMethodField()

    class Meta:
        model = Gig
        fields = [
            'id', 'title', 'slug', 'venue', 'start_datetime', 'end_datetime',
            'doors_open', 'description', 'poster', 'poster_url', 'display_poster',
            'ticket_price', 'is_free', 'price_range_display', 'ticket_tiers',
            'ticket_url', 'status', 'is_featured',
            'is_happening_today', 'lineups', 'genres', 'created_at'
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

