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
    list_display = ('__str__', 'project', 'language')
    ordering = ['project', 'language']
    search_fields = ['translators']
    autocomplete_fields = ['project', 'language', 'translators']


@admin.register(TranslatorRequest)
class TranslatorRequestAdmin(admin.ModelAdmin):
    list_display = ('language_version', 'user', 'create_date')
    ordering = ['create_date']
    search_fields = ['language_version', 'user']
    autocomplete_fields = ['language_version', 'user']


@admin.register(TrString)
class TrStringAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'project', 'path', 'name', 'words', 'characters', 'last_change')
    ordering = ['project', 'path', 'name']
    search_fields = ['name', 'path']
    autocomplete_fields = ['project']
    list_filter = ('project',)


@admin.register(TrStringText)
class TrStringTextAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'trstring','language', 'pluralized', 'text', 'state')
    ordering = ['trstring', 'language']
    search_fields = ['text']
    autocomplete_fields = ['trstring', 'language']
    list_filter = ('language','trstring__project')
    actions = ['mark_outdated', 'mark_translated']


    @admin.action(description='Mark translations as outdated')
    def mark_outdated(self, request, queryset):
        queryset.update(state=TRANSLATION_STATE_OUTDATED)


    @admin.action(description='Mark translations as translated')
    def mark_translated(self, request, queryset):
        queryset.update(state=TRANSLATION_STATE_TRANSLATED)


@admin.register(TrStringTextHistory)
class TrStringTextHistoryAdmin(admin.ModelAdmin):
    list_display = ('trstringtext', 'pluralized', 'text', 'create_date')
    ordering = ['trstringtext']
    search_fields = ['text']
    autocomplete_fields = ['trstringtext',]
    list_filter = ('trstringtext__trstring__project',)


@admin.register(StringActivity)
class StringActivityAdmin(admin.ModelAdmin):
    list_display = ('trstringtext', 'user', 'language', 'action', 'words', 'characters', 'date', 'datetime')
    autocomplete_fields = ['trstringtext', 'language', 'user']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('trstringtext', 'author', 'text', 'create_date')
    autocomplete_fields = ['trstringtext', 'author']
