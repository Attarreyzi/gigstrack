from rest_framework import serializers
from .models import Venue

class VenueSerializer(serializers.ModelSerializer):
    display_image = serializers.ReadOnlyField()
    maps_url = serializers.CharField(source='resolved_maps_url', read_only=True)

    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'slug', 'address', 'city', 'province',
            'maps_url', 'capacity', 'instagram_url', 'image', 'image_url',
            'display_image', 'is_active'
        ]
