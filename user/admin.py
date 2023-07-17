from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name',)
    readonly_fields = ('date_joined', 'last_login',)
    exclude = ( 'is_superuser','is_staff', 'user_permissions', 'groups', )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    ordering = ['-date_joined']
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(CustomUser, CustomUserAdmin)
