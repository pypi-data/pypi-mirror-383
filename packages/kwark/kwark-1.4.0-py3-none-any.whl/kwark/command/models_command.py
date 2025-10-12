import yaml
from kwark.command import KwarkCommand
from kwark.ai import AI


class ModelsCommand(KwarkCommand):
    """List available Anthropic AI models."""

    name = 'models'

    @KwarkCommand.wrap
    def execute(self):
        ai = AI(self.api_key)
        models = ai.available_models

        if not models:
            self.status = "Retrieved available models (none found)"
            return yaml.dump([], default_flow_style=False)

        # Create YAML output as array of hashes
        yaml_models = [
            {
                'id': model['id'],
                'display_name': model.get('display_name', model['id']),
                'created_at': model.get('created_at', 'Unknown')
            }
            for model in models
        ]

        self.status = "Retrieved available models"
        return yaml.dump(yaml_models, default_flow_style=False)
