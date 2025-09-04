from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.files.base import ContentFile
from django.conf import settings
import json
import os
import threading
import tempfile
import uuid
from datetime import datetime

from .models import TranslationProject, Subtitle, TranslationOutput
from .forms import TranslationProjectForm, SubtitleEditForm
from .services import TranslationService, VideoExportService

@login_required
def home(request):
    """Home page for the translation app"""
    return render(request, 'translation/home.html')

@login_required
def project_list(request):
    """List all translation projects for the current user"""
    projects = TranslationProject.objects.filter(user=request.user)
    context = {
        'projects': projects
    }
    return render(request, 'translation/list.html', context)

@login_required
def project_create(request):
    """Create a new translation project"""
    if request.method == 'POST':
        form = TranslationProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.status = 'pending'
            project.save()
            
            # Start processing in a separate thread to avoid blocking the request
            def process_video_thread(project_id):
                service = TranslationService(project_id)
                service.process_video()
            
            # Start the thread
            thread = threading.Thread(target=process_video_thread, args=(project.id,))
            thread.daemon = True  # Thread will exit when main program exits
            thread.start()
            
            return redirect('translation:detail', pk=project.id)
    else:
        form = TranslationProjectForm()
    
    context = {
        'form': form
    }
    return render(request, 'translation/create.html', context)

@login_required
def project_detail(request, pk):
    """View project details and status"""
    project = get_object_or_404(TranslationProject, pk=pk, user=request.user)
    outputs = project.outputs.all()
    
    context = {
        'project': project,
        'outputs': outputs
    }
    return render(request, 'translation/detail.html', context)

@login_required
def subtitle_editor(request, pk):
    """Enhanced subtitle and video editor interface"""
    project = get_object_or_404(TranslationProject, pk=pk, user=request.user)
    
    # Only allow editing completed projects
    if project.status != 'completed':
        return redirect('translation:detail', pk=project.id)
    
    subtitles = project.subtitles.all()
    
    context = {
        'project': project,
        'subtitles': subtitles
    }
    return render(request, 'translation/editor.html', context)

@login_required
def api_subtitle_list(request, pk):
    """API endpoint to get all subtitles for a project"""
    project = get_object_or_404(TranslationProject, pk=pk, user=request.user)
    subtitles = project.subtitles.all()
    
    data = []
    for subtitle in subtitles:
        data.append({
            'id': subtitle.id,
            'sequence': subtitle.sequence,
            'start_time': subtitle.start_time,
            'end_time': subtitle.end_time,
            'original_text': subtitle.original_text,
            'translated_text': subtitle.translated_text,
            'speaker': subtitle.speaker or "",  # Include speaker field
            'font_family': subtitle.font_family,
            'font_size': subtitle.font_size,
            'font_color': subtitle.font_color,
            'background_color': subtitle.background_color,
            'background_opacity': subtitle.background_opacity,
            'is_bold': subtitle.is_bold,
            'is_italic': subtitle.is_italic,
            'is_underline': subtitle.is_underline,
            'alignment': subtitle.alignment
        })
    
    return JsonResponse(data, safe=False)

