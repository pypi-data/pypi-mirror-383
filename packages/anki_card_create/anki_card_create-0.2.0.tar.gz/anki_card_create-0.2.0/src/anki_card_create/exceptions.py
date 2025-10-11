from anki_card_create.models.response import AnkiSendMediaResponse


class MediaAdditionError(Exception):
    """Exception raised when adding media fails."""

    def __init__(self, response: AnkiSendMediaResponse, message="Failed to add media"):
        self.status_code = response.status_code
        message = response.error
        self.message = f"{message}. Status code: {self.status_code}"
        super().__init__(self.message)
