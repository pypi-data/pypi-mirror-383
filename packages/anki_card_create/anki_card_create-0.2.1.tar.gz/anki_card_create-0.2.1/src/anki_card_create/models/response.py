from pydantic import BaseModel, ConfigDict

from anki_card_create.models.anki_note import AnkiNote


class AnkiNoteResponse(AnkiNote):
    """Response model for sending the created notes to the Anki DB."""

    status_code: int
    result: None | int
    error: None | str
    audio: str | None = None
    model_config = ConfigDict(from_attributes=True)


class AnkiSendMediaResponse(BaseModel):
    """Response after sending the created mp3 file to Anki collection folder."""

    audio_path: str
    audio_file_name: str
    status_code: int
    result: None | str = None
    error: None | str = None
