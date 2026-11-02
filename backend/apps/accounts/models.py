import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    AUTH_PROVIDER_CHOICES = [
        ('email', 'Email / Password'),
        ('google', 'Google Account'),
        ('guest', 'Guest (Tamu)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    auth_provider = models.CharField(max_length=20, choices=AUTH_PROVIDER_CHOICES, default='email')
    referral_code = models.CharField(max_length=30, blank=True, unique=True)
    avatar_url = models.URLField(blank=True, null=True)
    last_active = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            random_suffix = uuid.uuid4().hex[:6].upper()
            username_prefix = ''.join(c for c in self.user.username[:6] if c.isalnum()).upper() or 'GIGS'
            self.referral_code = f"GT-{username_prefix}-{random_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.get_auth_provider_display()})"


class SavedGig(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_gigs')
    gig = models.ForeignKey('gigs.Gigs', on_delete=models.CASCADE, related_name='saved_by_users', db_column='gig_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts_savedgig'
        unique_together = ('user', 'gig')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.gig.title}"
