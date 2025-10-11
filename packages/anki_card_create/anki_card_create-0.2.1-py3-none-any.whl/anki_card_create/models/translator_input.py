from pydantic import BaseModel

from anki_card_create.config import InputLang, TranslatedLang


class TranslatorInput(BaseModel):
    """A data model to create the translator module."""

    source: InputLang = InputLang.ko
    target: TranslatedLang = TranslatedLang.ja
    ai: bool = False
