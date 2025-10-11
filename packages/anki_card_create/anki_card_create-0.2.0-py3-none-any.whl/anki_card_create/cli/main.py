import argparse
import logging
from pathlib import Path

from anki_card_create.card_creator import CardCreator
from anki_card_create.config import settings
from anki_card_create.models.kanki_input import KankiInput

logger = logging.getLogger(__name__)


def get_args_parser(known=False) -> argparse.Namespace:
    """Get the arguments parser for the command line interface."""
    parser = argparse.ArgumentParser("Create Anki flash cards.")
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-f",
        "--file",
        help="File containing text for Anki cards.",
    )
    group.add_argument(
        "-w",
        "--word",
        help="The vocabulary for Anki cards.",
    )

    parser.add_argument(
        "-d",
        "--deck_name",
        default=settings.deck_name,
        help="Name of the Anki deck to which the cards will be added.",
    )

    parser.add_argument(
        "-m",
        "--model_name",
        default=settings.model_name,
        help="Name of the Anki card model to which the cards will be added.",
    )

    return parser.parse_known_args()[0] if known else parser.parse_args()


def main() -> None:
    """Create Anki flash cards from the input word or file."""
    args = get_args_parser(known=True)
    logger.info(f"deck name: {args.deck_name}; card model: {args.model_name}")

    # Create notes according to the input word
    if args.file:
        kanki_input = KankiInput.from_txt(
            data_fname=Path() / args.file,
            deck_name=args.deck_name,
            model_name=args.model_name,
        )
    else:
        kanki_input = KankiInput.from_input_word(
            input_str=args.word,
            deck_name=args.deck_name,
            model_name=args.model_name,
        )

    # Send the notes to Anki with the audio
    card_creator = CardCreator()
    card_creator.send_notes(kanki_input=kanki_input, audio=True)


if __name__ == "__main__":
    main()
