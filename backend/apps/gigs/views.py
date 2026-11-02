from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count
from .models import Gig, GigStatus
from .serializers import GigListSerializer, GigDetailSerializer
from apps.venues.models import Venue
from apps.artists.models import Artist, Genre

JABODETABEK_CITIES = ['Jakarta', 'Bogor', 'Depok', 'Tangerang', 'Bekasi', 'Tangerang Selatan']

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

        # Hanya tampilkan wilayah Jabodetabek
        qs = qs.filter(venue__city__in=JABODETABEK_CITIES)

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

        # Filter tanggal cerdas
        date_param = params.get('date')
        include_past = params.get('include_past', 'false').lower() in ['true', '1']
        local_today = timezone.localdate()

        if date_param:
            d_lower = date_param.lower().strip()
            if d_lower == 'today':
                qs = qs.filter(start_datetime__date=local_today)
            elif d_lower == 'tomorrow':
                tomorrow = local_today + timezone.timedelta(days=1)
                qs = qs.filter(start_datetime__date=tomorrow)
            elif d_lower == 'this_week':
                days_to_sunday = 6 - local_today.weekday()
                end_of_week = local_today + timezone.timedelta(days=days_to_sunday)
                qs = qs.filter(start_datetime__date__gte=local_today, start_datetime__date__lte=end_of_week)
            elif d_lower == 'weekend':
                # Akhir pekan (Jumat, Sabtu, Minggu) mendatang
                # Di Django ORM: week_day 1=Minggu, 6=Jumat, 7=Sabtu
                qs = qs.filter(
                    start_datetime__date__gte=local_today,
                    start_datetime__week_day__in=[1, 6, 7]
                )
            else:
                try:
                    parsed_date = timezone.datetime.strptime(date_param, '%Y-%m-%d').date()
                    qs = qs.filter(start_datetime__date=parsed_date)
                except ValueError:
                    pass
        elif not include_past:
            # Sembunyikan konser yang sudah lewat kemarin
            qs = qs.filter(start_datetime__date__gte=local_today)

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

        day_names = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
        }
        month_names = {
            'January': 'Januari', 'February': 'Februari', 'March': 'Maret', 'April': 'April',
            'May': 'Mei', 'June': 'Juni', 'July': 'Juli', 'August': 'Agustus',
            'September': 'September', 'October': 'Oktober', 'November': 'November', 'December': 'Desember'
        }
        eng_day = today_date.strftime('%A')
        eng_month = today_date.strftime('%B')
        date_display = f"{day_names.get(eng_day, eng_day)}, {today_date.strftime('%d')} {month_names.get(eng_month, eng_month)} {today_date.strftime('%Y')}"

        serializer = GigListSerializer(today_gigs, many=True, context={'request': request})
        return Response({
            'date': today_date.strftime('%Y-%m-%d'),
            'date_display': date_display,
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
        """Daftar kota Jabodetabek."""
        return Response(['Jakarta', 'Bogor', 'Depok', 'Tangerang', 'Bekasi'])

    @action(detail=False, methods=['get'])
    def summary_stats(self, request):
        """Statistik ringkas untuk dashboard radar."""
        today_date = timezone.localdate()
        active_gigs = Gig.objects.filter(venue__city__in=JABODETABEK_CITIES).exclude(status=GigStatus.CANCELLED)

        total_artists = Artist.objects.filter(is_active=True).count()
        total_venues = Venue.objects.filter(is_active=True, city__in=JABODETABEK_CITIES).count()

        return Response({
            'gigs_today': active_gigs.filter(start_datetime__date=today_date).count(),
            'total_artists': total_artists,
            'total_venues': total_venues,
            'total_upcoming': active_gigs.filter(start_datetime__date__gte=today_date).count(),
        })

# Alias for backward-compatibility if router expects GigsViewSet
GigsViewSet = GigViewSet
