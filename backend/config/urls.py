"""
URL configuration for GigsSTRACK project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from apps.accounts.admin_views import (
    AdminGigsViewSet, AdminArtistViewSet,
    AdminGenreViewSet, AdminVenueViewSet,
    admin_dashboard_stats,
)

# Admin API Router
admin_router = DefaultRouter()
admin_router.register(r'Gigss', AdminGigsViewSet, basename='admin-Gigss')
admin_router.register(r'artists', AdminArtistViewSet, basename='admin-artists')
admin_router.register(r'genres', AdminGenreViewSet, basename='admin-genres')
admin_router.register(r'venues', AdminVenueViewSet, basename='admin-venues')

urlpatterns = [
    # Convenient redirects so localhost:8000/ and localhost:8000/login go straight to admin
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    re_path(r'^login/?$', RedirectView.as_view(url='/admin/login/', permanent=False)),
    path('admin/', admin.site.urls),

    # Public API
    path('api/artists/', include('apps.artists.urls')),
    path('api/venues/', include('apps.venues.urls')),
    path('api/gigs/', include('apps.gigs.urls')),
    path('api/Gigss/', include('apps.gigs.urls')),

    # Auth endpoints
    path('api/auth/', include('apps.accounts.urls')),

    # Admin panel API (requires is_staff=True)
    path('api/admin-panel/stats/', admin_dashboard_stats, name='admin-stats'),
    path('api/admin-panel/', include(admin_router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "GigsSTRACK Admin Dashboard"
admin.site.site_title = "GigsSTRACK Portal"
admin.site.index_title = "Manajemen Konser, Artis, dan Venue"