@require_POST
@login_required
def api_subtitle_update(request, pk):
    """API endpoint to update a subtitle"""
    subtitle = get_object_or_404(Subtitle, pk=pk)
    
    # Check permissions
    if subtitle.project.user != request.user:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    # Parse JSON data
    try:
        data = json.loads(request.body)
        print(f"Received data: {data}")
        
        # Update fields
        if 'original_text' in data:
            subtitle.original_text = data['original_text']
        if 'translated_text' in data:
            subtitle.translated_text = data['translated_text']
        if 'speaker' in data:  # New field
            subtitle.speaker = data['speaker']
        if 'start_time' in data:  # New field
            subtitle.start_time = float(data['start_time'])
        if 'end_time' in data:  # New field
            subtitle.end_time = float(data['end_time'])
        
        # Update styling options
        if 'font_family' in data:
            subtitle.font_family = data['font_family']
        if 'font_size' in data:
            subtitle.font_size = data['font_size']
        if 'font_color' in data:
            subtitle.font_color = data['font_color']
        if 'background_color' in data:
            subtitle.background_color = data['background_color']
        if 'background_opacity' in data:
            subtitle.background_opacity = data['background_opacity']
        if 'is_bold' in data:
            subtitle.is_bold = data['is_bold']
        if 'is_italic' in data:
            subtitle.is_italic = data['is_italic']
        if 'is_underline' in data:
            subtitle.is_underline = data['is_underline']
        if 'alignment' in data:
            subtitle.alignment = data['alignment']
        
        subtitle.save()
        print(f"Subtitle saved. ID: {subtitle.id}, Text: {subtitle.original_text}")
        
        # Invalidate existing output files to force regeneration
        TranslationOutput.objects.filter(project=subtitle.project).delete()
        
        return JsonResponse({'status': 'success', 'message': 'Subtitle updated successfully'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        print(f"Error updating subtitle: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@login_required
def download_output(request, pk, output_type):
    """Download output files"""
    project = get_object_or_404(TranslationProject, pk=pk, user=request.user)
    
    try:
        # Try to get existing output file
        output = TranslationOutput.objects.get(project=project, output_type=output_type)
        if os.path.exists(output.file.path):
            return FileResponse(open(output.file.path, 'rb'), as_attachment=True, filename=os.path.basename(output.file.name))
        else:
            # File exists in database but not on disk, regenerate it
            output.delete()
            raise TranslationOutput.DoesNotExist()
    except TranslationOutput.DoesNotExist:
        # If file doesn't exist, generate it on the fly
        service = TranslationService(project.id)
        file_path = service.generate_single_output(output_type)
        
        if file_path and os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
        else:
            return HttpResponse("File could not be generated. Please check that subtitles exist for this project.", status=404)
        
@login_required
def export_video(request, pk):
    """Export video with embedded subtitles"""
    project = get_object_or_404(TranslationProject, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Get options from form
        subtitle_lang = request.POST.get('subtitle_language', 'original')
        font_size = request.POST.get('font_size', '24')
        font_color = request.POST.get('font_color', '#FFFFFF')
        include_images = request.POST.get('include_images', 'false') == 'true'
        
        try:
            # Start export process
            export_service = VideoExportService(project.id)
            result = export_service.export_video_with_subtitles(
                subtitle_lang=subtitle_lang,
                font_size=int(font_size),
                font_color=font_color
            )
            
            if result and os.path.exists(result):
                # File was created successfully
                response = FileResponse(open(result, 'rb'), as_attachment=True, 
                                      filename=f"{project.title}_subtitled.mp4")
                return response
            else:
                messages.error(request, "Failed to create subtitled video. Please try again.")
                
        except Exception as e:
            messages.error(request, f"Error exporting video: {str(e)}")
    
    # Show export options form
    context = {
        'project': project,
    }
    return render(request, 'translation/export.html', context)

@login_required
def download_video_with_subtitles(request, pk):
    """Download the video file and current subtitles as separate files"""
    project = get_object_or_404(TranslationProject, pk=pk, user=request.user)
    
    # First try the FFmpeg export
    if request.method == 'POST':
        subtitle_lang = request.POST.get('subtitle_language', 'original')
        try:
            export_service = VideoExportService(project.id)
            result = export_service.export_video_with_subtitles(
                subtitle_lang=subtitle_lang
            )
            
            if result and os.path.exists(result):
                # File was created successfully
                response = FileResponse(open(result, 'rb'), as_attachment=True, 
                                      filename=f"{project.title}_subtitled.mp4")
                return response
            else:
                messages.warning(request, "Could not create subtitled video. Providing video and subtitle files separately.")
                
                # Alternative: Provide both files in a zip
                import zipfile
                import tempfile
                
                with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                    zip_path = temp_zip.name
                    
                with zipfile.ZipFile(zip_path, 'w') as zip_file:
                    # Add the video file
                    video_name = os.path.basename(project.video_file.path)
                    zip_file.write(project.video_file.path, video_name)
                    
                    # Add SRT file
                    try:
                        srt_output = TranslationOutput.objects.get(
                            project=project, 
                            output_type=f"srt_{subtitle_lang}"
                        )
                        zip_file.write(srt_output.file.path, f"{project.title}_{subtitle_lang}.srt")
                    except TranslationOutput.DoesNotExist:
                        # Generate SRT file
                        service = TranslationService(project.id)
                        subtitles = project.subtitles.all().order_by('sequence')
                        srt_path = service.generate_srt_file(subtitles, subtitle_lang)
                        if srt_path:
                            zip_file.write(srt_path, f"{project.title}_{subtitle_lang}.srt")
                
                # Return the zip file
                return FileResponse(open(zip_path, 'rb'), as_attachment=True,
                                  filename=f"{project.title}_video_and_subtitles.zip")
        except Exception as e:
            messages.error(request, f"Error processing download: {str(e)}")
    
    return render(request, 'translation/export.html', {'project': project})

@require_POST
@login_required
def api_save_all_subtitles(request, pk):
    """API endpoint to save all subtitles at once with support for new and deleted subtitles"""
    project = get_object_or_404(TranslationProject, pk=pk, user=request.user)
    
    try:
        data = json.loads(request.body)
        subtitles_data = data.get('subtitles', [])
        deleted_ids = data.get('deleted', [])
        
        # Process deletions
        if deleted_ids:
            # Filter to only delete subtitles that belong to this project
            Subtitle.objects.filter(id__in=deleted_ids, project=project).delete()
        
        # Process updates and new subtitles
        for subtitle_data in subtitles_data:
            subtitle_id = subtitle_data.get('id')
            is_new = subtitle_data.get('isNew', False)
            
            # Handle new subtitles (negative IDs are temporary)
            if is_new or (subtitle_id and subtitle_id < 0):
                # Create new subtitle
                subtitle = Subtitle(project=project)
            elif subtitle_id:
                # Update existing subtitle
                try:
                    subtitle = Subtitle.objects.get(id=subtitle_id, project=project)
                except Subtitle.DoesNotExist:
                    continue
            else:
                continue
            
            # Update fields
            if 'sequence' in subtitle_data:
                subtitle.sequence = subtitle_data['sequence']
            if 'start_time' in subtitle_data:
                subtitle.start_time = float(subtitle_data['start_time'])
            if 'end_time' in subtitle_data:
                subtitle.end_time = float(subtitle_data['end_time'])
            if 'original_text' in subtitle_data:
                subtitle.original_text = subtitle_data['original_text']
            if 'translated_text' in subtitle_data:
                subtitle.translated_text = subtitle_data['translated_text']
            if 'speaker' in subtitle_data:
                subtitle.speaker = subtitle_data['speaker']
            
            # Update styling options
            if 'font_family' in subtitle_data:
                subtitle.font_family = subtitle_data['font_family']
            if 'font_size' in subtitle_data:
                subtitle.font_size = int(subtitle_data['font_size'])
            if 'font_color' in subtitle_data:
                subtitle.font_color = subtitle_data['font_color']
            if 'background_color' in subtitle_data:
                subtitle.background_color = subtitle_data['background_color']
            if 'background_opacity' in subtitle_data:
                subtitle.background_opacity = float(subtitle_data['background_opacity'])
            if 'is_bold' in subtitle_data:
                subtitle.is_bold = bool(subtitle_data['is_bold'])
            if 'is_italic' in subtitle_data:
                subtitle.is_italic = bool(subtitle_data['is_italic'])
            if 'is_underline' in subtitle_data:
                subtitle.is_underline = bool(subtitle_data['is_underline'])
            if 'alignment' in subtitle_data:
                subtitle.alignment = subtitle_data['alignment']
            
            subtitle.save()
        
        # Invalidate existing output files to force regeneration
        TranslationOutput.objects.filter(project=project).delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Successfully updated {len(subtitles_data)} subtitles'
        })
    except Exception as e:
        print(f"Error saving all subtitles: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def direct_download_video(request, pk):
    """Download video with hard-coded subtitles"""
    project = get_object_or_404(TranslationProject, pk=pk, user=request.user)
    subtitle_lang = request.GET.get('subtitle_language', 'original')
    font_size = request.GET.get('font_size', '24')
    font_color = request.GET.get('font_color', '#FFFFFF')
    include_images = request.GET.get('include_images', 'true') == 'true'
    
    try:
        export_service = VideoExportService(project.id)
        
        # This will try all three methods automatically
        result = export_service.export_video_with_subtitles(
            subtitle_lang=subtitle_lang,
            font_size=int(font_size),
            font_color=font_color
        )
        
        if result and os.path.exists(result):
            return FileResponse(
                open(result, 'rb'), 
                as_attachment=True, 
                filename=f"{project.title}_subtitled.mp4"
            )
        else:
            messages.error(request, "Could not create video with burned-in subtitles.")
            return redirect('translation:editor', pk=project.pk)
            
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('translation:editor', pk=project.pk)

@require_POST
@login_required
def upload_image_overlay(request, pk):
    """API endpoint to upload and save an image overlay for a video"""
    project = get_object_or_404(TranslationProject, pk=pk, user=request.user)
    
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'status': 'error', 'message': 'No image file provided'}, status=400)
            
        image_file = request.FILES['image']
        start_time = float(request.POST.get('start_time', 0))
        end_time = float(request.POST.get('end_time', 5))
        position_x = float(request.POST.get('position_x', 10))
        position_y = float(request.POST.get('position_y', 10))
        width = float(request.POST.get('width', 30))
        height = request.POST.get('height', 'auto')
        
        # Generate a unique ID for the overlay
        overlay_id = str(uuid.uuid4())
        
        # Save image to media storage
        from core.utils import get_file_upload_path
        image_path = get_file_upload_path(None, f"overlay_{overlay_id}.{image_file.name.split('.')[-1]}")
        
        from django.core.files.storage import default_storage
        with default_storage.open(image_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # Return success response with overlay data
        return JsonResponse({
            'status': 'success',
            'message': 'Image overlay saved',
            'data': {
                'id': overlay_id,
                'image_url': default_storage.url(image_path),
                'start_time': start_time,
                'end_time': end_time,
                'position_x': position_x,
                'position_y': position_y,
                'width': width,
                'height': height
            }
        })
        
    except Exception as e:
        print(f"Error uploading image overlay: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)