from itertools import batched

from django.contrib import admin, messages
from django.db.models import OuterRef, Subquery
from django.utils.translation import gettext_lazy as _

from traduko.deepl import deepl_translate
from traduko.translation_functions import (
    add_or_update_trstringtext,
    parse_submitted_text,
)

from .models import *


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "direction")
    ordering = ["code"]
    search_fields = ["name", "code"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "strings", "words", "characters")
    ordering = ["name"]
    search_fields = ["name", "description"]
    autocomplete_fields = ["source_language", "needed_languages", "admins"]


@admin.register(LanguageVersion)
class LanguageVersionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "project", "language")
    ordering = ["project", "language"]
    search_fields = ["translators__username", "language__name", "language__code"]
    autocomplete_fields = ["project", "language", "translators"]
    list_filter = ["project", "language"]
    actions = ["translate_untranslated_with_deepl"]

    @admin.action(
        permissions=["change"],
        description=_("Translate untranslated with DeepL"),
    )
    def translate_untranslated_with_deepl(self, request, queryset):
        num_lang, num_str = 0, 0

        for langver in queryset.filter(language__deepl=True):
            project, language = langver.project, langver.language
            untranslated = TrString.objects.untranslated(project, language)

            # Need to batch due to DeepL API v2 limitation
            for trstrings in batched(untranslated, 50):
                texts = [trstr.source_text for trstr in trstrings]
                translated = deepl_translate(project, texts, language)

                for trstring, text in zip(trstrings, translated):
                    add_or_update_trstringtext(
                        project=project,
                        path=trstring.path,
                        name=trstring.name,
                        language=language,
                        text=text,
                        author=request.user,
                        state=TRANSLATION_STATE_OUTDATED,
                    )
                num_str += len(translated)

            num_lang += 1

        msg = _("Translated %d strings in %d languages" % (num_str, num_lang))
        self.message_user(request, msg, level=messages.SUCCESS)


@admin.register(TranslatorRequest)
class TranslatorRequestAdmin(admin.ModelAdmin):
    list_display = ("language_version", "user", "create_date")
    ordering = ["create_date"]
    search_fields = ["language_version", "user"]
    autocomplete_fields = ["language_version", "user"]


@admin.register(TrString)
class TrStringAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "project",
        "path",
        "name",
        "words",
        "characters",
        "last_change",
    )
    ordering = ["project", "path", "name"]
    search_fields = ["name", "path"]
    autocomplete_fields = ["project"]
    list_filter = ("project",)


@admin.register(TrStringText)
class TrStringTextAdmin(admin.ModelAdmin):
    list_display = ("__str__", "trstring", "language", "pluralized", "text", "state")
    ordering = ["trstring", "language"]
    search_fields = ["text"]
    autocomplete_fields = ["trstring", "language"]
    list_filter = ("language", "trstring__project")
    actions = ["mark_outdated", "mark_translated"]

    @admin.action(description="Mark translations as outdated")
    def mark_outdated(self, request, queryset):
        queryset.update(state=TRANSLATION_STATE_OUTDATED)

    @admin.action(description="Mark translations as translated")
    def mark_translated(self, request, queryset):
        queryset.update(state=TRANSLATION_STATE_TRANSLATED)


@admin.register(TrStringTextHistory)
class TrStringTextHistoryAdmin(admin.ModelAdmin):
    list_display = ("trstringtext", "pluralized", "text", "create_date")
    ordering = ["trstringtext"]
    search_fields = ["text"]
    autocomplete_fields = [
        "trstringtext",
    ]
    list_filter = ("trstringtext__trstring__project",)


@admin.register(StringActivity)
class StringActivityAdmin(admin.ModelAdmin):
    list_display = (
        "trstringtext",
        "user",
        "language",
        "action",
        "words",
        "characters",
        "date",
        "datetime",
    )
    autocomplete_fields = ["trstringtext", "language", "user"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("trstringtext", "author", "text", "create_date")
    autocomplete_fields = ["trstringtext", "author"]
