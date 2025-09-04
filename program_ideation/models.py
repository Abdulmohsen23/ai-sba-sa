from django.db import models
from django.conf import settings
from core.models import BaseModel


class ProgramIdea(BaseModel):
    """Model for program ideas."""
    LANGUAGE_CHOICES = [
        ('ar', 'Arabic'),
        ('en', 'English'),
    ]
    
    IDEA_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='ar')
    has_specific_idea = models.BooleanField(default=True)
    has_initial_concept = models.BooleanField(null=True, blank=True)
    initial_concept = models.TextField(blank=True, null=True)
    
    # Program details
    program_name = models.CharField(max_length=255, blank=True, null=True)
    general_idea = models.TextField(blank=True, null=True)
    target_audience = models.TextField(blank=True, null=True)
    program_objectives = models.TextField(blank=True, null=True)
    program_type = models.CharField(max_length=255, blank=True, null=True)
    program_duration = models.CharField(max_length=255, blank=True, null=True)
    episode_count = models.CharField(max_length=50, blank=True, null=True)
    filming_location = models.TextField(blank=True, null=True)
    
    # Process tracking
    current_step = models.CharField(max_length=50, default='start')
    status = models.CharField(max_length=20, choices=IDEA_STATUS_CHOICES, default='draft')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.program_name or f"Program Idea #{self.id}"
    
    def get_missing_fields(self):
        """Return a list of missing required fields."""
        required_fields = [
            'program_name', 'general_idea', 'target_audience', 
            'program_objectives', 'program_type', 'program_duration',
            'episode_count', 'filming_location'
        ]
        
        missing = []
        for field in required_fields:
            if not getattr(self, field):
                missing.append(field)
        
        return missing
    
    def is_complete(self):
        """Check if all required fields are filled."""
        return len(self.get_missing_fields()) == 0


class IdeaResponse(BaseModel):
    """Model for LLM responses during idea development."""
    RESPONSE_TYPE_CHOICES = [
        ('suggestions', 'Suggestions'),
        ('discussion_questions', 'Discussion Questions'),
        ('missing_data', 'Missing Data Proposals'),
        ('program_format', 'Program Format'),
        ('program_script', 'Program Script'),
        ('visual_materials', 'Visual Materials'),
    ]
    
    idea = models.ForeignKey(ProgramIdea, on_delete=models.CASCADE, related_name='responses')
    response_type = models.CharField(max_length=50, choices=RESPONSE_TYPE_CHOICES)
    content = models.TextField()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_response_type_display()} for {self.idea}"
    


# Add this to program_ideation/models.py

# UPDATE the IdeaNote model:
class IdeaNote(BaseModel):
    """Enhanced model for notes on program idea fields."""
    FIELD_CHOICES = [
        ('program_name', 'Program Name'),
        ('general_idea', 'General Idea'),
        ('target_audience', 'Target Audience'),
        ('program_objectives', 'Program Objectives'),
        ('program_type', 'Program Type'),
        ('program_duration', 'Program Duration'),
        ('episode_count', 'Episode Count'),
        ('filming_location', 'Filming Location'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    NOTE_TYPE_CHOICES = [
        ('enhancement', 'Enhancement'),
        ('question', 'Question'),
        ('concern', 'Concern'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    idea = models.ForeignKey(ProgramIdea, on_delete=models.CASCADE, related_name='notes')
    
    # Keep single field for backward compatibility
    field_name = models.CharField(max_length=50, choices=FIELD_CHOICES, blank=True, null=True)
    
    # New fields for enhanced functionality
    note_type = models.CharField(max_length=20, choices=NOTE_TYPE_CHOICES, default='enhancement')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    note_content = models.TextField(help_text="Note or request for enhancement")
    response_content = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_applied = models.BooleanField(default=False, help_text="Whether the suggestion has been applied")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.idea} - {self.created_at}"
    
    def get_field_label_arabic(self):
        """Return Arabic label for the field."""
        labels = {
            'program_name': 'اسم البرنامج',
            'general_idea': 'الفكرة العامة',
            'target_audience': 'الجمهور المستهدف',
            'program_objectives': 'أهداف البرنامج',
            'program_type': 'نوع البرنامج',
            'program_duration': 'مدة البرنامج',
            'episode_count': 'عدد الحلقات',
            'filming_location': 'موقع أو أسلوب التصوير'
        }
        return labels.get(self.field_name, self.field_name)
    
    def get_all_field_names(self):
        """Get all field names associated with this note."""
        field_names = []
        if self.note_fields.exists():
            field_names.extend([f.field_name for f in self.note_fields.all()])
        elif self.field_name:
            field_names.append(self.field_name)
        return field_names
    

# ADD these new models:
class NoteField(BaseModel):
    """Represents a field associated with a note for multi-field support."""
    note = models.ForeignKey(IdeaNote, on_delete=models.CASCADE, related_name='note_fields')
    field_name = models.CharField(max_length=50)
    current_content = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['note', 'field_name']
    
    def __str__(self):
        return f"{self.field_name} for Note #{self.note.id}"
    
    def get_field_name_display(self):
        """Get display name for the field."""
        display_names = {
            'program_name': 'Program Name',
            'general_idea': 'General Idea',
            'target_audience': 'Target Audience',
            'program_objectives': 'Program Objectives',
            'program_type': 'Program Type',
            'program_duration': 'Program Duration',
            'episode_count': 'Episode Count',
            'filming_location': 'Filming Location',
        }
        return display_names.get(self.field_name, self.field_name)
    
    def get_field_label_arabic(self):
        """Get Arabic label for the field."""
        arabic_labels = {
            'program_name': 'اسم البرنامج',
            'general_idea': 'الفكرة العامة',
            'target_audience': 'الجمهور المستهدف',
            'program_objectives': 'أهداف البرنامج',
            'program_type': 'نوع البرنامج',
            'program_duration': 'مدة البرنامج',
            'episode_count': 'عدد الحلقات',
            'filming_location': 'موقع التصوير',
        }
        return arabic_labels.get(self.field_name, self.field_name)


class AppliedSuggestion(BaseModel):
    """Track which suggestions have been applied."""
    note = models.ForeignKey(IdeaNote, on_delete=models.CASCADE, related_name='applied_suggestions')
    field_name = models.CharField(max_length=50)
    suggestion_text = models.TextField()
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"Applied suggestion for {self.field_name} - {self.applied_at}"