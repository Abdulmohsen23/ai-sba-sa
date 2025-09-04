from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.postgres.fields import JSONField
from core.models import BaseModel
from core.utils import get_file_upload_path


def video_upload_path(instance, filename):
    """Generate upload path for video files."""
    return get_file_upload_path(instance, filename)


def subtitle_file_path(instance, filename):
    """Generate upload path for subtitle files."""
    return f"subtitles/{timezone.now().strftime('%Y/%m/%d')}/{filename}"


def processed_video_path(instance, filename):
    """Generate upload path for processed videos."""
    return f"processed_videos/{timezone.now().strftime('%Y/%m/%d')}/{filename}"


class VideoFile(BaseModel):
    """Model for uploaded video files."""
    RETENTION_CHOICES = [
        ('5days', 'Keep for 5 days'),
        ('delete', 'Delete now'),
    ]
    
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_files')
    file = models.FileField(upload_to=video_upload_path)
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    retention = models.CharField(max_length=10, choices=RETENTION_CHOICES, default='5days')
    delete_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    duration = models.FloatField(null=True, blank=True, help_text="Video duration in seconds")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.original_filename


class SubtitleProject(BaseModel):
    """Model for subtitle projects."""
    LANGUAGE_CHOICES = [
        ('ar', 'Arabic'),
        ('en', 'English'),
    ]
    
    SUBTITLE_MODE_CHOICES = [
        ('same', 'Same Language'),
        ('translate', 'Translated'),
    ]
    
    video = models.ForeignKey(VideoFile, on_delete=models.CASCADE, related_name='subtitle_projects')
    source_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    subtitle_mode = models.CharField(max_length=20, choices=SUBTITLE_MODE_CHOICES)
    target_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True, help_text="Processing time in minutes")
    
    # Subtitle files
    srt_file_arabic = models.FileField(upload_to=subtitle_file_path, null=True, blank=True)
    srt_file_english = models.FileField(upload_to=subtitle_file_path, null=True, blank=True)
    vtt_file_arabic = models.FileField(upload_to=subtitle_file_path, null=True, blank=True)
    vtt_file_english = models.FileField(upload_to=subtitle_file_path, null=True, blank=True)
    
    # Document files
    doc_file_arabic = models.FileField(upload_to=subtitle_file_path, null=True, blank=True)
    doc_file_english = models.FileField(upload_to=subtitle_file_path, null=True, blank=True)
    
    # Processed video with subtitles
    processed_video = models.FileField(upload_to=processed_video_path, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Subtitle Project for {self.video.original_filename}"


class SubtitleSegment(BaseModel):
    """Model for individual subtitle segments."""
    project = models.ForeignKey(SubtitleProject, on_delete=models.CASCADE, related_name='segments')
    segment_number = models.IntegerField()
    start_time = models.FloatField(help_text="Start time in seconds")
    end_time = models.FloatField(help_text="End time in seconds")
    original_text = models.TextField()
    translated_text = models.TextField(blank=True, null=True)
    edited_text = models.TextField(blank=True, null=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['segment_number']
        unique_together = ['project', 'segment_number']
    
    def get_display_text(self):
        """Get the text to display (edited if available, otherwise original)."""
        return self.edited_text if self.is_edited else self.original_text


class SubtitleStyle(BaseModel):
    """Model for subtitle styling settings."""
    project = models.OneToOneField(SubtitleProject, on_delete=models.CASCADE, related_name='style')
    
    # Font settings
    font_family = models.CharField(max_length=100, default='Arial')
    font_size = models.IntegerField(default=24, help_text="Font size in pixels")
    font_color = models.CharField(max_length=7, default='#FFFFFF', help_text="Hex color code")
    font_weight = models.CharField(max_length=20, default='normal', choices=[
        ('normal', 'Normal'),
        ('bold', 'Bold'),
    ])
    font_style = models.CharField(max_length=20, default='normal', choices=[
        ('normal', 'Normal'),
        ('italic', 'Italic'),
    ])
    text_align = models.CharField(max_length=20, default='center', choices=[
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    ])
    
    # Background settings
    background_color = models.CharField(max_length=7, default='#000000', help_text="Hex color code")
    background_opacity = models.FloatField(default=0.7, help_text="0 to 1")
    padding = models.IntegerField(default=10, help_text="Padding in pixels")
    border_radius = models.IntegerField(default=5, help_text="Border radius in pixels")
    
    # Position settings
    position_y = models.IntegerField(default=85, help_text="Vertical position as percentage from top")
    
    # Shadow settings
    text_shadow = models.BooleanField(default=True)
    shadow_color = models.CharField(max_length=7, default='#000000')
    shadow_blur = models.IntegerField(default=2)
    
    def get_css_style(self):
        """Generate CSS style string for subtitles."""
        return {
            'font-family': self.font_family,
            'font-size': f'{self.font_size}px',
            'color': self.font_color,
            'font-weight': self.font_weight,
            'font-style': self.font_style,
            'text-align': self.text_align,
            'background-color': f'{self.background_color}{int(self.background_opacity * 255):02x}',
            'padding': f'{self.padding}px',
            'border-radius': f'{self.border_radius}px',
            'position': 'absolute',
            'bottom': f'{100 - self.position_y}%',
            'text-shadow': f'0 0 {self.shadow_blur}px {self.shadow_color}' if self.text_shadow else 'none',
        }