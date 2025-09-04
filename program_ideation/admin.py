from django.contrib import admin
from django.utils.html import format_html
from .models import ProgramIdea, IdeaResponse , IdeaNote


class IdeaResponseInline(admin.TabularInline):
    """Inline admin for idea responses."""
    model = IdeaResponse
    extra = 0
    fields = ('response_type', 'content_preview', 'created_at')
    readonly_fields = ('content_preview', 'created_at')
    can_delete = False
    max_num = 0  # Don't allow adding new responses through admin
    
    def content_preview(self, obj):
        """Show a preview of the response content."""
        if obj.content:
            return obj.content[:150] + '...' if len(obj.content) > 150 else obj.content
        return "-"
    content_preview.short_description = "Content Preview"


@admin.register(ProgramIdea)
class ProgramIdeaAdmin(admin.ModelAdmin):
    """Admin for program ideas."""
    list_display = ('id', 'program_name_display', 'user', 'language', 'status', 
                    'current_step', 'has_specific_idea', 'created_at', 'updated_at')
    list_filter = ('status', 'language', 'current_step', 'has_specific_idea', 'created_at')
    search_fields = ('program_name', 'general_idea', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [IdeaResponseInline]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'language')
        }),
        ('Idea State', {
            'fields': ('status', 'current_step', 'has_specific_idea', 'has_initial_concept', 'initial_concept')
        }),
        ('Program Details', {
            'fields': ('program_name', 'general_idea', 'target_audience', 'program_objectives',
                      'program_type', 'program_duration', 'episode_count', 'filming_location')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def program_name_display(self, obj):
        """Display program name or placeholder if not available."""
        if obj.program_name:
            return obj.program_name
        return format_html('<span style="color: #999;">Untitled Idea #{}</span>', obj.id)
    program_name_display.short_description = "Program Name"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for user."""
        return super().get_queryset(request).select_related('user')


@admin.register(IdeaResponse)
class IdeaResponseAdmin(admin.ModelAdmin):
    """Admin for idea responses."""
    list_display = ('id', 'get_program_name', 'response_type', 'content_preview', 'created_at')
    list_filter = ('response_type', 'created_at')
    search_fields = ('idea__program_name', 'content', 'idea__user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Response Information', {
            'fields': ('idea', 'response_type')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """Show a preview of the response content."""
        if obj.content:
            return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return "-"
    content_preview.short_description = "Content Preview"
    
    def get_program_name(self, obj):
        """Get the program name associated with this response."""
        if obj.idea and obj.idea.program_name:
            return obj.idea.program_name
        return f"Idea #{obj.idea_id}" if obj.idea_id else "-"
    get_program_name.short_description = "Program"
    get_program_name.admin_order_field = 'idea__program_name'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for idea and user."""
        return super().get_queryset(request).select_related('idea', 'idea__user')
    

# Add this to program_ideation/admin.py

@admin.register(IdeaNote)
class IdeaNoteAdmin(admin.ModelAdmin):
    """Admin for idea notes."""
    list_display = ('id', 'get_program_name', 'get_field_display', 'note_preview', 
                    'status', 'is_applied', 'created_at')
    list_filter = ('status', 'is_applied', 'field_name', 'created_at')
    search_fields = ('note_content', 'response_content', 'idea__program_name', 'idea__user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Note Information', {
            'fields': ('idea', 'field_name', 'status', 'is_applied')
        }),
        ('Content', {
            'fields': ('note_content', 'response_content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def note_preview(self, obj):
        """Show a preview of the note content."""
        if obj.note_content:
            return obj.note_content[:100] + '...' if len(obj.note_content) > 100 else obj.note_content
        return "-"
    note_preview.short_description = "Note Preview"
    
    def get_program_name(self, obj):
        """Get the program name associated with this note."""
        if obj.idea and obj.idea.program_name:
            return obj.idea.program_name
        return f"Idea #{obj.idea_id}" if obj.idea_id else "-"
    get_program_name.short_description = "Program"
    get_program_name.admin_order_field = 'idea__program_name'
    
    def get_field_display(self, obj):
        """Show the display name of the field."""
        return obj.get_field_name_display()
    get_field_display.short_description = "Field"
    get_field_display.admin_order_field = 'field_name'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for idea and user."""
        return super().get_queryset(request).select_related('idea', 'idea__user')