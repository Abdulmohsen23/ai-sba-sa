# translation/management/commands/register_translation_models.py
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import torch
import whisper

class Command(BaseCommand):
    help = 'Downloads and registers translation models for offline use'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting translation model registration...'))
        
        # Check for CUDA
        self.stdout.write('Checking for CUDA...')
        if torch.cuda.is_available():
            self.stdout.write(self.style.SUCCESS(f'CUDA available: {torch.cuda.get_device_name(0)}'))
        else:
            self.stdout.write(self.style.WARNING('CUDA not available, using CPU (slower)'))
        
        # Register Whisper model
        self.stdout.write('Downloading Whisper large-v2 model...')
        try:
            whisper.load_model("large-v2")
            self.stdout.write(self.style.SUCCESS('✓ Whisper model downloaded successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error downloading Whisper model: {e}'))
        
        # Register NLLB model
        self.stdout.write('Downloading NLLB-200 translation model...')
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            
            model_name = "facebook/nllb-200-1.3B"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            translator_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            self.stdout.write(self.style.SUCCESS('✓ NLLB-200 model downloaded successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error downloading translation model: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Models registered successfully!'))