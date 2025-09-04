import os
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import VideoFile, SubtitleProject, SubtitleSegment, SubtitleStyle
from .subtitle_services import EnhancedSubtitleService, create_subtitle_document

logger = logging.getLogger(__name__)


class SubtitleProcessor:
    """Synchronous subtitle processing service."""
    
    @staticmethod
    def process_subtitle_generation(project_id):
        """Process subtitle generation synchronously."""
        try:
            # Get project
            project = SubtitleProject.objects.get(id=project_id)
            video = project.video
            
            # Update status
            video.status = 'processing'
            video.save()
            
            logger.info(f"Starting subtitle generation for project {project_id}")
            
            # Initialize service
            service = EnhancedSubtitleService()
            
            # Get video path
            video_path = video.file.path
            
            # Transcribe video
            logger.info(f"Transcribing video: {video_path}")
            transcription_result = service.transcribe_video(
                video_path,
                source_language=project.source_language
            )
            
            # Create subtitle segments
            logger.info("Creating subtitle segments...")
            subtitle_segments = service.create_subtitle_segments(
                transcription_result['segments']
            )
            
            # Process each segment
            segments_data = []
            for idx, segment in enumerate(subtitle_segments, 1):
                original_text = segment['text'].strip()
                
                # Translate if needed
                translated_text = None
                if project.subtitle_mode == 'translate':
                    logger.info(f"Translating segment {idx}/{len(subtitle_segments)}")
                    translated_text = service.translate_text(
                        original_text,
                        source_lang=project.source_language,
                        target_lang=project.target_language
                    )
                
                # Create SubtitleSegment in database
                SubtitleSegment.objects.create(
                    project=project,
                    segment_number=idx,
                    start_time=segment['start'],
                    end_time=segment['end'],
                    original_text=original_text,
                    translated_text=translated_text
                )
                
                segments_data.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'original_text': original_text,
                    'translated_text': translated_text
                })
            
            # Generate subtitle files
            logger.info("Generating subtitle files...")
            
            # Create subtitles directory if it doesn't exist
            subtitles_dir = os.path.join(settings.MEDIA_ROOT, 'subtitles')
            os.makedirs(subtitles_dir, exist_ok=True)
            
            # Generate SRT files
            srt_content_original = service.create_srt_content(segments_data, use_translated=False)
            srt_filename_original = f"{video.id}_original.srt"
            srt_path_original = os.path.join(subtitles_dir, srt_filename_original)
            
            with open(srt_path_original, 'w', encoding='utf-8') as f:
                f.write(srt_content_original)
            
            project.srt_file_arabic = f"subtitles/{srt_filename_original}"
            
            if project.subtitle_mode == 'translate':
                srt_content_translated = service.create_srt_content(segments_data, use_translated=True)
                srt_filename_translated = f"{video.id}_translated.srt"
                srt_path_translated = os.path.join(subtitles_dir, srt_filename_translated)
                
                with open(srt_path_translated, 'w', encoding='utf-8') as f:
                    f.write(srt_content_translated)
                
                project.srt_file_english = f"subtitles/{srt_filename_translated}"
            
            # Generate VTT files
            vtt_content_original = service.create_vtt_content(segments_data, use_translated=False)
            vtt_filename_original = f"{video.id}_original.vtt"
            vtt_path_original = os.path.join(subtitles_dir, vtt_filename_original)
            
            with open(vtt_path_original, 'w', encoding='utf-8') as f:
                f.write(vtt_content_original)
            
            project.vtt_file_arabic = f"subtitles/{vtt_filename_original}"
            
            if project.subtitle_mode == 'translate':
                vtt_content_translated = service.create_vtt_content(segments_data, use_translated=True)
                vtt_filename_translated = f"{video.id}_translated.vtt"
                vtt_path_translated = os.path.join(subtitles_dir, vtt_filename_translated)
                
                with open(vtt_path_translated, 'w', encoding='utf-8') as f:
                    f.write(vtt_content_translated)
                
                project.vtt_file_english = f"subtitles/{vtt_filename_translated}"
            
            # Generate Word documents
            logger.info("Generating Word documents...")
            
            # Arabic document
            doc_arabic = create_subtitle_document(
                segments_data, 
                video.original_filename,
                project.source_language,
                is_rtl=(project.source_language == 'ar')
            )
            doc_filename_arabic = f"{video.id}_transcription_arabic.docx"
            doc_path_arabic = os.path.join(subtitles_dir, doc_filename_arabic)
            doc_arabic.save(doc_path_arabic)
            project.doc_file_arabic = f"subtitles/{doc_filename_arabic}"
            
            # English document (if translated)
            if project.subtitle_mode == 'translate':
                doc_english = create_subtitle_document(
                    segments_data,
                    video.original_filename,
                    'en',
                    is_rtl=False,
                    use_translated=True
                )
                doc_filename_english = f"{video.id}_transcription_english.docx"
                doc_path_english = os.path.join(subtitles_dir, doc_filename_english)
                doc_english.save(doc_path_english)
                project.doc_file_english = f"subtitles/{doc_filename_english}"
            
            # Update project processing time
            project.processing_time = (timezone.now() - project.created_at).total_seconds() / 60
            project.save()
            
            # Update video status
            video.status = 'completed'
            
            # Set deletion date if retention is 5 days
            if video.retention == '5days':
                video.delete_at = timezone.now() + timedelta(days=5)
            
            video.save()
            
            logger.info(f"Subtitle generation completed for project {project_id}")
            
            return {
                'success': True,
                'project_id': project.id,
                'segments_count': len(segments_data)
            }
            
        except Exception as e:
            logger.error(f"Error processing project {project_id}: {str(e)}")
            
            # Update video status to failed
            try:
                video = VideoFile.objects.get(id=project.video.id)
                video.status = 'failed'
                video.error_message = str(e)
                video.save()
            except:
                pass
            
            return {
                'success': False,
                'error': str(e)
            }