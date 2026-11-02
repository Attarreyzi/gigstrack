from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GigsViewSet

router = DefaultRouter()
router.register(r'', GigsViewSet, basename='Gigs')

urlpatterns = [
    path('', include(router.urls)),
]
