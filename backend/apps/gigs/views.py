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

        # Filter by specific date (YYYY-MM-DD), or default to today onwards (sembunyikan konser kemarin)
        date_param = params.get('date')
        include_past = params.get('include_past', 'false').lower() in ['true', '1']
        if date_param:
            try:
                parsed_date = timezone.datetime.strptime(date_param, '%Y-%m-%d').date()
                qs = qs.filter(start_datetime__date=parsed_date)
            except ValueError:
                pass
        elif not include_past:
            # Otomatis sembunyikan konser yang sudah lewat kemarin
            local_today = timezone.localdate()
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
        """Daftar kota yang memiliki venue aktif."""
        cities = Venue.objects.filter(is_active=True).values_list('city', flat=True).distinct()
        return Response(sorted(list(set(cities))))

    @action(detail=False, methods=['get'])
    def summary_stats(self, request):
        """Statistik ringkas untuk dashboard radar."""
        today_date = timezone.localdate()
        active_gigs = Gig.objects.exclude(status=GigStatus.CANCELLED)
        
        # Hitung artis dan venue yang benar-benar memiliki jadwal gig aktif
        total_artists = Artist.objects.filter(
            is_active=True,
            gig_appearances__gig__in=active_gigs
        ).distinct().count()

        total_venues = Venue.objects.filter(
            is_active=True,
            gigs__in=active_gigs
        ).distinct().count()

        return Response({
            'gigs_today': active_gigs.filter(start_datetime__date=today_date).count(),
            'total_artists': total_artists,
            'total_venues': total_venues,
            'total_upcoming': active_gigs.filter(start_datetime__date__gte=today_date).count(),
        })

    @action(detail=False, methods=['post', 'get'])
    def sync_live(self, request):
        """Endpoint untuk memicu sinkronisasi jadwal gig secara otomatis."""
        from django.core.management import call_command
        import io
        out = io.StringIO()
        call_command('sync_live_gigs', stdout=out)
        return Response({
            'status': 'success',
            'message': 'Sinkronisasi gig live berhasil dijalankan.',
            'log': out.getvalue()
        })

    @action(detail=False, methods=['post'], url_path='sync-bandsintown')
    def sync_bandsintown(self, request):
        """
        Endpoint untuk menyinkronkan jadwal konser dari Bandsintown API.
        Body JSON:
        {
            "artist": "Reality Club",  # Opsional jika sync_all=True
            "all": false,              # Jika True, sync semua artis di DB
            "app_id": "YOUR_KEY",      # Opsional
            "use_mock": false          # Opsional
        }
        """
        from apps.gigs.services.bandsintown import BandsintownService
        artist = request.data.get('artist')
        sync_all = request.data.get('all', False)
        app_id = request.data.get('app_id')
        use_mock = request.data.get('use_mock', False)

        if not artist and not sync_all:
            return Response(
                {"error": "Wajib menyertakan parameter 'artist' (nama band) atau 'all': true."},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = BandsintownService(app_id=app_id)
        results = []

        if artist:
            res = service.sync_artist_events(artist.strip(), app_id=app_id, use_mock=use_mock)
            results.append(res)
        elif sync_all:
            db_artists = list(Artist.objects.values_list('name', flat=True))
            for name in db_artists:
                res = service.sync_artist_events(name, app_id=app_id, use_mock=use_mock)
                results.append(res)

        return Response({
            "status": "success",
            "total_artists_synced": len(results),
            "results": results
        })

    @action(detail=False, methods=['post'], url_path='import-real-event')
    def import_real_event(self, request):
        """
        Endpoint untuk memasukkan pengumuman konser nyata (teks caption IG atau trigger sinkronisasi).
        Body JSON:
        {
            "text": "Pestapora 2026 di Gambir Expo Kemayoran..."
        }
        atau tanpa text untuk sinkronisasi konser resmi Jabodetabek.
        """
        from apps.gigs.services.real_events import RealEventService
        service = RealEventService()
        raw_text = request.data.get('text')

        if raw_text:
            result = service.parse_text_announcement(raw_text)
            return Response({"status": "success", "event": result})

        synced = service.sync_verified_concerts()
        return Response({
            "status": "success",
            "message": f"Berhasil menyinkronkan {len(synced)} konser nyata Jabodetabek.",
            "events": synced
        })

    @action(detail=False, methods=['post'], url_path='sync-verified')
    def sync_verified(self, request):
        """
        Endpoint untuk menyinkronkan konser musik nyata terverifikasi
        dan opsi membersihkan data dummy lama.
        Body JSON:
        {
            "clean_dummy": true  # Opsional, default false
        }
        """
        from apps.gigs.services.real_concert_scraper import RealConcertScraperService
        clean_dummy = request.data.get('clean_dummy', False)
        service = RealConcertScraperService()
        result = service.sync_all_verified(clean_dummy=clean_dummy)
        return Response(result)

    @action(detail=False, methods=['post'], url_path='sync-ticketmaster')
    def sync_ticketmaster(self, request):
        """
        Endpoint untuk menyinkronkan event konser musik resmi dari Ticketmaster Discovery API.
        Body JSON (seluruh parameter opsional):
        {
            "keyword": "Arctic Monkeys",
            "city": "Jakarta",
            "country_code": "ID",
            "size": 20,
            "api_key": "YOUR_API_KEY",
            "use_mock": false
        }
        """
        from apps.gigs.services.ticketmaster import TicketmasterService

        keyword = request.data.get('keyword')
        city = request.data.get('city', 'Jakarta')
        country_code = request.data.get('country_code', 'ID')
        size = request.data.get('size', 20)
        api_key = request.data.get('api_key')
        use_mock = request.data.get('use_mock', False)

        service = TicketmasterService(api_key=api_key)
        res = service.sync(
            keyword=keyword,
            city=city,
            country_code=country_code,
            size=size,
            use_mock=use_mock
        )

        if not res.get("success"):
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='scan-poster')
    def scan_poster(self, request):
        """
        Endpoint untuk scan & ekstrak informasi konser musik dari foto poster (Instagram flyer).
        Terima multipart/form-data dengan key 'image'.
        Opsi: 'auto_save=true' untuk langsung simpan ke database.
        """
        from apps.gigs.services.poster_ai import PosterAIService

        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"success": False, "error": "Wajib mengunggah file gambar poster dengan key 'image'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image_bytes = image_file.read()
            mime_type = image_file.content_type or 'image/jpeg'
            auto_save = request.data.get('auto_save', 'false').lower() in ['true', '1']

            service = PosterAIService()
            extracted = service.analyze_poster(image_bytes=image_bytes, mime_type=mime_type)

            if not extracted.get("success"):
                return Response(extracted, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            if auto_save:
                image_file.seek(0)
                gig = service.save_gig_to_database(extracted, poster_file=image_file)
                serializer = GigDetailSerializer(gig, context={'request': request})
                return Response({
                    "success": True,
                    "saved": True,
                    "message": f"Konser '{gig.title}' berhasil diekstrak dan disimpan!",
                    "gig": serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response({
                "success": True,
                "saved": False,
                "message": "Poster berhasil diekstrak oleh AI. Silakan periksa dan konfirmasi data.",
                "data": extracted
            }, status=status.HTTP_200_OK)

        except ValueError as ve:
            return Response({"success": False, "error": str(ve)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"success": False, "error": f"Gagal memproses poster: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='confirm-poster-gig')
    def confirm_poster_gig(self, request):
        """
        Endpoint untuk menyimpan data konser hasil review/edit user ke database.
        Mendukung multipart/form-data (dengan image opsional) atau JSON payload.
        """
        from apps.gigs.services.poster_ai import PosterAIService

        image_file = request.FILES.get('image')
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        # Parse artists & genres if sent as JSON string in form-data
        import json
        if isinstance(data.get('artists'), str):
            try:
                data['artists'] = json.loads(data['artists'])
            except Exception:
                data['artists'] = [a.strip() for a in data['artists'].split(',') if a.strip()]
        if isinstance(data.get('genres'), str):
            try:
                data['genres'] = json.loads(data['genres'])
            except Exception:
                data['genres'] = [g.strip() for g in data['genres'].split(',') if g.strip()]

        try:
            service = PosterAIService()
            normalized = service.normalize_extracted_data(data)
            gig = service.save_gig_to_database(normalized, poster_file=image_file)
            serializer = GigDetailSerializer(gig, context={'request': request})

            return Response({
                "success": True,
                "saved": True,
                "message": f"Konser '{gig.title}' berhasil disimpan ke database!",
                "gig": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "success": False,
                "error": f"Gagal menyimpan gig: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


