from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import models
from .models import VideoFile, SubtitleProject, SubtitleSegment, SubtitleStyle
from .forms import VideoUploadForm
from .processing_service import SubtitleProcessor
from .subtitle_services import EnhancedSubtitleService
from core.utils import log_user_activity
import json
import os
import threading
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


@login_required
def home(request):
    """Transcription tool home page."""
    recent_projects = SubtitleProject.objects.filter(
        video__user=request.user
    ).select_related('video').order_by('-created_at')[:5]
    
    context = {
        'title': 'Subtitle Generator & Editor',
        'recent_projects': recent_projects,
    }
    
    return render(request, 'transcription/home.html', context)


@login_required
def upload_video(request):
    """Handle video upload and subtitle settings."""
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create VideoFile instance
                video = VideoFile.objects.create(
                    user=request.user,
                    file=request.FILES['file'],
                    original_filename=request.FILES['file'].name,
                    file_size=request.FILES['file'].size,
                    status='uploaded',
                    retention=form.cleaned_data['retention']
                )
                
                # Get video duration
                service = EnhancedSubtitleService()
                video_path = video.file.path
                duration = service.get_video_duration(video_path)
                if duration:
                    video.duration = duration
                    video.save()
                
                # Create SubtitleProject
                project = SubtitleProject.objects.create(
                    video=video,
                    source_language=form.cleaned_data['source_language'],
                    subtitle_mode=form.cleaned_data['subtitle_mode'],
                    target_language=form.cleaned_data.get('target_language')
                )
                
                # Create default style
                SubtitleStyle.objects.create(project=project)
                
                # Log activity
                log_user_activity(
                    user=request.user,
                    tool_name='subtitle_generator',
                    action='upload_video',
                    details={
                        'video_id': video.id,
                        'project_id': project.id,
                        'filename': video.original_filename,
                        'source_language': project.source_language,
                        'subtitle_mode': project.subtitle_mode
                    },
                    request=request
                )
                
                # Process in background thread for better UX
                def process_in_background():
                    processor = SubtitleProcessor()
                    processor.process_subtitle_generation(project.id)
                
                thread = threading.Thread(target=process_in_background)
                thread.daemon = True
                thread.start()
                
                messages.success(request, 'Video uploaded successfully. Generating subtitles...')
                return redirect('transcription:editor', project_id=project.id)
                
            except Exception as e:
                logger.error(f"Error uploading video: {str(e)}")
                messages.error(request, f'Error uploading video: {str(e)}')
                return redirect('transcription:upload')
    else:
        form = VideoUploadForm()
    
    context = {
        'title': 'Upload Video for Subtitles',
        'form': form,
    }
    
    return render(request, 'transcription/upload.html', context)


@login_required
def subtitle_editor(request, project_id):
    """Subtitle editor interface."""
    project = get_object_or_404(
        SubtitleProject,
        id=project_id,
        video__user=request.user
    )
    
    # Get segments
    segments = project.segments.all().order_by('segment_number')
    
    # Get or create style
    style, created = SubtitleStyle.objects.get_or_create(project=project)
    
    context = {
        'title': f'Edit Subtitles - {project.video.original_filename}',
        'project': project,
        'video': project.video,
        'segments': segments,
        'style': style,
        'style_json': json.dumps({
            'font_family': style.font_family,
            'font_size': style.font_size,
            'font_color': style.font_color,
            'font_weight': style.font_weight,
            'font_style': style.font_style,
            'text_align': style.text_align,
            'background_color': style.background_color,
            'background_opacity': style.background_opacity,
            'padding': style.padding,
            'border_radius': style.border_radius,
            'position_y': style.position_y,
            'text_shadow': style.text_shadow,
            'shadow_color': style.shadow_color,
            'shadow_blur': style.shadow_blur,
        })
    }
    
    return render(request, 'transcription/editor.html', context)


