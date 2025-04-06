from django.contrib import admin
from .models import Athlet, Result

@admin.register(Athlet)
class AthletAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender', 'rank', 'team', 'publish']
    list_filter = ['gender', 'team', 'region']
    search_fields = ['name', 'team', 'region']
    date_hierarchy = 'publish'
    ordering = ['name', 'gender']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['athlet', 'score', 'created_at']
    list_filter = ['athlet', 'created_at']
    search_fields = ['athlet__name']