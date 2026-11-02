"""
GigsSTRACK Admin API Views
Full CRUD REST API endpoints for the custom admin panel.
All views require IsAdminUser (is_staff=True) permission.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone

from apps.gigs.models import Gigs, Gig, GigsLineup, GigLineup, GigsTicketTier, GigTicketTier, GigsStatus, GigStatus
from apps.artists.models import Artist, Genre
from apps.venues.models import Venue
from .admin_serializers import (
    GigsAdminSerializer, VenueAdminSerializer,
    ArtistAdminSerializer, GenreAdminSerializer,
    LineupAdminSerializer, TicketTierAdminSerializer,
)


# ─── Dashboard Stats ──────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    """Statistik ringkas untuk dashboard admin."""
    today = timezone.localdate()
    total_Gigss = Gigs.objects.count()
    today_Gigss = Gigs.objects.filter(start_datetime__date=today).count()
    upcoming_Gigss = Gigs.objects.filter(start_datetime__date__gte=today, status='scheduled').count()
    featured_Gigss = Gigs.objects.filter(is_featured=True).count()
    total_artists = Artist.objects.count()
    active_artists = Artist.objects.filter(is_active=True).count()
    total_venues = Venue.objects.count()
    total_genres = Genre.objects.count()
    total_users = User.objects.count()
    staff_users = User.objects.filter(is_staff=True).count()

    # Status breakdown
    status_breakdown = {}
    for s in GigsStatus.values:
        status_breakdown[s] = Gigs.objects.filter(status=s).count()

    # Recent Gigss (last 5)
    recent_Gigss = Gigs.objects.select_related('venue').order_by('-created_at')[:5]
    recent_Gigss_data = [
        {
            'id': g.id,
            'title': g.title,
            'venue': g.venue.name,
            'city': g.venue.city,
            'start_datetime': g.start_datetime.strftime('%d %b %Y %H:%M'),
            'status': g.status,
            'is_featured': g.is_featured,
            'poster': g.display_poster,
        }
        for g in recent_Gigss
    ]

    return Response({
        'Gigss': {
            'total': total_Gigss,
            'today': today_Gigss,
            'upcoming': upcoming_Gigss,
            'featured': featured_Gigss,
            'status_breakdown': status_breakdown,
        },
        'artists': {
            'total': total_artists,
            'active': active_artists,
        },
        'venues': {
            'total': total_venues,
        },
        'genres': {
            'total': total_genres,
        },
        'users': {
            'total': total_users,
            'staff': staff_users,
        },
        'recent_Gigss': recent_Gigss_data,
    })


# ─── Gigs Admin ViewSet ────────────────────────────────────────────────────────

class AdminGigsViewSet(viewsets.ModelViewSet):
    queryset = Gigs.objects.select_related('venue').prefetch_related('lineups__artist__genres', 'ticket_tiers').order_by('-start_datetime')
    serializer_class = GigsAdminSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'venue__name', 'venue__city', 'lineups__artist__name']
    ordering_fields = ['start_datetime', 'created_at', 'title', 'status']

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        city_param = self.request.query_params.get('city')
        featured_param = self.request.query_params.get('featured')
        if status_param:
            qs = qs.filter(status=status_param)
        if city_param:
            qs = qs.filter(venue__city__iexact=city_param)
        if featured_param in ['true', '1']:
            qs = qs.filter(is_featured=True)
        return qs

    @action(detail=True, methods=['post'], url_path='add-lineup')
    def add_lineup(self, request, pk=None):
        Gigs = self.get_object()
        serializer = LineupAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(Gigs=Gigs)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='remove-lineup/(?P<lineup_id>[^/.]+)')
    def remove_lineup(self, request, pk=None, lineup_id=None):
        try:
            lineup = GigsLineup.objects.get(pk=lineup_id, Gigs_id=pk)
            lineup.delete()
            return Response({'message': 'Lineup berhasil dihapus.'})
        except GigsLineup.DoesNotExist:
            return Response({'error': 'Lineup tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='add-tier')
    def add_tier(self, request, pk=None):
        Gigs = self.get_object()
        serializer = TicketTierAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(Gigs=Gigs)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='remove-tier/(?P<tier_id>[^/.]+)')
    def remove_tier(self, request, pk=None, tier_id=None):
        try:
            tier = GigsTicketTier.objects.get(pk=tier_id, Gigs_id=pk)
            tier.delete()
            return Response({'message': 'Tier tiket berhasil dihapus.'})
        except GigsTicketTier.DoesNotExist:
            return Response({'error': 'Tier tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)


# ─── Artist Admin ViewSet ─────────────────────────────────────────────────────

class AdminArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.prefetch_related('genres').order_by('name')
    serializer_class = ArtistAdminSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'bio', 'hometown']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        active_param = self.request.query_params.get('active')
        genre_param = self.request.query_params.get('genre')
        if active_param in ['true', '1']:
            qs = qs.filter(is_active=True)
        elif active_param in ['false', '0']:
            qs = qs.filter(is_active=False)
        if genre_param:
            qs = qs.filter(genres__slug__iexact=genre_param)
        return qs


# ─── Genre Admin ViewSet ──────────────────────────────────────────────────────

class AdminGenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.annotate(artists_count=Count('artists')).order_by('name')
    serializer_class = GenreAdminSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


# ─── Venue Admin ViewSet ──────────────────────────────────────────────────────

class AdminVenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.order_by('city', 'name')
    serializer_class = VenueAdminSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address', 'city']
    ordering_fields = ['name', 'city', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        city_param = self.request.query_params.get('city')
        active_param = self.request.query_params.get('active')
        if city_param:
            qs = qs.filter(city__iexact=city_param)
        if active_param in ['true', '1']:
            qs = qs.filter(is_active=True)
        elif active_param in ['false', '0']:
            qs = qs.filter(is_active=False)
        return qs
