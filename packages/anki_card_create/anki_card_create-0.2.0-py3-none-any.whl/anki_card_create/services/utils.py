import uuid
from pathlib import Path

from navertts import NaverTTS

from anki_card_create.config import settings
from anki_card_create.models.response import AnkiNoteResponse


def create_message(card_create_response: AnkiNoteResponse) -> str:
    """Generate a readable message based on the response of Anki connector after sending the notes.

    Args:
        card_create_response (AnkiNoteResponse): _description_

    Returns:
        str: The message.

    """
    # Check if the deck exists and the note was added successfully
    if card_create_response.status_code == 200:
        word_being_sent = f"{card_create_response.front}, {card_create_response.back}"
        if card_create_response.error is not None:
            # Check if the error message indicates that the deck does not exist
            if "deck not found" in card_create_response.error:
                return word_being_sent + ":Error: Deck does not exist"
            return word_being_sent + f": Error: {card_create_response.error}"
        return word_being_sent + ": Note added successfully"
    return word_being_sent + ": Error adding note to deck"


def create_audio(text: str, path: Path | str = settings.mp3_path) -> Path:
    """Create an audio file (.mp3) for the input korean word. Based on Naver TTS API.

    Args:
        text (str): Korean word.
        path (Union[Path, str], optional): _description_. Defaults to MP3_PATH.

    Returns:
        Union[Path, str]: The path of the output audio file.
            For example: User/path/to/directory/naver_e9633695-8fce-4ea3-901a-489863a9214e.mp3

    """
    # texts = [note.front for note in self._anki_notes]
    if not isinstance(path, Path):
        path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    tts = NaverTTS(text)
    audio_filename = path / f"naver_{uuid.uuid4()}.mp3"
    tts.save(audio_filename)
    return audio_filename
