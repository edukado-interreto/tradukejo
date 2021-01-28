import difflib
from django.core.mail import send_mail
from django.db.models import Sum, Q, Count, Max
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from .models import *
from collections import OrderedDict
import json, html


def is_project_admin(user, project):
    if user.is_superuser or user in project.admins.all():
        return True
    else:
        return False


def is_allowed_to_translate(user, project, language):
    if is_project_admin(user, project):
        return True

    if project.locked or not project.visible:
        return False

    try:
        lv = LanguageVersion.objects.get(project=project, language=language)
    except LanguageVersion.DoesNotExist:
        lv = None

    if lv is not None and user in lv.translators.all():
        return True

    return False


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def mark_translations_as_outdated(trstring):
    trstring.trstringtext_set.exclude(language=trstring.project.source_language).update(
        state=TRANSLATION_STATE_OUTDATED)


def add_or_update_trstringtext(project, path, name, language, text, author, pluralized=False, force_update=True,
                               context='', minor=False, new_string=False, state=TRANSLATION_STATE_TRANSLATED,
                               importing_user=None):
    """
    Main function used to save strings. Translation right checks should be done before calling this function.
    text: text to be parsed with parse_submitted_text
    force_update: if existing texts should be replaced with new text
    minor: whether changes made to texts in source language are minor (and translations shouldn't be marked as outdated)
    context: context for the TrString, if we are editing it
    new_string: if we are adding a string (detected automatically otherwise)
    state: state of the added translation, by default translated
    importing_user: if provided, the string activities are marked as imports
    """

    editing_original = language == project.source_language
    new_string = new_string and editing_original

    # Checking if trstring and trstringtext exist (new_string parameter avoids unnecessary queries)
    if not new_string:
        try:
            current_string = TrString.objects.get(project=project, path=path, name=name)
        except TrString.DoesNotExist:
            new_string = True

    if new_string and not editing_original:  # Trying to add translation of non-existing TrString:
        return {
            'trstring': None,
            'trstringtext': None
        }

    if new_string:
        current_string = TrString(project=project, path=path, name=name)
        current_string.save()

    new_translation = new_string
    if not new_translation:
        try:
            translated_text = TrStringText.objects.get(language=language, trstring=current_string)
        except TrStringText.DoesNotExist:
            new_translation = True

    if new_translation:
        translated_text = TrStringText(language=language, trstring=current_string)

    if not new_translation and not force_update:
        return {
            'trstring': None,
            'trstringtext': None
        }

    if not editing_original:
        pluralized = TrStringText.objects.get(trstring=current_string,
                                              language=current_string.project.source_language).pluralized

    parsed_text_data = parse_submitted_text(text,
                                            pluralized,
                                            language.nplurals())

    if new_translation or parsed_text_data['text'] != translated_text.text or (editing_original and (
            translated_text.pluralized != pluralized or current_string.context != context)):  # If there are changes
        # If not new string and text has changed: save in history
        if not new_translation and parsed_text_data['text'] != translated_text.text:
            # Save as pluralized only if string has several forms
            old_version_pluralized = translated_text.number_of_pluralized_texts() == translated_text.language.nplurals() and translated_text.language.nplurals() > 1
            history = TrStringTextHistory(trstringtext=translated_text,
                                          pluralized=old_version_pluralized,
                                          text=translated_text.text,
                                          translated_by=translated_text.translated_by)
            history.save()

        # Update the translation
        if not editing_original and state not in [TRANSLATION_STATE_TRANSLATED, TRANSLATION_STATE_OUTDATED]:
            state = TRANSLATION_STATE_TRANSLATED
        translated_text.state = state
        translated_text.translated_by = author
        translated_text.text = parsed_text_data['text']

        # TrStringText has to be updated first, then TrString
        # Otherwise signals fire in the wrong order and translated word count breaks

        if editing_original:
            translated_text.pluralized = pluralized
            if not minor:  # Update translation status of translations
                mark_translations_as_outdated(current_string)
                translated_text.last_change = timezone.now()
        else:
            original_text = get_object_or_404(TrStringText, trstring=current_string,
                                              language=current_string.project.source_language)
            translated_text.pluralized = original_text.pluralized
            translated_text.last_change = timezone.now()
        translated_text.save()

        if editing_original:  # Update word and character count
            update_project_admins(author, current_string.project)
            current_string.context = context
            current_string.words = parsed_text_data['words']
            current_string.characters = parsed_text_data['characters']
            current_string.save()

        # Add activity to last activities
        activity = StringActivity(trstringtext=translated_text,
                                  language=language,
                                  user=author if importing_user is None else importing_user)
        if new_string:
            activity.action = ACTION_TYPE_ADD if importing_user is None else ACTION_TYPE_IMPORT
            activity.words = current_string.words
            activity.characters = current_string.characters
        elif new_translation:
            activity.action = ACTION_TYPE_TRANSLATE if importing_user is None else ACTION_TYPE_IMPORT
            activity.words = current_string.words
            activity.characters = current_string.characters
        else:
            activity.action = ACTION_TYPE_EDIT
        activity.save()

    update_translators_when_translating(author, current_string.project, language)

    return {
        'trstring': current_string,
        'trstringtext': translated_text
    }


