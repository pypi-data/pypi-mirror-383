import logging
import sys
from argparse import Namespace

import pytest

from anki_card_create.cli.main import get_args_parser
from anki_card_create.config import settings

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "args, expected",
    [
        pytest.param(
            ["--file", "test.txt"],
            Namespace(
                file="test.txt",
                word=None,
                deck_name=settings.deck_name,
                model_name=settings.model_name,
            ),
        ),
        pytest.param(
            ["--word", "안녕하세요"],
            Namespace(
                file=None,
                word="안녕하세요",
                deck_name=settings.deck_name,
                model_name=settings.model_name,
            ),
        ),
        pytest.param(
            ["--file", "test.txt", "--deck_name", "test"],
            Namespace(
                file="test.txt",
                word=None,
                deck_name="test",
                model_name=settings.model_name,
            ),
        ),
        pytest.param(
            ["--file", "test.txt", "--model_name", "TestModel"],
            Namespace(
                file="test.txt",
                word=None,
                deck_name=settings.deck_name,
                model_name="TestModel",
            ),
        ),
    ],
)
def test_get_args_parser(args, expected, monkeypatch):
    # Simulate command-line arguments
    monkeypatch.setattr(sys, "argv", ["prog"] + args)

    assert get_args_parser(known=True) == expected


# def test_main_word(monkeypatch, global_data, setup_anki_mock):
#     test_args = [
#         "prog",
#         "--w",
#         "죄송합니다",
#         "--deck_name",
#         global_data["deck_name"],
#         "--model_name",
#         global_data["model_name"],
#     ]

#     # Mimic sys.argv
#     # sys.argv[0] would be "죄송합니다" ... vice versa.
#     monkeypatch.setattr(sys, "argv", test_args)

#     # Execute the main function
#     main()


# def test_main_file(monkeypatch, create_test_data, global_data, setup_anki_mock):
#     input_file = global_data["dir_path"] / global_data["test_file_name"]
#     input_file = input_file.__str__()

#     test_args = [
#         "prog",
#         "--f",
#         input_file,
#         "--deck_name",
#         global_data["deck_name"],
#         "--model_name",
#         global_data["model_name"],
#     ]
#     # Mimic sys.argv
#     monkeypatch.setattr(sys, "argv", test_args)

#     # Execute the main function
#     main()
