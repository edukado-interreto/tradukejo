from django.db.models import Sum, Q
from .models import *
from collections import OrderedDict
import json


def get_subdirectories(trstrings, current_directory):
    string_subdirectories = trstrings.filter(path__startswith=current_directory)
    # TODO: improve this (distinct not supported by SQLite)
    subdirectories = {}
    for s in string_subdirectories:
        subdirectory = s.path[len(current_directory):].strip('/')
        if subdirectory.find('/') >= 0:
            subdirectory = subdirectory[0:subdirectory.find('/')]
        if subdirectory != '' and subdirectory not in subdirectories.keys():
            path = current_directory + ('/' if current_directory != '' else '') + subdirectory
            wordcharcount = string_subdirectories.filter(path__startswith=path).aggregate(Sum('words'), Sum('characters'))
            subdirectories[subdirectory] = {
                'path': path,
                # TODO filter by translation state
                'strings': string_subdirectories.filter(path__startswith=path).count(),
                'words': wordcharcount['words__sum'],
                'characters': wordcharcount['characters__sum'],
            }
    return OrderedDict(sorted(subdirectories.items()))


def update_string_count(project):
    trstrings = TrString.objects.filter(project=project).aggregate(Sum('words'), Sum('characters'))
    project.strings = project.trstring_set.count()
    project.words = trstrings['words__sum']
    project.characters = trstrings['characters__sum']
    project.save()


def get_project_language_statistics(project):
    languages = project.languageversion_set.all()
    for l in languages:
        translated = TrStringText.objects.filter(trstring__project=project, language=l.language, state=TRANSLATION_STATE_TRANSLATED)
        outdated = l.outdated_strings = TrStringText.objects.filter(trstring__project=project, language=l.language, state=TRANSLATION_STATE_OUTDATED)

        l.translated_strings = translated.count()
        l.outdated_strings = outdated.count()
        l.untranslated_strings = project.strings - l.translated_strings - l.outdated_strings

        translated_aggregated = translated.aggregate(Sum('trstring__words'), Sum('trstring__characters'))
        outdated_aggregated = outdated.aggregate(Sum('trstring__words'), Sum('trstring__characters'))

        l.translated_words = translated_aggregated['trstring__words__sum']
        if l.translated_words is None:
            l.translated_words = 0
        l.outdated_words = outdated_aggregated['trstring__words__sum']
        if l.outdated_words is None:
            l.outdated_words = 0
        l.untranslated_words = project.words - l.translated_words - l.outdated_words

        l.translated_characters = translated_aggregated['trstring__characters__sum']
        if l.translated_characters is None:
            l.translated_characters = 0
        l.outdated_characters = outdated_aggregated['trstring__characters__sum']
        if l.outdated_characters is None:
            l.outdated_characters = 0
        l.untranslated_characters = project.characters - l.translated_characters - l.outdated_characters

        l.translated_percent = l.translated_words / project.words * 100
        l.outdated_percent = l.outdated_words / project.words * 100
        l.untranslated_percent = l.untranslated_words / project.words * 100

    return languages


def filter_by_state(trstrings, current_language, state):
    if state == STATE_FILTER_UNTRANSLATED:
        return trstrings.exclude(trstringtext__language=current_language)
    elif state == STATE_FILTER_OUTDATED:
        return trstrings.filter(trstringtext__language=current_language, trstringtext__state=TRANSLATION_STATE_OUTDATED)
    elif state == STATE_FILTER_OUTDATED_UNTRANSLATED:
        untranslated = trstrings.exclude(trstringtext__language=current_language)
        outdated = trstrings.filter(trstringtext__language=current_language, trstringtext__state=TRANSLATION_STATE_OUTDATED)
        return (untranslated | outdated).distinct()  # Otherwise some strings appear several times, I don't know why
    else:
        return trstrings


def filter_by_search(trstrings, current_language, search_string):
    search_string = search_string.strip()
    if search_string == '' or trstrings.count() == 0:
        return trstrings
    else:
        in_source_language = trstrings.filter(trstringtext__language=trstrings[0].project.source_language, trstringtext__text__icontains=search_string)
        if trstrings[0].project.source_language == current_language:
            return in_source_language
        else:
            in_current_language = trstrings.filter(trstringtext__language=current_language, trstringtext__text__icontains=search_string)
            return (in_current_language | in_source_language).distinct()  # Otherwise some strings appear several times, I don't know why


# submitted_text has to be a JSON string like [{"name":"text[0]","value":"content here"},{"name":"text[1]","value":"content2 here"}]
# There should be several values for translations of pluralized strings, and one otherwise
def parse_submitted_text(submitted_text, is_pluralized, nplurals):
    json_data = json.loads(submitted_text)

    submitted_strings = {}
    for s in json_data:
        submitted_strings[s['name']] = s['value']

    if is_pluralized:
        words = 0
        characters = 0
        strings = []
        i = 0
        while i < nplurals and 'text['+str(i)+']' in submitted_strings.keys():
            t = submitted_strings['text['+str(i)+']'].strip()
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
