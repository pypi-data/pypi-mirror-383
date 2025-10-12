from kwark.command import KwarkCommand
from kwark.ai import AI


class ChatCommand(KwarkCommand):
    """Simple chat command to interact with AI.
    Takes input text and returns an AI response."""

    name = 'chat'

    @KwarkCommand.wrap
    def execute(self):
        initial_message = self.app.stream.text.strip() or None

        ai = AI(self.api_key)
        ai.chat(self.app.ui, initial_message=initial_message)

        self.status = "Chat session completed"
