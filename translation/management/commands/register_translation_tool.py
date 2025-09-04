# translation/management/commands/register_translation_tool.py
from django.core.management.base import BaseCommand
from tool_registry.models import AITool

class Command(BaseCommand):
    help = 'Register the Translation tool with the tool registry'
    
    def handle(self, *args, **options):
        self.stdout.write('Registering Translation tool...')
        
        AITool.objects.update_or_create(
            slug='translation',
            defaults={
                'name': 'Translation & Subtitling',
                'description': 'Automatically generate and edit subtitles for videos, with translation between Arabic and English.',
                'icon': 'translate',
                'url_name': 'translation:home',
                'order': 3,
                'is_active': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Translation tool registered successfully!'))