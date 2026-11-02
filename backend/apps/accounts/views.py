import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.gigs.models import Gigs
from apps.gigs.serializers import GigsListSerializer
from .models import UserProfile, SavedGig
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login endpoint - returns JWT token + user info."""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.filter(username=request.data.get('username')).first()
            if user:
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.last_active = timezone.now()
                profile.save(update_fields=['last_active'])
        return response


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Endpoint registrasi user baru."""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        refresh = RefreshToken.for_user(user)
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'auth_provider': 'email'})
        return Response({
            'message': f'Akun "{user.username}" berhasil dibuat!',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'auth_provider': profile.auth_provider,
                'referral_code': profile.referral_code,
                'saved_gigs_count': 0,
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    """
    Login / Sign-up instan menggunakan akun Google.
    Menerima email, nama, google_id, dan opsional avatar_url.
    """
    credential = request.data.get('credential', '').strip()
    email = request.data.get('email', '').strip().lower()
    name = request.data.get('name', '').strip()
    google_id = request.data.get('google_id', '').strip()
    avatar_url = request.data.get('avatar_url', '').strip()

    # Jika dikirim token credential JWT resmi dari Google Identity Services (GIS)
    if credential and not email:
        try:
            import base64
            parts = credential.split('.')
            if len(parts) >= 2:
                payload_segment = parts[1]
                padded = payload_segment + '=' * (-len(payload_segment) % 4)
                token_data = json.loads(base64.urlsafe_b64decode(padded).decode('utf-8'))
                email = token_data.get('email', '').strip().lower()
                name = token_data.get('name', '') or name
                avatar_url = token_data.get('picture', '') or avatar_url
                google_id = token_data.get('sub', '') or google_id
        except Exception as e:
            logger.warning(f"Gagal decode Google JWT credential: {e}")

    if not email:
        # Fallback generated email if simulated
        email_base = name.lower().replace(' ', '') if name else f"user_{uuid.uuid4().hex[:6]}"
        email = f"{email_base}@gmail.com"

    user = User.objects.filter(email=email).first()
    if not user:
        # Tentukan username unik
        base_username = email.split('@')[0].replace('.', '_')
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        name_parts = name.split(' ', 1) if name else ['Google', 'User']
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_unusable_password()

    # Perbarui data profile & last_login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.auth_provider = 'google'
    if avatar_url:
        profile.avatar_url = avatar_url
    profile.last_active = timezone.now()
    profile.save()

    refresh = RefreshToken.for_user(user)
    return Response({
        'message': f'Selamat datang kembali, {user.first_name or user.username}!',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'auth_provider': 'google',
            'referral_code': profile.referral_code,
            'avatar_url': profile.avatar_url,
            'saved_gigs_count': user.saved_gigs.count(),
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def guest_login(request):
    """
    Masuk instan sebagai Tamu (Guest Mode).
    Membuat sesi sementara tanpa registrasi rumit.
    """
    guest_uuid = uuid.uuid4().hex[:8]
    guest_username = f"guest_{guest_uuid}"
    
    user = User.objects.create_user(
        username=guest_username,
        first_name="Tamu",
        last_name=f"#{guest_uuid[:4].upper()}",
        email=f"{guest_username}@guest.gigtrack.id"
    )
    user.set_unusable_password()
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    profile = UserProfile.objects.create(
        user=user,
        auth_provider='guest',
        last_active=timezone.now()
    )

    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'Masuk sebagai Tamu GigTrack.',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': False,
            'is_superuser': False,
            'auth_provider': 'guest',
            'referral_code': profile.referral_code,
            'saved_gigs_count': 0,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Endpoint untuk melihat dan update profil user sendiri."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.last_active = timezone.now()
    profile.save(update_fields=['last_active'])

    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def saved_gigs_view(request):
    """
    Fitur 'Disimpan' (Bookmark) untuk user yang login.
    GET: Mengambil daftar konser yang disimpan oleh user.
    POST: Menyimpan atau menghapus (toggle) konser dari daftar simpanan user.
    """
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.last_active = timezone.now()
    profile.save(update_fields=['last_active'])

    if request.method == 'GET':
        saved_items = SavedGig.objects.filter(user=user).select_related('gig', 'gig__venue')
        gig_ids = list(saved_items.values_list('gig_id', flat=True))
        gigs = [item.gig for item in saved_items if item.gig]
        serializer = GigsListSerializer(gigs, many=True, context={'request': request})
        return Response({
            'saved_ids': gig_ids,
            'total_saved': len(gig_ids),
            'results': serializer.data
        })

    gig_id = request.data.get('gig_id')
    if not gig_id:
        return Response({'error': 'gig_id wajib disertakan.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        gig = Gigs.objects.get(pk=gig_id)
    except Gigs.DoesNotExist:
        return Response({'error': 'Konser tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

    existing = SavedGig.objects.filter(user=user, gig=gig).first()
    if existing:
        existing.delete()
        is_saved = False
        message = f'"{gig.title}" dihapus dari konser tersimpan.'
    else:
        SavedGig.objects.create(user=user, gig=gig)
        is_saved = True
        message = f'"{gig.title}" berhasil disimpan!'

    all_saved_ids = list(SavedGig.objects.filter(user=user).values_list('gig_id', flat=True))
    return Response({
        'is_saved': is_saved,
        'gig_id': gig.id,
        'total_saved': len(all_saved_ids),
        'saved_ids': all_saved_ids,
        'message': message
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Blacklist refresh token untuk logout."""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception:
        pass
    return Response({'message': 'Logout berhasil.'}, status=status.HTTP_200_OK)


# ─── Admin User Management ────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_list_users(request):
    """List semua user beserta status login & konser tersimpan - untuk admin/staff."""
    users = User.objects.all().order_by('-date_joined')
    serializer = UserProfileSerializer(users, many=True)
    return Response({
        'count': users.count(),
        'results': serializer.data
    })


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_manage_user(request, user_id):
    """Edit atau hapus user - hanya untuk superuser."""
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User tidak ditemukan.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        if user == request.user:
            return Response({'error': 'Tidak bisa menghapus akun sendiri.'}, status=status.HTTP_400_BAD_REQUEST)
        username = user.username
        user.delete()
        return Response({'message': f'User "{username}" berhasil dihapus.'})

    if 'is_staff' in request.data and request.user.is_superuser:
        user.is_staff = request.data['is_staff']
    if 'is_active' in request.data:
        user.is_active = request.data['is_active']
    if 'first_name' in request.data:
        user.first_name = request.data['first_name']
    if 'last_name' in request.data:
        user.last_name = request.data['last_name']
    user.save()
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)
