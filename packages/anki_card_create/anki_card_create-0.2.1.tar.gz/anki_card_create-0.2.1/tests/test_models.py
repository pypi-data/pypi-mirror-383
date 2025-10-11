import logging

from anki_card_create.config import settings
from anki_card_create.models.anki_note import AnkiNote
from anki_card_create.models.kanki_input import KankiInput
from anki_card_create.models.translator_input import TranslatorInput
from anki_card_create.services.translators import TranslationTool

# TODO: will remove after applying DI
translator_settings = TranslatorInput(
    source=settings.using_lang,
    target=settings.translate_lang,
    ai=settings.ai,
)
translator = TranslationTool(translator_settings)

logger = logging.getLogger(__name__)


def test_anki_note_model():
    """TESTCASE1: Create a note by manually input the text"""
    note = AnkiNote(
        deckName="korean",
        modelName="Basic (裏表反転カード付き)+sentense",
        front="안녕하세요",
        back="こんにちは",
    )

    assert note.deckName == "korean"
    assert note.modelName == "Basic (裏表反転カード付き)+sentense"
    assert note.front == "안녕하세요"
    assert note.back == "こんにちは"
    assert note.frontLang == "ko"


def test_anki_note_model_no_back():
    """TESTCASE2: Create a note by manually input the text without back"""
    note = AnkiNote(
        deckName="korean",
        modelName="Basic (裏表反転カード付き)+sentense",
        front="안녕하세요",
    )

    assert note.deckName == "korean"
    assert note.modelName == "Basic (裏表反転カード付き)+sentense"
    assert note.front == "안녕하세요"
    assert note.frontLang == "ko"


def test_create_anki_notes_from_txt(global_data, create_test_data):
    """TESTCASE3: Create anki notes from a given txt file."""
    logger.info("TESTCASE3")
    logger.info(global_data["dir_path"] / global_data["test_file_name"])

    anki_notes = KankiInput.from_txt(
        data_fname=global_data["dir_path"] / global_data["test_file_name"],
    ).anki_notes

    assert len(anki_notes) == 2
    assert anki_notes[0].front == "죄송합니다"
    assert anki_notes[1].front == "이거 얼마예요"
    assert anki_notes[0].back == translator.translate("죄송합니다")
    assert anki_notes[1].back == translator.translate("이거 얼마예요")


def test_create_anki_notes_from_input(global_data):
    """TESTCASE4: Create anki notes from a single input"""
    anki_notes = KankiInput.from_input_word(
        input_str="죄송합니다",
        deck_name=global_data["deck_name"],
        model_name=global_data["model_name"],
    ).anki_notes
    assert len(anki_notes) == 1
    assert anki_notes[0].front == "죄송합니다"
    assert anki_notes[0].back == translator.translate("죄송합니다")
