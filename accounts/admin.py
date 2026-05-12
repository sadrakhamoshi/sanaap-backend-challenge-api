from django.contrib import admin
from accounts.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'is_superuser', 'is_staff')
    list_filter = ('role', 'is_superuser', 'is_staff')