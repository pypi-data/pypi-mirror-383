from wizlib.command import WizCommand
from wizlib.parser import WizParser


class KwarkCommand(WizCommand):

    default = 'null'

    @classmethod
    def add_args(cls, parser: WizParser):
        super().add_args(parser)
        parser.add_argument('--api-key', '-k')

    def handle_vals(self):
        super().handle_vals()
        if not self.provided('api_key'):  # Fixed: use 'api_key' not 'api-key'
            if key := self.app.config.get('kwark-api-anthropic-key'):
                self.api_key = key


class PromptBasedCommand(KwarkCommand):
    """Base class for commands that use AI with a prompt template."""

    # Set to True if command requires non-empty input
    require_input = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from kwark.util import load_prompt
        self.prompt = load_prompt(self.name)

    @KwarkCommand.wrap
    def execute(self):
        from kwark.ai import AI

        input_text = self.app.stream.text

        # Validate input if required
        if self.require_input and not input_text.strip():
            self.status = "Error: No input text provided"
            return ""

        # Format prompt and query AI
        formatted_prompt = self.prompt.format(text=input_text)
        response = AI(self.api_key).query(formatted_prompt).strip()

        # Set status message
        self.status = getattr(
            self, 'success_message', f"Generated {self.name} " +
            f"from {self.get_input_type()}")

        return response

    def get_input_type(self):
        """Override this to customize the input type in status messages."""
        return "input text"


class NullCommand(KwarkCommand):

    name = 'null'
