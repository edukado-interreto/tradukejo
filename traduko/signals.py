from .models import *
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .translation_functions import update_project_count, update_language_version_count, update_all_language_versions_count


# See also import_export_functions where these functions are temporarily disabled

@receiver(post_save, sender=TrStringText)
def update_project_count_from_trstringtext(sender, instance, **kwargs):
    if instance.trstring.project.source_language != instance.language:
        lv = LanguageVersion.objects.get(project=instance.trstring.project, language=instance.language)
        update_language_version_count(lv)
    # If we are editing/adding the text in the source language, the associated TrString should already be updated


@receiver(post_save, sender=TrString)
@receiver(post_delete, sender=TrString)
def update_project_count_from_trstring(sender, instance, **kwargs):
    update_project_count(instance.project)
    update_all_language_versions_count(instance.project)
