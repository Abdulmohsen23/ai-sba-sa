"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Check if we're in build phase to avoid importing heavy dependencies
BUILD_PHASE = os.environ.get('BUILD_PHASE', 'false').lower() == 'true'

# Core URLs including program_ideation from the start
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Django auth URLs
    path('askme/', include('askme.urls', namespace='askme')),
    path('program-ideation/', include('program_ideation.urls', namespace='program_ideation')),  # Include from start
    path('', include('tool_registry.urls')),  # Include tool registry URLs for the dashboard
]

# Only exclude transcription and translation apps during build phase (they have heavier ML dependencies)
if not BUILD_PHASE:
    urlpatterns += [
        path('transcription/', include('transcription.urls', namespace='transcription')),
        path('translation/', include('translation.urls', namespace='translation')),
    ]

# Add debug toolbar URLs in development
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)