from django.db import models
from django.conf import settings
from core.models import BaseModel
from core.utils import get_file_upload_path


def media_upload_path(instance, filename):
    """Generate upload path for media files."""
    return get_file_upload_path(instance, filename)


class LLMModel(BaseModel):
    """Model for available LLM models."""
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=50)
    model_id = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="chat-dots")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.provider})"


class Conversation(BaseModel):
    """Model for conversations (threads of questions and responses)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    llm_model = models.ForeignKey(LLMModel, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title


class Question(BaseModel):
    """Model for user questions."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='questions')
    content = models.TextField()
    file = models.FileField(upload_to=media_upload_path, null=True, blank=True)
    file_type = models.CharField(max_length=20, null=True, blank=True)
    llm_model = models.ForeignKey(LLMModel, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(null=True, blank=True)
    sequence = models.PositiveIntegerField(default=0)  # Order in conversation
    
    class Meta:
        ordering = ['sequence']
    
    def __str__(self):
        return f"{self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        # Set sequence if not provided
        if not self.sequence and self.conversation_id:
            max_seq = Question.objects.filter(conversation=self.conversation).aggregate(models.Max('sequence'))['sequence__max'] or 0
            self.sequence = max_seq + 1
        super().save(*args, **kwargs)


class Response(BaseModel):
    """Model for LLM responses."""
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='response')
    content = models.TextField()
    processing_time = models.FloatField(null=True, blank=True, help_text="Processing time in seconds")
    sensitive_content_detected = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Response to: {self.question.content[:30]}..."