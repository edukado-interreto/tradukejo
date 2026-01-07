from rest_framework import serializers

from traduko.models import Language


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            "code",
            "name",
            "direction",
            "google",
            "deepl",
            "yandex",
            "plural_forms",
            "plural_examples_list",
        ]
