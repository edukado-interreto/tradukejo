from django import forms
from django.forms import CheckboxSelectMultiple

from traduko.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'url', 'image', 'source_language', 'description', 'needed_languages', 'visible', 'locked']
        labels = {
            'name': 'Nomo',
            'url': 'URL',
            'image': 'Bildo',
            'source_language': 'Fontolingvo',
            'description': 'Priskribo',
            'needed_languages': 'Bezonataj lingvoj',
            'visible': 'Videbla',
            'locked': 'Ŝlosita',
        }
        help_texts = {
            'needed_languages': 'Lasi malplena, se ĉiuj lingvoj estas bezonataj'
        }


class CSVImportForm(forms.Form):
    file = forms.FileField(label="Dosiero", required=True)
    update_texts = forms.BooleanField(label="Ĝisdatigi jam ekzistantajn ĉenojn kaj tradukojn (malrapida!)", required=False)
    user_is_author = forms.BooleanField(label="Marki min kiel aŭtoron de importitaj tekstoj kaj tradukoj", required=False)


class JSONExportForm(forms.Form):
    path = forms.CharField(label="Dosierujo por eksporti (lasi malplena por eksporti ĉion)",
                           required=False)
    languages = forms.MultipleChoiceField(label="Lingvoj por eksporti (lasi malplena por eksporti ĉiujn)",
                                          required=False,
                                          choices=[],
                                          widget=CheckboxSelectMultiple)

    def __init__(self, language_choices=None, *args, **kwargs):
        super(JSONExportForm, self).__init__(*args, **kwargs)
        if language_choices:
            self.fields['languages'].choices = language_choices
