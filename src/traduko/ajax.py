import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from traduko.models import Language, LanguageVersion, Project, TranslatorRequest

from .translation_functions import send_email_to_admins_about_translation_request


@login_required
def request_translator_permission(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    language = get_object_or_404(Language, pk=request.POST.get("language"))

    try:
        lv = LanguageVersion.objects.get(project=project, language=language)
    except LanguageVersion.DoesNotExist:
        lv = LanguageVersion(project=project, language=language)
        lv.save()

    if request.user in lv.translators.all():
        message = _("messages#request-already-allowed")
    elif (
        TranslatorRequest.objects.filter(user=request.user, language_version=lv).count()
        > 0
    ):
        message = _("messages#request-already-sent")
    else:
        translator_request = TranslatorRequest(
            user=request.user,
            explanation=request.POST.get("explanation"),
            language_version=lv,
        )
        translator_request.save()
        message = _("messages#request-sent")
        send_email_to_admins_about_translation_request(request, translator_request)

    button = render_to_string("traduko/project/translation_request_sent_button.html")
    response_dict = {"message": message, "button": button}
    return HttpResponse(json.dumps(response_dict, ensure_ascii=False))
