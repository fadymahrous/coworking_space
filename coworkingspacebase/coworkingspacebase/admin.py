from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts_app.models import User


class UserAdmin(BaseUserAdmin):
    ordering = ('email',)


admin.site.register(User, UserAdmin)