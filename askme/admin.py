from django.contrib import admin
from .models import LLMModel, Question, Response


class ResponseInline(admin.StackedInline):
    model = Response
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'model_id', 'is_active')
    list_filter = ('provider', 'is_active')
    search_fields = ('name', 'model_id', 'description')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'truncated_content', 'user', 'llm_model', 'status', 'created_at')
    list_filter = ('status', 'llm_model', 'created_at')
    search_fields = ('content', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ResponseInline]
    date_hierarchy = 'created_at'
    
    def truncated_content(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    truncated_content.short_description = 'Question'


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'processing_time', 'sensitive_content_detected', 'created_at')
    list_filter = ('sensitive_content_detected', 'created_at')
    search_fields = ('content', 'question__content')
    readonly_fields = ('created_at', 'updated_at')