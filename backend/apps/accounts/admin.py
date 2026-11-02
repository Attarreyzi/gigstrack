from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

# Unregister default Django admin user & group
try:
    admin.site.unregister(User)
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = (
        'avatar_preview', 'username', 'email', 'full_name_display',
        'is_staff_badge', 'is_active_badge', 'date_joined'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    list_filter_submit = True

    @display(description="User")
    def avatar_preview(self, obj):
        initial = (obj.first_name or obj.username or "U")[0].upper()
        bg_gradient = "linear-gradient(135deg, #FF0055, #7928CA)" if obj.is_staff else "linear-gradient(135deg, #2196F3, #00F0FF)"
        return format_html(
            '<div style="width: 36px; height: 36px; border-radius: 50%; background: {}; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">'
            '{}'
            '</div>',
            bg_gradient, initial
        )

    @display(description="Nama Lengkap")
    def full_name_display(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else "-"

    @display(description="Role / Akses")
    def is_staff_badge(self, obj):
        if obj.is_superuser:
            return format_html('<span style="background: rgba(255,0,85,0.2); border: 1px solid #FF0055; color: #FF0055; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold;">SUPERUSER</span>')
        elif obj.is_staff:
            return format_html('<span style="background: rgba(0,240,255,0.2); border: 1px solid #00F0FF; color: #00F0FF; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold;">STAFF / ADMIN</span>')
        return format_html('<span style="background: rgba(255,255,255,0.06); color: #888; padding: 2px 8px; border-radius: 9999px; font-size: 11px;">MEMBER</span>')

    @display(description="Status")
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #00E676; font-weight: bold;">● Aktif</span>')
        return format_html('<span style="color: #FF5252; font-weight: bold;">● Nonaktif</span>')


@admin.register(Group)
class CustomGroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
