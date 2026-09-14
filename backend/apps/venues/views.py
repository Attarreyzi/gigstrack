from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Venue
from .serializers import VenueSerializer

class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.filter(is_active=True)
    serializer_class = VenueSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'province']
    search_fields = ['name', 'address', 'city']
    ordering_fields = ['name', 'city', 'capacity']
    ordering = ['city', 'name']
