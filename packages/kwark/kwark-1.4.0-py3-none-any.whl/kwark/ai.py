from datetime import datetime

from anthropic import Anthropic

from wizlib.ui import Emphasis


DEFAULT_MODEL = 'claude-sonnet-4-5-20250929'
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0
SYSTEM_PROMPT_TEMPLATE = """You are Kwark, a lightweight AI assistant that
performs specific tasks. You use the {model} model. Now is {now}.\n"""


class AI:

    def __init__(self, api_key=None, model=None):
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = Anthropic()
        self.available_models = self._fetch_available_models()
        self.model = DEFAULT_MODEL if model is None else model
        model_name = next((m['display_name'] for m in self.available_models
                           if m['id'] == self.model), None)
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            model=model_name, now=datetime.now())

    def _fetch_available_models(self):
        """Fetch list of available Anthropic models"""
        try:
            response = self.client.models.list()
            models = []
            for model in response:
                models.append({
                    'id': model.id,
                    'display_name': getattr(model, 'display_name', model.id),
                    'created_at': getattr(model, 'created_at', None),
                })
            return models
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    def _create_user_message(self, text):
        """Create a user message structure"""
        return {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }

    def _send_message(self, messages, model):
        """Send messages to API and return the message object"""
        model = model or self.model
        return self.client.messages.create(
            model=model,
            max_tokens=DEFAULT_MAX_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
            system=self.system_prompt,
            messages=messages)

    def query(self, text, model=None):
        """Send a one-time query, no tools"""
        messages = [self._create_user_message(text)]
        message = self._send_message(messages, model)
        return message.content[0].text

    def chat(self, ui, initial_message=None, model=None):
        """Interactive chat with conversation history using UI"""

        model = model or self.model
        messages = []

        # Handle initial message if provided
        if initial_message:
            messages.append(self._create_user_message(initial_message))

            # Stream initial message response
            response = ""
            with self.client.messages.stream(
                model=model,
                max_tokens=DEFAULT_MAX_TOKENS,
                temperature=DEFAULT_TEMPERATURE,
                system=self.system_prompt,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    ui.send(text, Emphasis.GENERAL, newline=False)
                    response += text

            messages.append({
                "role": "assistant",
                "content": response
            })

        # Chat loop
        while True:
            try:
                user_input = ui.get_text("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    ui.send("Goodbye!", Emphasis.INFO)
                    break

                messages.append(self._create_user_message(user_input))

                # Stream response
                ui.send("Assistant: ", Emphasis.GENERAL)
                response = ""
                with self.client.messages.stream(
                    model=model,
                    max_tokens=DEFAULT_MAX_TOKENS,
                    temperature=DEFAULT_TEMPERATURE,
                    system=self.system_prompt,
                    messages=messages
                ) as stream:
                    for text in stream.text_stream:
                        ui.send(text, Emphasis.GENERAL, newline=False)
                        response += text
                ui.send("\n")
                messages.append({
                    "role": "assistant",
                    "content": response
                })

            except KeyboardInterrupt:
                ui.send("Goodbye!", Emphasis.INFO)
                break
            except EOFError:
                ui.send("Goodbye!", Emphasis.INFO)
                break
