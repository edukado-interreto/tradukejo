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


class ImportForm(forms.Form):
    file = forms.FileField(label="Dosiero", required=True)
    import_to = forms.CharField(label="Importi al la jena dosierujo:",
                                required=False)
    update_texts = forms.BooleanField(label="Ĝisdatigi jam ekzistantajn ĉenojn kaj tradukojn (tre malrapida!)", required=False)
    user_is_author = forms.BooleanField(label="Marki min kiel defaŭltan aŭtoron de importitaj tekstoj kaj tradukoj", required=False)


class ExportForm(forms.Form):
    path = forms.CharField(label="Dosierujo por eksporti (lasi malplena por eksporti ĉion)",
                           required=False)
    remove_path = forms.BooleanField(label="Forpreni la nomon de la dosierujo",
                                     required=False)
    languages = forms.MultipleChoiceField(label="Lingvoj por eksporti (lasi malplena por eksporti ĉiujn)",
                                          required=False,
                                          choices=[],
                                          widget=CheckboxSelectMultiple)

    def __init__(self, language_choices=None, *args, **kwargs):
        super(ExportForm, self).__init__(*args, **kwargs)
        if language_choices:
            self.fields['languages'].choices = language_choices


class POExportForm(ExportForm):
    untranslated_as_source_language = forms.BooleanField(label="Netradukitaj ĉenoj estos anstataŭigitaj per la fontolingvo (se ne, ili estos lasitaj malplenaj)",
                                                         required=False)
    include_outdated = forms.BooleanField(label="Eksporti ankaŭ retradukendajn tradukojn",
                                          required=False)
    po_file_name = forms.CharField(label="Nomo de PO/MO-dosieroj",
                                   required=False,
                                   help_text="Se malplena, ĉiuj estos en la sama dosierujo kaj la nomo estos la kodo de la lingvo. Alie, ili estos ekzemple <code><i>lingvokodo</i>/LC_MESSAGES/<i>nomo</i>.po</code>. Do ekzemple por Django-projekto, la valoro devas esti <code>django</code>.")
