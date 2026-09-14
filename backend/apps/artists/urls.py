from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, ArtistViewSet

router = DefaultRouter()
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'', ArtistViewSet, basename='artist')

urlpatterns = [
    path('', include(router.urls)),
]
