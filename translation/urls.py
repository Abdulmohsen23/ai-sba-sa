from django.urls import path
from . import views

app_name = 'translation'

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.project_list, name='list'),
    path('projects/<int:pk>/', views.project_detail, name='detail'),
    path('projects/<int:pk>/editor/', views.subtitle_editor, name='editor'),
    path('projects/create/', views.project_create, name='create'),
    path('projects/<int:pk>/export/', views.export_video, name='export_video'),
    path('projects/<int:pk>/download-video/', views.download_video_with_subtitles, name='download_video'),
    path('api/projects/<int:pk>/save-all-subtitles/', views.api_save_all_subtitles, name='api_save_all_subtitles'),
    path('projects/<int:pk>/direct-download/', views.direct_download_video, name='direct_download'),
    
    # API endpoints for the subtitle editor
    path('api/projects/<int:pk>/subtitles/', views.api_subtitle_list, name='api_subtitle_list'),
    path('api/subtitles/<int:pk>/update/', views.api_subtitle_update, name='api_subtitle_update'),
    path('api/projects/<int:pk>/download/<str:output_type>/', views.download_output, name='download'),
    # Add this line to urlpatterns
path('api/projects/<int:pk>/upload-image/', views.upload_image_overlay, name='upload_image'),
    
]