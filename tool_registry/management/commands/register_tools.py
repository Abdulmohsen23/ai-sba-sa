from django.core.management.base import BaseCommand
from django.utils.text import slugify
from tool_registry.models import AITool


class Command(BaseCommand):
    help = 'Register or update AI tools in the platform'

    def handle(self, *args, **options):
        # Define the initial tools
        initial_tools = [
            {
                'name': 'Video Transcription',
                'description': 'Transcribe videos to text with AI. Supports multiple languages and generates downloadable documents.',
                'icon': 'camera-video',  # Bootstrap icon
                'url_name': 'transcription:home',
                'order': 1,
            },
            {
                'name': 'Ask Me',
                'description': 'Ask questions to various AI models. Upload files or just type your query to get intelligent responses.',
                'icon': 'chat-dots',  # Bootstrap icon
                'url_name': 'askme:home',
                'order': 2,
            },
            {
                'name': 'Program Ideation',
                'description': 'Create TV program ideas for Saudi Broadcasting Authority using AI assistance.',
                'icon': 'lightbulb',  # Bootstrap icon
                'url_name': 'program_ideation:home',
                'order': 3,
            }
        ]
        
        # Register each tool
        for tool_data in initial_tools:
            slug = slugify(tool_data['name'])
            
            # Check if tool already exists
            tool, created = AITool.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': tool_data['name'],
                    'description': tool_data['description'],
                    'icon': tool_data['icon'],
                    'url_name': tool_data['url_name'],
                    'order': tool_data['order'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created tool: {tool.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated tool: {tool.name}'))