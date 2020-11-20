from django.contrib import admin
from .models import *


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'direction')
    ordering = ['code']
    search_fields = ['name', 'code']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'strings', 'words', 'characters')
    ordering = ['name']
    search_fields = ['name', 'description']
    autocomplete_fields = ['source_language', 'needed_languages', 'admins']


@admin.register(LanguageVersion)
class LanguageVersionAdmin(admin.ModelAdmin):
    list_display = ('project', 'language')
    ordering = ['project', 'language']
    search_fields = ['translators', 'translator_requests']
    autocomplete_fields = ['project', 'language', 'translators', 'translator_requests']


@admin.register(TrString)
class TrStringAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'path', 'pluralized', 'words', 'characters')
    ordering = ['project', 'path', 'name']
    search_fields = ['name', 'path']
    autocomplete_fields = ['project']
    list_filter = ('project',)


@admin.register(TrStringText)
class TrStringTextAdmin(admin.ModelAdmin):
    list_display = ('trstring', 'language', 'pluralized', 'text', 'state')
    ordering = ['trstring', 'language']
    search_fields = ['text']
    autocomplete_fields = ['trstring', 'language']
    list_filter = ('language',)


