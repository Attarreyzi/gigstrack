from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Genre, Artist
from .serializers import GenreSerializer, ArtistSerializer

class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = None  # Return all genres for easy filtering buttons


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.filter(is_active=True).prefetch_related('genres')
    serializer_class = ArtistSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'bio', 'hometown', 'genres__name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
