from django.core.management.base import BaseCommand
from askme.models import LLMModel


class Command(BaseCommand):
    help = 'Register or update LLM models'

    def handle(self, *args, **options):
        # Define the initial models
        initial_models = [
            {
                'name': 'Claude 3.7 Sonnet',
                'provider': 'Anthropic',
                'model_id': 'claude-3-7-sonnet',
                'description': 'Claude 3.7 Sonnet is excellent at complex reasoning, creative writing, and detailed explanations.',
                'icon': 'chat-square-text',
            },
            {
                'name': 'GPT-4o',
                'provider': 'OpenAI',
                'model_id': 'gpt-4o',
                'description': 'GPT-4o is a powerful model for a wide range of tasks including creative content, code generation, and problem-solving.',
                'icon': 'cpu',
            },
            # {
            #     'name': 'DeepSeek Coder',
            #     'provider': 'DeepSeek',
            #     'model_id': 'deepseek-coder',
            #     'description': 'DeepSeek Coder excels at understanding and generating code across multiple programming languages.',
            #     'icon': 'code-square',
            # },
            {
                'name': 'DeepSeek Chat',
                'provider': 'DeepSeek',
                'model_id': 'deepseek-chat',
                'description': 'DeepSeek Chat provides natural conversational abilities with strong knowledge across various domains.',
                'icon': 'chat',
            },
            {
                'name': 'Test Model',
                'provider': 'Mock',
                'model_id': 'mock-model',
                'description': 'A test model that doesn\'t require API keys. Use this for development and testing.',
                'icon': 'activity',
            },
        ]
        
        # Register each model
        for model_data in initial_models:
            # Check if model already exists
            model, created = LLMModel.objects.update_or_create(
                name=model_data['name'],
                provider=model_data['provider'],
                defaults={
                    'model_id': model_data['model_id'],
                    'description': model_data['description'],
                    'icon': model_data.get('icon', 'chat-dots'),
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created LLM model: {model.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated LLM model: {model.name}'))