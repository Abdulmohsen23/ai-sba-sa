"""
URL configuration for config project.
"""
import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Check multiple ways to detect build phase
BUILD_PHASE = (
    os.environ.get('BUILD_PHASE', 'false').lower() == 'true' or
    os.environ.get('RAILWAY_ENVIRONMENT') == 'build' or
    'migrate' in os.sys.argv if hasattr(os, 'sys') else False
)

# Always include these core URLs
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('askme/', include('askme.urls', namespace='askme')),
    path('program-ideation/', include('program_ideation.urls', namespace='program_ideation')),
    path('', include('tool_registry.urls')),
]

# For now, NEVER include transcription and translation to avoid build errors
# TODO: Add these back after successful deployment with proper ML dependencies
"""
# Temporarily commented out - add back after successful basic deployment
if not BUILD_PHASE:
    urlpatterns += [
        path('transcription/', include('transcription.urls', namespace='transcription')),
        path('translation/', include('translation.urls', namespace='translation')),
    ]
"""

# Debug toolbar and media files
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)