@login_required
@require_POST
def update_segment(request, project_id, segment_id):
    """Update a subtitle segment via AJAX."""
    project = get_object_or_404(
        SubtitleProject,
        id=project_id,
        video__user=request.user
    )
    segment = get_object_or_404(
        SubtitleSegment,
        id=segment_id,
        project=project
    )
    
    try:
        data = json.loads(request.body)
        
        # Update segment text
        if 'text' in data:
            segment.edited_text = data['text']
            segment.is_edited = True
            segment.save()
        
        # Update timing if provided
        if 'start_time' in data:
            segment.start_time = float(data['start_time'])
        if 'end_time' in data:
            segment.end_time = float(data['end_time'])
        
        segment.save()
        
        return JsonResponse({
            'success': True,
            'segment': {
                'id': segment.id,
                'text': segment.get_display_text(),
                'start_time': segment.start_time,
                'end_time': segment.end_time,
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def update_style(request, project_id):
    """Update subtitle style settings via AJAX."""
    project = get_object_or_404(
        SubtitleProject,
        id=project_id,
        video__user=request.user
    )
    style = project.style
    
    try:
        data = json.loads(request.body)
        
        # Update style fields
        for field in ['font_family', 'font_size', 'font_color', 'font_weight',
                      'font_style', 'text_align', 'background_color',
                      'background_opacity', 'padding', 'border_radius',
                      'position_y', 'text_shadow', 'shadow_color', 'shadow_blur']:
            if field in data:
                setattr(style, field, data[field])
        
        style.save()
        
        return JsonResponse({
            'success': True,
            'css_style': style.get_css_style()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def add_segment(request, project_id):
    """Add a new subtitle segment."""
    project = get_object_or_404(
        SubtitleProject,
        id=project_id,
        video__user=request.user
    )
    
    try:
        data = json.loads(request.body)
        
        # Get the position for the new segment
        after_segment_id = data.get('after_segment_id')
        
        if after_segment_id:
            after_segment = SubtitleSegment.objects.get(
                id=after_segment_id,
                project=project
            )
            segment_number = after_segment.segment_number + 1
            
            # Shift all subsequent segments
            SubtitleSegment.objects.filter(
                project=project,
                segment_number__gte=segment_number
            ).update(segment_number=models.F('segment_number') + 1)
        else:
            # Add at the beginning
            segment_number = 1
            SubtitleSegment.objects.filter(
                project=project
            ).update(segment_number=models.F('segment_number') + 1)
        
        # Create new segment
        segment = SubtitleSegment.objects.create(
            project=project,
            segment_number=segment_number,
            start_time=float(data['start_time']),
            end_time=float(data['end_time']),
            original_text=data.get('text', ''),
            edited_text=data.get('text', ''),
            is_edited=True
        )
        
        return JsonResponse({
            'success': True,
            'segment': {
                'id': segment.id,
                'segment_number': segment.segment_number,
                'text': segment.get_display_text(),
                'start_time': segment.start_time,
                'end_time': segment.end_time,
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def delete_segment(request, project_id, segment_id):
    """Delete a subtitle segment."""
    project = get_object_or_404(
        SubtitleProject,
        id=project_id,
        video__user=request.user
    )
    segment = get_object_or_404(
        SubtitleSegment,
        id=segment_id,
        project=project
    )
    
    try:
        segment_number = segment.segment_number
        segment.delete()
        
        # Re-number subsequent segments
        SubtitleSegment.objects.filter(
            project=project,
            segment_number__gt=segment_number
        ).update(segment_number=models.F('segment_number') - 1)
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def export_subtitles(request, project_id, format_type):
    """Export subtitles in different formats."""
    project = get_object_or_404(
        SubtitleProject,
        id=project_id,
        video__user=request.user
    )
    
    segments = project.segments.all().order_by('segment_number')
    service = EnhancedSubtitleService()
    
    # Prepare segment data
    segment_data = []
    for segment in segments:
        segment_data.append({
            'start': segment.start_time,
            'end': segment.end_time,
            'original_text': segment.get_display_text(),
            'translated_text': segment.translated_text
        })
    
    if format_type == 'srt':
        content = service.create_srt_content(segment_data)
        content_type = 'text/plain'
        filename = f"{project.video.original_filename.rsplit('.', 1)[0]}.srt"
    elif format_type == 'vtt':
        content = service.create_vtt_content(segment_data)
        content_type = 'text/vtt'
        filename = f"{project.video.original_filename.rsplit('.', 1)[0]}.vtt"
    else:
        return JsonResponse({'error': 'Invalid format'}, status=400)
    
    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
@require_POST
def export_video(request, project_id):
    """Export video with burned-in subtitles (placeholder for now)."""
    project = get_object_or_404(
        SubtitleProject,
        id=project_id,
        video__user=request.user
    )
    
    # This is a placeholder - actual video export would require FFmpeg processing
    messages.info(request, 'Video export feature is coming soon. For now, you can export subtitles as SRT/VTT files.')
    return redirect('transcription:editor', project_id=project.id)


@login_required
def download_document(request, project_id, language):
    """Download transcription document."""
    project = get_object_or_404(
        SubtitleProject,
        id=project_id,
        video__user=request.user
    )
    
    if language == 'arabic' and project.doc_file_arabic:
        file_path = os.path.join(settings.MEDIA_ROOT, project.doc_file_arabic.name)
    elif language == 'english' and project.doc_file_english:
        file_path = os.path.join(settings.MEDIA_ROOT, project.doc_file_english.name)
    else:
        messages.error(request, 'Document not available.')
        return redirect('transcription:editor', project_id=project.id)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(
                f.read(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    else:
        messages.error(request, 'File not found.')
        return redirect('transcription:editor', project_id=project.id)


@login_required
def check_processing_status(request, project_id):
    """Check if subtitle processing is complete."""
    project = get_object_or_404(
        SubtitleProject,
        id=project_id,
        video__user=request.user
    )
    
    return JsonResponse({
        'status': project.video.status,
        'segments_count': project.segments.count(),
        'has_segments': project.segments.exists()
    })


# Legacy views for compatibility with old transcription system
@login_required
def video_list(request):
    """List all user's videos (legacy support)."""
    videos = VideoFile.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'title': 'My Videos',
        'videos': videos,
    }
    
    return render(request, 'transcription/list.html', context)


@login_required
def video_detail(request, video_id):
    """Show video details (redirect to editor for new system)."""
    video = get_object_or_404(VideoFile, id=video_id, user=request.user)
    
    # Check if video has a subtitle project
    project = SubtitleProject.objects.filter(video=video).first()
    if project:
        return redirect('transcription:editor', project_id=project.id)
    else:
        # Create a new project for this video
        project = SubtitleProject.objects.create(
            video=video,
            source_language='ar',  # Default
            subtitle_mode='same'
        )
        SubtitleStyle.objects.create(project=project)
        return redirect('transcription:editor', project_id=project.id)


@login_required
def check_status(request, video_id):
    """Check transcription status (legacy support)."""
    video = get_object_or_404(VideoFile, id=video_id, user=request.user)
    
    data = {
        'status': video.status,
        'updated_at': video.updated_at.isoformat() if hasattr(video, 'updated_at') else None,
    }
    
    return JsonResponse(data)


@login_required
@require_POST
def update_retention(request, video_id):
    """Update video retention setting (legacy support)."""
    video = get_object_or_404(VideoFile, id=video_id, user=request.user)
    
    retention = request.POST.get('retention')
    if retention in dict(VideoFile.RETENTION_CHOICES):
        video.retention = retention
        
        # Update delete_at based on retention
        if retention == '5days':
            video.delete_at = timezone.now() + timezone.timedelta(days=5)
        else:  # delete now
            video.delete_at = None
        
        video.save()
        
        messages.success(request, 'Retention setting updated successfully.')
    else:
        messages.error(request, 'Invalid retention value.')
    
    # Find project and redirect to editor
    project = SubtitleProject.objects.filter(video=video).first()
    if project:
        return redirect('transcription:editor', project_id=project.id)
    else:
        return redirect('transcription:home')