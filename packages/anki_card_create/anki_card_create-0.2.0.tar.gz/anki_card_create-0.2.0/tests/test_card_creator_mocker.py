from anki_card_create.card_creator import CardCreator
from anki_card_create.models.kanki_input import KankiInput


def test_add_note_to_anki(setup_anki_mock, global_data):
    # Assuming 'add_note_to_anki' is a function in your module that makes the post request
    kanki_input = KankiInput.from_input_word(
        input_str="죄송합니다",
        deck_name=global_data["deck_name"],
        model_name=global_data["model_name"],
    )

    # Call the function that makes the API request
    card_creator = CardCreator()
    response_list = card_creator.send_notes(kanki_input=kanki_input, audio=False)

    # Check that the response is as expected
    # assert response.json() == expected_response
    assert response_list[0].status_code == 200
