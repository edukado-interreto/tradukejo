from django import forms
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
    update_texts = forms.BooleanField(label="Ĝisdatigi jam ekzistantajn ĉenojn kaj tradukojn", required=False)
    user_is_author = forms.BooleanField(label="Marki min kiel aŭtoron de importitaj tekstoj kaj tradukoj", required=False)
