"""
URL configuration for GigTrack project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/artists/', include('apps.artists.urls')),
    path('api/venues/', include('apps.venues.urls')),
    path('api/gigs/', include('apps.gigs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "GigTrack Admin Dashboard"
admin.site.site_title = "GigTrack Portal"
admin.site.index_title = "Manajemen Konser, Artis, dan Venue"
