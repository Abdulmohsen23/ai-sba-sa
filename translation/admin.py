from django.contrib import admin
from .models import TranslationProject, Subtitle, TranslationOutput

class SubtitleInline(admin.TabularInline):
    model = Subtitle
    fields = ('sequence', 'start_time', 'end_time', 'original_text')
    readonly_fields = ('sequence', 'start_time', 'end_time')
    extra = 0
    
class OutputInline(admin.TabularInline):
    model = TranslationOutput
    fields = ('output_type', 'file')
    readonly_fields = ('output_type', 'file')
    extra = 0

@admin.register(TranslationProject)
class TranslationProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'source_language', 'translation_mode', 'status', 'created_at')
    list_filter = ('status', 'source_language', 'translation_mode', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('status', 'processing_time', 'error_message')
    inlines = [SubtitleInline, OutputInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Add subtitle count annotation
        return qs.annotate(subtitle_count=models.Count('subtitles'))
    
    def subtitle_count(self, obj):
        return obj.subtitle_count
    subtitle_count.admin_order_field = 'subtitle_count'
    subtitle_count.short_description = 'Subtitle Count'

@admin.register(Subtitle)
class SubtitleAdmin(admin.ModelAdmin):
    list_display = ('project', 'sequence', 'start_time', 'end_time', 'short_text')
    list_filter = ('project__title',)
    search_fields = ('original_text', 'translated_text')
    
    def short_text(self, obj):
        if len(obj.original_text) > 50:
            return f"{obj.original_text[:50]}..."
        return obj.original_text
    short_text.short_description = 'Text'