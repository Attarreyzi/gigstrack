from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count
from .models import Gig, GigStatus
from .serializers import GigListSerializer, GigDetailSerializer
from apps.venues.models import Venue
from apps.artists.models import Artist, Genre

class GigViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'title', 'description', 'venue__name', 'venue__city',
        'lineups__artist__name', 'lineups__artist__genres__name'
    ]
    ordering_fields = ['start_datetime', 'ticket_price', 'created_at']
    ordering = ['start_datetime']

    def get_queryset(self):
        qs = Gig.objects.select_related('venue').prefetch_related('lineups__artist__genres')
        params = self.request.query_params

        # Filter by search keyword
        search_param = params.get('search')
        if search_param:
            search_param = search_param.strip()
            qs = qs.filter(
                Q(title__icontains=search_param) |
                Q(description__icontains=search_param) |
                Q(venue__name__icontains=search_param) |
                Q(venue__city__icontains=search_param) |
                Q(lineups__artist__name__icontains=search_param) |
                Q(lineups__artist__genres__name__icontains=search_param)
            )

        # Filter by specific date (YYYY-MM-DD)
        date_param = params.get('date')
        if date_param:
            try:
                parsed_date = timezone.datetime.strptime(date_param, '%Y-%m-%d').date()
                qs = qs.filter(start_datetime__date=parsed_date)
            except ValueError:
                pass

        # Filter by city
        city_param = params.get('city')
        if city_param:
            qs = qs.filter(venue__city__iexact=city_param)

        # Filter by genre (slug or name)
        genre_param = params.get('genre')
        if genre_param:
            qs = qs.filter(
                Q(lineups__artist__genres__slug__iexact=genre_param) |
                Q(lineups__artist__genres__name__iexact=genre_param)
            )

        # Filter by artist (id or name)
        artist_param = params.get('artist')
        if artist_param:
            if artist_param.isdigit():
                qs = qs.filter(lineups__artist__id=int(artist_param))
            else:
                qs = qs.filter(lineups__artist__name__icontains=artist_param)

        # Filter by venue id
        venue_param = params.get('venue')
        if venue_param and venue_param.isdigit():
            qs = qs.filter(venue__id=int(venue_param))

        # Filter by is_free
        free_param = params.get('is_free')
        if free_param is not None:
            if free_param.lower() in ['true', '1']:
                qs = qs.filter(is_free=True)
            elif free_param.lower() in ['false', '0']:
                qs = qs.filter(is_free=False)

        # Filter by status
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)

        return qs.distinct()

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return GigDetailSerializer
        return GigListSerializer

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Endpoint khusus untuk mendeteksi semua gig yang main HARI INI."""
        today_date = timezone.localdate()
        today_gigs = self.get_queryset().filter(
            start_datetime__date=today_date
        ).exclude(status=GigStatus.CANCELLED).order_by('start_datetime')

        serializer = GigListSerializer(today_gigs, many=True, context={'request': request})
        return Response({
            'date': today_date.strftime('%Y-%m-%d'),
            'date_display': today_date.strftime('%A, %d %B %Y'),
            'total_gigs_today': today_gigs.count(),
            'gigs': serializer.data
        })

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Endpoint untuk konser mendatang (mulai besok dan seterusnya)."""
        tomorrow_date = timezone.localdate() + timezone.timedelta(days=1)
        upcoming_gigs = self.get_queryset().filter(
            start_datetime__date__gte=tomorrow_date
        ).exclude(status=GigStatus.CANCELLED).order_by('start_datetime')

        serializer = GigListSerializer(upcoming_gigs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def cities(self, request):
        """Daftar kota yang memiliki venue aktif."""
        cities = Venue.objects.filter(is_active=True).values_list('city', flat=True).distinct()
        return Response(sorted(list(set(cities))))

    @action(detail=False, methods=['get'])
    def summary_stats(self, request):
        """Statistik ringkas untuk dashboard radar."""
        today_date = timezone.localdate()
        return Response({
            'gigs_today': Gig.objects.filter(start_datetime__date=today_date).exclude(status=GigStatus.CANCELLED).count(),
            'total_artists': Artist.objects.filter(is_active=True).count(),
            'total_venues': Venue.objects.filter(is_active=True).count(),
            'total_upcoming': Gig.objects.filter(start_datetime__date__gt=today_date).exclude(status=GigStatus.CANCELLED).count(),
        })
