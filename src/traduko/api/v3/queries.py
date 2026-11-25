"""Path and query parameters of the API v3."""

from typing import Annotated, Final

import msgspec

DEFAULT_PAGE_SIZE: Final = 100
MAX_PAGE_SIZE: Final = 1000


class CodePath(msgspec.Struct):
    code: str


class PkPath(msgspec.Struct):
    pk: int


# Unknown parameters are rejected: JSON:API requires a 400
# for `sort` and other parameters that the server does not support.


class DetailQuery(msgspec.Struct, forbid_unknown_fields=True):
    include: str | None = None


class ListQuery(DetailQuery, forbid_unknown_fields=True):
    page_number: Annotated[int, msgspec.Meta(ge=1)] = msgspec.field(
        default=1, name="page[number]"
    )
    page_size: Annotated[int, msgspec.Meta(ge=1, le=MAX_PAGE_SIZE)] = msgspec.field(
        default=DEFAULT_PAGE_SIZE, name="page[size]"
    )


class StringListQuery(ListQuery, forbid_unknown_fields=True):
    filter_path: str | None = msgspec.field(default=None, name="filter[path]")


class TranslationListQuery(ListQuery, forbid_unknown_fields=True):
    filter_language: str | None = msgspec.field(default=None, name="filter[language]")
