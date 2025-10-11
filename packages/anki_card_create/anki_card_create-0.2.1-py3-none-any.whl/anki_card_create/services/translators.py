from abc import ABC, abstractmethod

from deep_translator import GoogleTranslator

from anki_card_create.models.translator_input import TranslatorInput


class TranslatorStrategy(ABC):
    @abstractmethod
    def translate(self, word: str) -> str | None:
        pass


class SimpleGoogleTranslatorStrategy:
    def __init__(self, translation_input: TranslatorInput) -> None:
        self._translator = GoogleTranslator(
            source=translation_input.source,
            target=translation_input.target,
        )

    def translate(self, word: str) -> str | None:
        return self._translator.translate(word)


class AITranslatorStrategy:
    def __init__(self, translation_input: TranslatorInput) -> None:
        self._translator = translation_input

    def translate(self, word: str) -> str | None:
        raise NotImplementedError("AI translation is not implemented yet.")


class TranslationTool:
    def __init__(self, translation_input: TranslatorInput):
        # Save the AI flag
        self._strategy = self._init_strategy(translation_input)

    def _init_strategy(self, input: TranslatorInput):
        if not input.ai:
            return SimpleGoogleTranslatorStrategy(input)
        return AITranslatorStrategy(input)

    def translate(self, word: str) -> str | None:
        return self._strategy.translate(word)
