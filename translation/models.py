from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import BaseModel
from core.utils import get_file_upload_path

User = get_user_model()

class TranslationProject(BaseModel):
    """Model to store translation projects"""
    LANGUAGE_CHOICES = (
        ('ar', 'Arabic'),
        ('en', 'English'),
    )
    
    TRANSLATION_MODE_CHOICES = (
        ('same', 'Same Language'),
        ('translate', 'Translate'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='translation_projects')
    title = models.CharField(max_length=255)
    source_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    translation_mode = models.CharField(max_length=20, choices=TRANSLATION_MODE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    video_file = models.FileField(upload_to=get_file_upload_path)
    processing_time = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('translation:detail', kwargs={'pk': self.pk})
    
    class Meta:
        ordering = ['-created_at']

class Subtitle(BaseModel):
    """Model to store subtitle segments"""
    project = models.ForeignKey(TranslationProject, on_delete=models.CASCADE, related_name='subtitles')
    start_time = models.FloatField(help_text="Start time in seconds")
    end_time = models.FloatField(help_text="End time in seconds")
    original_text = models.TextField()
    translated_text = models.TextField(blank=True, null=True)
    sequence = models.IntegerField()
    speaker = models.CharField(max_length=100, blank=True, null=True)

    
    # Styling options
    font_family = models.CharField(max_length=100, default="Arial")
    font_size = models.IntegerField(default=16)
    font_color = models.CharField(max_length=20, default="#FFFFFF")
    background_color = models.CharField(max_length=20, default="#000000")
    background_opacity = models.FloatField(default=0.5)
    is_bold = models.BooleanField(default=False)
    is_italic = models.BooleanField(default=False)
    is_underline = models.BooleanField(default=False)
    alignment = models.CharField(max_length=10, default="center", 
                               choices=[('left', 'Left'), ('center', 'Center'), ('right', 'Right')])
    
    class Meta:
        ordering = ['sequence']
    
    def __str__(self):
        return f"Subtitle {self.sequence} ({self.start_time:.2f}s - {self.end_time:.2f}s)"

class TranslationOutput(BaseModel):
    """Model to store output files from translation process"""
    project = models.ForeignKey(TranslationProject, on_delete=models.CASCADE, related_name='outputs')
    
    OUTPUT_TYPE_CHOICES = (
        ('srt_original', 'SRT Original'),
        ('srt_translated', 'SRT Translated'),
        ('vtt_original', 'VTT Original'),
        ('vtt_translated', 'VTT Translated'),
        ('docx_original', 'DOCX Original'),
        ('docx_translated', 'DOCX Translated'),
        ('txt_original', 'TXT Original'),
        ('txt_translated', 'TXT Translated'),
    )
    
    output_type = models.CharField(max_length=20, choices=OUTPUT_TYPE_CHOICES)
    file = models.FileField(upload_to=get_file_upload_path)
    
    def __str__(self):
        return f"{self.get_output_type_display()} for {self.project.title}"