from django.contrib import admin
from django.contrib.admin import ModelAdmin

from applications.tokens.models import Token


@admin.register(Token)
class TokenAdmin(ModelAdmin):
    list_display = ('token', 'created_at')
