from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Auth endpoints
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.register_user, name='register'),
    path('google/', views.google_login, name='google_login'),
    path('guest/', views.guest_login, name='guest_login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('saved-gigs/', views.saved_gigs_view, name='saved_gigs'),

    # Admin user management
    path('admin/users/', views.admin_list_users, name='admin_list_users'),
    path('admin/users/<int:user_id>/', views.admin_manage_user, name='admin_manage_user'),
]
