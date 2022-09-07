from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email',
        'first_name', 'last_name', 'date_joined',
    )

    search_fields = (
        'username', 'email', 'first_name', 'last_name',
    )

    list_filter = (
        'email', 'first_name', 'date_joined',
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    search_fields = ('user', 'author',)
