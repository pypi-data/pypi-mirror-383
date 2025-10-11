import logging
import os
from pathlib import Path

import pytest

from anki_card_create.card_creator import CardCreator
from anki_card_create.models.kanki_input import KankiInput

logger = logging.getLogger(__name__)


@pytest.fixture
def anki2_path() -> Path:
    return Path(os.getenv("ANKI2_PATH"))


def test_send_anki_note_not_audio(global_data: dict[str, str | Path], create_test_data):
    """TESTCASE1: Send the created notes to the specified deck, without generating audios"""
    kanki_input = KankiInput.from_txt(
        data_fname=global_data["dir_path"] / global_data["test_file_name"],
        deck_name=global_data["deck_name"],
        model_name=global_data["model_name"],
    )

    card_creator = CardCreator()
    response_list = card_creator.send_notes(kanki_input=kanki_input, audio=False)
    assert len(response_list) == 2
    assert response_list[0].status_code == 200
    assert response_list[1].status_code == 200


def test_send_audio(global_data, create_test_audio, anki2_path):
    """TESTCASE2: Send the audio files to the Anki collection directory, without attaching it to the ankicard"""
    audio_path = global_data["dir_path"] / create_test_audio
    kanki_input = KankiInput.from_input_word(
        input_str="죄송합니다",
        deck_name=global_data["deck_name"],
        model_name=global_data["model_name"],
    )
    card_creator = CardCreator()
    response = card_creator._send_media(audio_path)
    assert response.error is None
    assert response.audio_file_name == global_data["audio_name"]
    # remove the audio file after testing
    # mp3_path = anki2_path / response.audio_file_name
    # os.remove(mp3_path.__str__())


def test_send_anki_note_with_audio(global_data, anki2_path):
    """TESTCASE3: Create an Anki card with audio"""
    kanki_input = KankiInput.from_input_word(
        input_str=global_data["test_word"],
        deck_name=global_data["deck_name"],
        model_name=global_data["model_name"],
    )
    card_creator = CardCreator()
    response_list = card_creator.send_notes(kanki_input=kanki_input, audio=True)
    logger.info(anki2_path / response_list[0].audio)
    assert response_list[0].status_code == 200
    # os.remove(anki2_path / response_list[0].audio)
