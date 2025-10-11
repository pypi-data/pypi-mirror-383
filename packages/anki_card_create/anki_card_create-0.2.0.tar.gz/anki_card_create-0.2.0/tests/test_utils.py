from anki_card_create.models.translator_input import TranslatorInput
from anki_card_create.services.translators import TranslationTool


def test_translation_tool():
    tool = TranslationTool(TranslatorInput(source="ko", target="ja", ai=False))
    assert tool.translate("안녕") == "こんにちは"
