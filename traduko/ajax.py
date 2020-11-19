from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import *
from datetime import datetime
from .translation_functions import *


@csrf_exempt
def save_translation(request, trstring_id, language):
    # TODO: rights
    # TODO: if no change
    if request.method != "POST":
        return HttpResponse('')

    current_language = get_object_or_404(Language, code=language)
    current_string = get_object_or_404(TrString, pk=trstring_id)
    editmode = current_language == current_string.project.source_language

    try:
        translated_text = TrStringText.objects.get(language=current_language, trstring=current_string)
    except ObjectDoesNotExist:
        translated_text = TrStringText(language=current_language, trstring=current_string)

    parsed_text_data = parse_submitted_text(request.POST.get('text'),
                                            TrStringText.objects.get(trstring=current_string, language=current_string.project.source_language).pluralized,
                                            current_language.nplurals())

    translated_text.state = TRANSLATION_STATE_TRANSLATED
    translated_text.translated_by = request.user
    translated_text.text = parsed_text_data['text']

    if editmode:  # Update word and character count
        translated_text.pluralized = bool(request.POST.get('pluralized') == 'true')
        current_string.context = request.POST.get('context')
        current_string.words = parsed_text_data['words']
        current_string.characters = parsed_text_data['characters']
        current_string.save()
        update_string_count(current_string.project)

        minor_change = bool(request.POST.get('minor') == 'true')  # Update translation status of translations
        if not minor_change:
            current_string.trstringtext_set.exclude(language=current_language).update(state=TRANSLATION_STATE_OUTDATED)
            translated_text.last_change = datetime.now()
    else:
        original_text = get_object_or_404(TrStringText, trstring=current_string,
                                          language=current_string.project.source_language)
        translated_text.pluralized = original_text.pluralized
        translated_text.last_change = datetime.now()

    translated_text.save()

    current_string.state = TRANSLATION_STATE_TRANSLATED
    current_string.translated_text = translated_text
    current_string.original_text = TrStringText.objects.get(language=current_string.project.source_language, trstring=current_string)

    context = {
        'editmode': editmode,
        'str': current_string,
        'language': current_language,
    }
    return render(request, "traduko/translation/translation-row.html", context)


def get_string_translation(request, trstring_id, language):
    # TODO: rights
    translated_text = get_object_or_404(TrStringText, language=language, trstring=trstring_id)
    str = TrString()
    str.original_text = translated_text
    context = {
        'str': str
    }
    return render(request, "traduko/translation/original-text.html", context)


def change_translation_state(request, trstringtext_id, state):
    trstringtext = get_object_or_404(TrStringText, pk=trstringtext_id)
    if trstringtext.language == trstringtext.trstring.project.source_language:
        raise Http404('Malĝusta ĉeno')
    trstringtext.state = state
    trstringtext.save()
    # TODO: rights

    current_string = trstringtext.trstring
    current_string.state = state
    current_string.translated_text = trstringtext
    current_string.original_text = TrStringText.objects.get(language=current_string.project.source_language,
                                                            trstring=current_string)

    context = {
        'editmode': False,
        'str': current_string,
        'language': trstringtext.language,
    }
    return render(request, "traduko/translation/translation-row.html", context)


def markoutdated(request, trstringtext_id):
    return change_translation_state(request, trstringtext_id, TRANSLATION_STATE_OUTDATED)


def marktranslated(request, trstringtext_id):
    return change_translation_state(request, trstringtext_id, TRANSLATION_STATE_TRANSLATED)