def get_subdirectories(trstrings, current_directory):
    if current_directory != "":
        string_subdirectories = trstrings.filter(path__startswith=current_directory + "/")
    else:
        string_subdirectories = trstrings
    subdirectories = {}
    for s in string_subdirectories:
        subdirectory = s.path[len(current_directory):].strip('/')
        if subdirectory.find('/') >= 0:
            subdirectory = subdirectory[0:subdirectory.find('/')]
        if subdirectory != '' and subdirectory not in subdirectories.keys():
            path = current_directory + ('/' if current_directory != '' else '') + subdirectory
            wordcharcount = string_subdirectories.filter(Q(path=path) | Q(path__startswith=path + "/")).aggregate(
                Sum('words'), Sum('characters'))
            subdirectories[subdirectory] = {
                'path': path,
                'strings': string_subdirectories.filter(Q(path=path) | Q(path__startswith=path + "/")).count(),
                'words': wordcharcount['words__sum'],
                'characters': wordcharcount['characters__sum'],
            }
    return OrderedDict(sorted(subdirectories.items()))


def get_all_strings(project, language, state_filter, search_string=''):
    all_strings = TrString.objects.filter(project=project)
    all_strings = filter_by_state(all_strings, language, state_filter)
    all_strings = filter_by_search(all_strings, language, search_string)
    return all_strings


def get_strings_to_translate(all_strings, language, path, sort, start=0):
    strings = all_strings.filter(path=path)
    total_strings = strings.count()
    if sort == SORT_STRINGS_BY_NEWEST:
        strings = strings.order_by('-last_change')
    elif sort == SORT_STRINGS_BY_OLDEST:
        strings = strings.order_by('last_change')
    else:
        strings = sorted(strings, key=lambda i: natural_keys(i.name))

    strings = strings[start:start + settings.MAX_LOADED_STRINGS]

    for trstr in strings:
        trstr.original_text = TrStringText(trstring=trstr, language=trstr.project.source_language, text="", last_change=timezone.now())
        trstr.translated_text = None
        for trans in trstr.trstringtext_set.all():
            if trans.language == trstr.project.source_language:
                trstr.original_text = trans
            if trans.language == language:
                trstr.translated_text = trans

        if trstr.translated_text is None:
            trstr.state = TRANSLATION_STATE_UNTRANSLATED
        else:
            trstr.state = trstr.translated_text.state

    return [strings, len(strings) + start < total_strings]


def update_project_count(project):
    trstrings = TrString.objects.filter(project=project).aggregate(Sum('words'), Sum('characters'))
    project.strings = project.trstring_set.count()
    project.words = 0 if trstrings['words__sum'] is None else trstrings['words__sum']
    project.characters = 0 if trstrings['characters__sum'] is None else trstrings['characters__sum']
    project.save()


def update_all_language_versions_count(project):
    languageversions = project.languageversion_set.all()
    for lv in languageversions:
        update_language_version_count(lv)


def update_language_version_count(l):  # l: languageversion
    translated = TrStringText.objects.filter(trstring__project=l.project, language=l.language,
                                             state=TRANSLATION_STATE_TRANSLATED)
    outdated = l.outdated_strings = TrStringText.objects.filter(trstring__project=l.project, language=l.language,
                                                                state=TRANSLATION_STATE_OUTDATED)

    l.translated_strings = translated.count()
    l.outdated_strings = outdated.count()

    translated_aggregated = translated.aggregate(Sum('trstring__words'), Sum('trstring__characters'))
    outdated_aggregated = outdated.aggregate(Sum('trstring__words'), Sum('trstring__characters'))

    l.translated_words = translated_aggregated['trstring__words__sum']
    if l.translated_words is None:
        l.translated_words = 0
    l.outdated_words = outdated_aggregated['trstring__words__sum']
    if l.outdated_words is None:
        l.outdated_words = 0

    l.translated_characters = translated_aggregated['trstring__characters__sum']
    if l.translated_characters is None:
        l.translated_characters = 0
    l.outdated_characters = outdated_aggregated['trstring__characters__sum']
    if l.outdated_characters is None:
        l.outdated_characters = 0

    l.save()


