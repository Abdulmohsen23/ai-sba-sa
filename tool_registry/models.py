from django.db import models
from django.urls import reverse
from core.models import BaseModel


class AITool(BaseModel):
    """Model for registering AI tools in the platform."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Icon class name")
    url_name = models.CharField(max_length=100, help_text="URL name for the tool's main view")
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order on the dashboard")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """Get the URL for this tool."""
        try:
            return reverse(self.url_name)
        except:
            return '#'  # Fallback if the URL doesn't exist


class ToolUsageStatistics(BaseModel):
    """Model to track usage statistics for each tool."""
    tool = models.ForeignKey(AITool, on_delete=models.CASCADE, related_name='usage_statistics')
    date = models.DateField()
    usage_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    average_processing_time = models.FloatField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Tool Usage Statistics"
        unique_together = ['tool', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.tool.name} - {self.date}"