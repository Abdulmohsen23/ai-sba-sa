from django.urls import path
from . import views

app_name = 'transcription'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('upload/', views.upload_video, name='upload'),
    path('editor/<int:project_id>/', views.subtitle_editor, name='editor'),
    
    # API endpoints for editor
    path('api/project/<int:project_id>/segment/<int:segment_id>/update/', 
         views.update_segment, name='update_segment'),
    path('api/project/<int:project_id>/segment/add/', 
         views.add_segment, name='add_segment'),
    path('api/project/<int:project_id>/segment/<int:segment_id>/delete/', 
         views.delete_segment, name='delete_segment'),
    path('api/project/<int:project_id>/style/update/', 
         views.update_style, name='update_style'),
    
    # Export endpoints
    path('export/<int:project_id>/<str:format_type>/', 
         views.export_subtitles, name='export_subtitles'),
    path('export/<int:project_id>/video/', 
         views.export_video, name='export_video'),
    path('download/<int:project_id>/document/<str:language>/', 
         views.download_document, name='download_document'),
    
    # Status check
    path('api/project/<int:project_id>/status/', 
         views.check_processing_status, name='check_processing_status'),
    
    # Legacy support for old transcription system
    path('list/', views.video_list, name='list'),
    path('<int:video_id>/', views.video_detail, name='detail'),
    path('<int:video_id>/status/', views.check_status, name='check_status'),
    path('<int:video_id>/retention/', views.update_retention, name='update_retention'),
]