def get_project_languages_for_user(project, user):
    if is_project_admin(user, project):
        available_languages = (Language.objects.filter(code=project.source_language.code) |
                               Language.objects.filter(languageversion__project=project)).distinct()
    else:
        available_languages = Language.objects.filter(languageversion__project=project,
                                                      languageversion__translators=user)
    return available_languages.order_by('code')


def get_project_language_statistics(project, user):
    all_lv = project.languageversion_set.all()

    # Getting list of translators for each language from the StringActivity table
    activities = StringActivity.objects.filter(trstringtext__trstring__project=project, action=ACTION_TYPE_TRANSLATE). \
        values('language__code', 'user__pk', 'user__username'). \
        annotate(strings=Count('trstringtext'), words_sum=Sum('words')). \
        order_by('-words_sum')

    all_activities = {}
    for activity in activities:
        if activity['language__code'] not in all_activities.keys():
            all_activities[activity['language__code']] = []
        all_activities[activity['language__code']].append(activity)

    # Now getting language versions for current user
    if is_project_admin(user, project):
        current_user = all_lv
        other_available = LanguageVersion.objects.none()
    else:
        current_user = all_lv.filter(translators=user)
        other_available = all_lv.exclude(translators=user)

    # Add activities to language version objects (have to do it twice)
    for lv in current_user:
        if lv.language.code in all_activities.keys():
            lv.translator_stats = all_activities[lv.language.code]
        else:
            lv.translator_stats = []

    for lv in other_available:
        if lv.language.code in all_activities.keys():
            lv.translator_stats = all_activities[lv.language.code]
        else:
            lv.translator_stats = []
        lv.translation_request_sent = lv.translatorrequest_set.filter(user=user).count() > 0

    return {
        'current_user': current_user,
        'other_available': other_available,
    }


# Returns languages that don't have a language version in a given project but could be added
def addible_languages(project):
    if project.needed_languages.count() > 0:
        languages = project.needed_languages.all()
    else:
        languages = Language.objects.all()
    languages = languages.exclude(code=project.source_language.code).exclude(languageversion__project=project)
    return languages.order_by('code')


def filter_by_state(trstrings, current_language, state):
    if state == STATE_FILTER_UNTRANSLATED:
        return trstrings.exclude(trstringtext__language=current_language)
    elif state == STATE_FILTER_OUTDATED:
        return trstrings.filter(trstringtext__language=current_language, trstringtext__state=TRANSLATION_STATE_OUTDATED)
    elif state == STATE_FILTER_OUTDATED_UNTRANSLATED:
        untranslated = trstrings.exclude(trstringtext__language=current_language)
        outdated = trstrings.filter(trstringtext__language=current_language,
                                    trstringtext__state=TRANSLATION_STATE_OUTDATED)
        return (untranslated | outdated).distinct()  # Otherwise some strings appear several times, I don't know why
    else:
        return trstrings


def filter_by_search(trstrings, current_language, search_string):
    search_string = search_string.strip()
    if search_string == '' or trstrings.count() == 0:
        return trstrings
    else:
        in_source_language = trstrings.filter(trstringtext__language=trstrings[0].project.source_language,
                                              trstringtext__text__icontains=search_string)
        if trstrings[0].project.source_language == current_language:
            return in_source_language
        else:
            in_current_language = trstrings.filter(trstringtext__language=current_language,
                                                   trstringtext__text__icontains=search_string)
            return (
                        in_current_language | in_source_language).distinct()  # Otherwise some strings appear several times, I don't know why


# submitted_text has to be a JSON string like [{"name":"text[0]","value":"content here"},{"name":"text[1]","value":"content2 here"}]
# Can also be just a JSON array of strings or a simple string
# There should be several values for translations of pluralized strings, and one otherwise
def parse_submitted_text(submitted_text, is_pluralized, nplurals):
    try:
        json_data = json.loads(submitted_text)
    except ValueError as e:
        json_data = [{'name': 'text[0]', 'value': submitted_text}, ]

    submitted_strings = {}
    i = 0
    for s in json_data:
        if isinstance(s, dict):
            submitted_strings[s['name']] = s['value']
        else:
            submitted_strings[f'text[{i}]'] = s
        i = i + 1

    if is_pluralized:
        words = 0
        characters = 0
        strings = []
        i = 0
        while i < nplurals and 'text[' + str(i) + ']' in submitted_strings.keys():
            t = submitted_strings['text[' + str(i) + ']'].strip()
            words = words + len(t.split())
            characters = characters + len(t)
            strings.append(t)
            i = i + 1
        text = json.dumps(strings, ensure_ascii=False)
    else:
        text = submitted_strings['text[0]'] if 'text[0]' in submitted_strings.keys() else submitted_text
        text = text.strip()
        words = len(text.split())
        characters = len(text)
    return {
        'text': text,
        'words': words,
        'characters': characters,
    }


