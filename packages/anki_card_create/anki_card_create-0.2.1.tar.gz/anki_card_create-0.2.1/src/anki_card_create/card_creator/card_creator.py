import json
import logging
from pathlib import Path

import requests
from requests import Response

from anki_card_create.config.settings import settings
from anki_card_create.exceptions import MediaAdditionError
from anki_card_create.models.anki_note import AnkiNote
from anki_card_create.models.kanki_input import KankiInput
from anki_card_create.models.response import AnkiNoteResponse, AnkiSendMediaResponse
from anki_card_create.services.utils import (
    create_audio,
    create_message,
)

logging.basicConfig(level=logging.INFO)


class CardCreator:
    def __init__(self) -> None:
        pass

    def send_notes(self, kanki_input: KankiInput, audio: bool = True) -> list[AnkiNoteResponse]:
        """Send the Anki notes to the Anki collection.

        Args:
            kanki_input (KankiInput): An input of the Anki notes.
            audio (bool, optional): If True, create an audio file from the front side of the Anki note. Defaults to True.

        Raises:
            MediaAdditionError: If the audio file is not added to the Anki collection.

        Returns:
            List[AnkiNoteResponse]: A list of the response of the Anki notes creation.

        """
        response_json_list = []
        # Create mp3 for a given anki-note and send it to Anki's media folder if audio is True
        anki_notes = kanki_input.anki_notes
        for anki_note in anki_notes:
            if audio:
                # Create the mp3 file from the front side of the anki-note
                audio_path = create_audio(anki_note.front)

                # Send the mp3 to Anki's media folder
                media_response = self._send_media(audio_path)
                if media_response.error is not None:
                    raise MediaAdditionError(media_response)

                # Create a str for denoting the media file
                audio_str = f"[sound:{media_response.audio_file_name}]"

                # remove the audio file that has been sent:
                audio_path.unlink()
            else:
                audio_str = ""

            # Create the Anki-note creation payload from the provided Anki-note
            note = {
                "deckName": anki_note.deckName,
                "modelName": anki_note.modelName,
                "fields": {
                    "表面": anki_note.front + audio_str,
                    "裏面": anki_note.back,
                },
            }
            params = {"note": note}

            # Send the request to add note into the specified deck, using anki connector
            response = self._anki_invoke(action="addNote", params=params)

            # Parse the response and create the response message
            if audio:
                card_create_response = self._create_response(
                    anki_note=anki_note,
                    connector_response=response,
                    audio=media_response.audio_file_name,
                )
            else:
                card_create_response = self._create_response(
                    anki_note=anki_note,
                    connector_response=response,
                )
            # Append the response message into a list
            response_json_list.append(card_create_response)
            logging.info(create_message(card_create_response))

        return response_json_list

    def _send_media(self, audio_path: Path | str) -> AnkiSendMediaResponse:
        """Send the created mp3 file to Anki collection folder (collection.media/).

        Args:
            audio_path (Union[Path, str]): _description_

        Returns:
            AnkiSendMediaResponse: _description_

        """
        # Convert the path into a Path datatype
        if not isinstance(audio_path, Path):
            audio_path = Path(audio_path)

        # Create the payload fot the anki connector request
        audio_filename = audio_path.name.__str__()
        audio_file_path = audio_path.__str__()
        params = {
            "filename": audio_filename,
            "path": audio_file_path,
        }

        # Send the request
        response = self._anki_invoke(action="storeMediaFile", params=params)

        return AnkiSendMediaResponse(
            audio_path=audio_file_path,
            audio_file_name=audio_filename,
            status_code=response.status_code,
            result=json.loads(response.text)["result"],
            error=json.loads(response.text)["error"],
        )

    def _anki_invoke(self, action: str, params: dict) -> Response:
        return requests.post(
            settings.api_url,
            json={"action": action, "version": 6, "params": params},
            timeout=30,
        )

    @staticmethod
    def _create_response(
        anki_note: AnkiNote,
        connector_response: requests.Response,
        audio: str | None = None,
    ) -> AnkiNoteResponse:
        response_json = connector_response.json()
        response_json["status_code"] = connector_response.status_code

        anki_note_dict = anki_note.model_dump()
        anki_note_dict.update(
            {
                "status_code": response_json["status_code"],
                "audio": audio,
                "result": response_json["result"],
                "error": response_json["error"],
            }
        )

        return AnkiNoteResponse(**anki_note_dict)
