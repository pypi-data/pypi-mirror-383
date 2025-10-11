import logging
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from anki_card_create.config import settings
from anki_card_create.models.anki_note import AnkiNote
from anki_card_create.models.translator_input import TranslatorInput
from anki_card_create.services.translators import TranslationTool

logging.basicConfig(level=logging.INFO)


class KankiInput(BaseModel):
    """A schema for the input of Kanki command line to create Anki notes."""

    # A list of Anki notes to be created
    anki_notes: list[AnkiNote]
    model_config = ConfigDict(protected_namespaces=("settings_",))

    @classmethod
    def from_input_word(
        cls,
        input_str: str,
        translated_word: str | None = None,
        deck_name: str = settings.deck_name,
        model_name: str = settings.model_name,
    ) -> "KankiInput":
        """Model the kanki input based on the given word.

        Args:
            input_str (str): A string of the front word.
            translated_word (str, optional): Back word of the Anki note. Defaults to None.
            deck_name (str, optional): The deck name that the created note will be sent. Defaults to settings.deck_name.
            model_name (str, optional): The model name that will be used to format the created note. Defaults to settings.model_name.

        Returns:
            KankiInput: _description_

        """
        # Create the Anki note model
        if translated_word is None:
            # If the translated word is not provided, translate the word
            # Create a translator
            translator_settings = TranslatorInput(
                source=settings.using_lang,
                target=settings.translate_lang,
                ai=settings.ai,
            )
            translator = TranslationTool(translator_settings)

            # Execute translation
            translated_word = translator.translate(input_str)

        # If the translated word is provided
        anki_note = AnkiNote(
            deckName=deck_name,
            modelName=model_name,
            front=input_str,
            back=translated_word,
        )

        anki_notes_list = [anki_note]
        return cls(anki_notes=anki_notes_list)

    @classmethod
    def from_txt(
        cls,
        data_fname: Path = settings.dir_path / "data" / "example.txt",
        deck_name: str = settings.deck_name,
        model_name: str = settings.model_name,
    ) -> "KankiInput":
        """Create a list of Anki note based on a file which contains multiple words.

        Args:
            data_fname (Path, optional): The input file path. Defaults to settings.dir_path/"data"/"example.txt".
            deck_name (str, optional): The deck name that the created note will be sent. Defaults to settings.deck_name.
            model_name (str, optional): The model name that will be used to format the created note. Defaults to settings.model_name.

        Returns:
            KankiInput: _description_

        """
        # Read the vocabularies from a given text file
        with data_fname.open("r") as f:
            rows = f.read().split("\n")

        # Allowing reading translated words if it is provided
        voc_list = []
        translated_list = []
        for n, row in enumerate(rows):
            split_row = row.split(",")
            if len(split_row) == 2:
                voc_list.append(split_row[0])
                translated_list.append(split_row[1])
            elif len(split_row) == 1:
                voc_list.append(split_row[0])
                translated_list.append(None)
            else:
                raise ValueError(f"Format of input file is not available at line {n + 1}: {row}")

        # Create a translator for translating the word
        translator_settings = TranslatorInput(
            source=settings.using_lang,
            target=settings.translate_lang,
            ai=settings.ai,
        )
        translator = TranslationTool(translator_settings)

        # Create anki notes one by one
        anki_notes_list = []
        for word, translated in zip(voc_list, translated_list, strict=False):
            # If the word is not empty, create an Anki note
            try:
                # Validate the read word first.
                # It the word is not korean, raising errors
                anki_note = AnkiNote(
                    deckName=deck_name,
                    modelName=model_name,
                    front=word,
                )

                # Create the back side (translation) of the Ankinote
                if not translated:
                    # Translate the word into japanese if translated word is not provided
                    translated = translator.translate(word)

                anki_note.back = translated

                # Append the anki note into a list
                anki_notes_list.append(anki_note)
            except Exception as e:
                # If the word is not valid, skip it
                logging.warning(f"Error at line {n + 1}: {word} - {e}; skipping...")
                continue

        return cls(anki_notes=anki_notes_list)
