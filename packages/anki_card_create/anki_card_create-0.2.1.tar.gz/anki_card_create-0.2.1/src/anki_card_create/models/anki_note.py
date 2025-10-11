from langdetect import detect
from pydantic import BaseModel, model_validator

from anki_card_create.config import InputLang, TranslatedLang, settings


class AnkiNote(BaseModel):
    """Schema for the input to create an Anki card."""

    deckName: str = settings.deck_name
    modelName: str = settings.model_name
    front: str
    back: str | None = None
    sentence: str | None = None
    translated_sentence: str | None = None
    audio: str | None = None
    frontLang: InputLang = settings.using_lang
    backLang: TranslatedLang = settings.translate_lang

    @model_validator(mode="after")
    def check_languages(self):
        """Validate the detected languages of the input fields."""
        front_lang = self.frontLang
        # back_lang = self.backLang

        # Detect languages of `front` and `back` fields
        detected_front_lang = detect(self.front)
        # detected_back_lang = detect(self.back)

        # Validate detected languages against expected languages
        if front_lang != detected_front_lang:
            raise ValueError(
                f"Expected language for 'front' field is '{front_lang}', but detected '{detected_front_lang}'."
            )

        return self
