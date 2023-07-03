from django.contrib import admin
from .models import (
    User,
    FollowingAuthor,
)


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'username',
    )
    search_fields = (
        'name',
    )
    empty_value_display = '-пусто-'


class FollowingAuthorAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author'
    )
    search_fields = (
        'user',
    )
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(FollowingAuthor, FollowingAuthorAdmin)
