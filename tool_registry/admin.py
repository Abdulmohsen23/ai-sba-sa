from django.contrib import admin
from .models import AITool, ToolUsageStatistics


@admin.register(AITool)
class AIToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'url_name', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ToolUsageStatistics)
class ToolUsageStatisticsAdmin(admin.ModelAdmin):
    list_display = ('tool', 'date', 'usage_count', 'success_count', 'error_count', 'average_processing_time')
    list_filter = ('tool', 'date')
    date_hierarchy = 'date'