def get_text_difference(text, n_text):
    """
    http://stackoverflow.com/a/788780
    Unify operations between two compared strings seqm is a difflib.
    SequenceMatcher instance whose a & b are strings
    """
    seqm = difflib.SequenceMatcher(None, text, n_text)
    output = []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append(f"<ins>{seqm.b[b0:b1]}</ins>")
        elif opcode == 'delete':
            output.append(f"<del>{seqm.a[a0:a1]}</del>")
        elif opcode == 'replace':
            # seqm.a[a0:a1] -> seqm.b[b0:b1]
            output.append(f"<del>{seqm.a[a0:a1]}</del>")
            output.append(f"<ins>{seqm.b[b0:b1]}</ins>")
        else:
            raise RuntimeError
    return ''.join(output)


def get_history_comparison(history):
    """
    Generates visual comparison of changes in the history of versions of a translated text.
    It adds to history object an ordered dictionary. A simple string has only one element in this dictionary,
    but it may be more if we are dealing with a pluralized string.
    """
    for i in range(len(history) - 1):
        new = history[i]
        new_texts = new.pluralized_text_dictionary()
        old = history[i + 1]
        old_texts = old.pluralized_text_dictionary()

        new.comparison = OrderedDict()

        if len(new_texts) == 1 and len(old_texts) == 1:  # Non-pluralized string
            new.comparison['1'] = get_text_difference(html.escape(old_texts['1']), html.escape(new_texts['1']))
        elif len(new_texts) == len(old_texts):  # Pluralized string
            for j in range(len(new_texts)):
                keys = list(new_texts.keys())
                new_values = list(new_texts.values())
                old_values = list(old_texts.values())
                new.comparison[keys[j]] = get_text_difference(html.escape(old_values[j]), html.escape(new_values[j]))
        elif len(old_texts) == 1:  # Old string is not pluralized, new one is
            old_values = list(old_texts.values())
            old_text = old_values[0]
            for number, text in new_texts.items():
                new.comparison[number] = get_text_difference(html.escape(old_text), html.escape(text))
        elif len(new_texts) == 1:  # Old string is pluralized, new one is not
            new_values = list(new_texts.values())
            new_text = new_values[0]
            new.comparison['1'] = get_text_difference(html.escape(old_texts['1']), html.escape(new_text))
        else:  # Pluralized but with different amounts of plural forms, no comparison shown because something is wrong
            new.comparison = new_texts
            for number, text in new_texts.items():
                new.comparison[number] = html.escape(text)

    # Last version: nothing to compare, just put the text
    history[-1].comparison = history[-1].pluralized_text_dictionary()

    return history


def send_email_to_admins_about_translation_request(request, translator_request):
    project = translator_request.language_version.project
    language = translator_request.language_version.language
    administrators = project.admins.filter(email_translation_request=True)
    for admin in administrators:
        mail_context = {
            'admin': admin,
            'project': project,
            'language': language,
            'translator_request': translator_request,
            'url': request.build_absolute_uri(reverse('translator_request_list', args=(project.pk,))),
        }
        html_message = render_to_string("traduko/email/new-translator-request.html", mail_context)
        plain_text_message = strip_tags(html_message)

        send_mail(
            'Tradukejo de E@I: peto de tradukrajto por ' + project.name,
            plain_text_message,
            None,
            [admin.email],
            html_message=html_message
        )


def update_translators_when_translating(user, project, language):
    if user is not None and language != project.source_language:
        try:
            lv = LanguageVersion.objects.get(project=project, language=language)
        except LanguageVersion.DoesNotExist:  # Shouldn't happen
            lv = LanguageVersion(project=project, language=language)
            lv.save()
        if user not in lv.translators.all():
            lv.translators.add(user)
            lv.save()


def update_project_admins(user, project):
    if user is not None and user.is_superuser and user not in project.admins.all():
        project.admins.add(user)
        project.save()


def get_last_activities(project, limit=50):
    activities = StringActivity.objects.filter(trstringtext__trstring__project=project). \
                     values('date', 'language__code', 'language__name', 'user__pk', 'user__username', 'action'). \
                     annotate(last=Max('datetime'), strings=Count('trstringtext', distinct=True), words_sum=Sum('words')).order_by(
        '-last')[0:limit]
    last_activities = {}
    for activity in activities:
        if activity['date'] not in last_activities.keys():
            last_activities[activity['date']] = []
        last_activities[activity['date']].append(activity)
    return last_activities
