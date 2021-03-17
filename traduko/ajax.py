from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import *
from .decorators import *
from .translation_functions import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json


@login_required
def request_translator_permission(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    language = get_object_or_404(Language, pk=request.POST.get('language'))

    try:
        lv = LanguageVersion.objects.get(project=project, language=language)
    except LanguageVersion.DoesNotExist:
        lv = LanguageVersion(project=project, language=language)
        lv.save()

    if request.user in lv.translators.all():
        message = 'Vi jam havas la rajton traduki al ĉi tiu lingvo.'
    elif TranslatorRequest.objects.filter(user=request.user, language_version=lv).count() > 0:
        message = 'Vi jam sendis peton por ĉi tiu lingvo.'
    else:
        translator_request = TranslatorRequest(user=request.user, explanation=request.POST.get('explanation'), language_version=lv)
        translator_request.save()
        print(translator_request)
        message = 'La peto estis sendita.'
        send_email_to_admins_about_translation_request(request, translator_request)

    button = render_to_string("traduko/project/translation_request_sent_button.html")
    response_dict = {
        'message': message,
        'button': button
    }
    return HttpResponse(json.dumps(response_dict, ensure_ascii=False))
