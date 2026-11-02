from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile, SavedGig


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer yang menyertakan info user di response."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'auth_provider': profile.auth_provider,
            'referral_code': profile.referral_code,
            'saved_gigs_count': user.saved_gigs.count(),
        }
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password': 'Password tidak cocok.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.get_or_create(user=user, defaults={'auth_provider': 'email'})
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    auth_provider = serializers.SerializerMethodField()
    referral_code = serializers.SerializerMethodField()
    saved_gigs_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_superuser', 'date_joined', 'last_login',
            'auth_provider', 'referral_code', 'saved_gigs_count'
        )
        read_only_fields = ('id', 'is_staff', 'is_superuser', 'date_joined', 'last_login')

    def get_auth_provider(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.auth_provider
        return 'email'

    def get_referral_code(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.referral_code
        return ''

    def get_saved_gigs_count(self, obj):
        return obj.saved_gigs.count()
