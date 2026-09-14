from rest_framework import serializers
from .models import Genre, Artist

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug', 'color']


class ArtistSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Genre.objects.all(), source='genres', write_only=True, required=False
    )
    display_image = serializers.ReadOnlyField()

    class Meta:
        model = Artist
        fields = [
            'id', 'name', 'slug', 'genres', 'genre_ids',
            'bio', 'image', 'image_url', 'display_image',
            'hometown', 'instagram_url', 'spotify_url', 'is_active'
        ]
