import msgspec

from traduko.models import Language


class ProjectPath(msgspec.Struct):
    pk: int


class LanguageSchema(msgspec.Struct):
    code: str
    name: str
    direction: str
    google: bool
    deepl: bool
    yandex: bool
    plural_forms: str
    plural_examples_list: list[str]

    @classmethod
    def from_language(cls, language: Language) -> "LanguageSchema":
        return cls(
            code=language.code,
            name=language.name,
            direction=language.direction,
            google=language.google,
            deepl=language.deepl,
            yandex=language.yandex,
            plural_forms=language.plural_forms,
            plural_examples_list=language.plural_examples_list(),
        )
