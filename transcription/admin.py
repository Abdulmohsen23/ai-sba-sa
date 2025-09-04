from django.contrib import admin
from .models import VideoFile


# class TranscriptionInline(admin.StackedInline):
#     model = Transcription
#     readonly_fields = ('created_at', 'updated_at')
#     extra = 0


# @admin.register(VideoFile)
# class VideoFileAdmin(admin.ModelAdmin):
#     list_display = ('id', 'original_filename', 'user', 'status', 'retention', 'created_at')
#     list_filter = ('status', 'retention', 'created_at')
#     search_fields = ('original_filename', 'user__username')
#     readonly_fields = ('created_at', 'updated_at')
#     inlines = [TranscriptionInline]
#     date_hierarchy = 'created_at'


# @admin.register(TranscriptionFeedback)
# class TranscriptionFeedbackAdmin(admin.ModelAdmin):
#     list_display = ('id', 'transcription', 'user', 'rating', 'created_at')
#     list_filter = ('rating', 'created_at')
#     search_fields = ('transcription__video__original_filename', 'user__username', 'comments')
#     readonly_fields = ('created_at', 'updated_at')