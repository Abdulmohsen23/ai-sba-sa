import os
import time
import whisper
from docx import Document
from datetime import datetime
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import tempfile
from django.conf import settings
from django.utils import timezone
import logging

# Set up logging
logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for handling video transcription using Whisper."""
    
    def __init__(self, model_name="large-v2"):
        self.model_name = model_name
        self.model = None
        self.pause_threshold = 0.5  # Minimum pause (in seconds) to start a new paragraph
    
    def load_model(self):
        """Load the Whisper model."""
        logger.info(f"Loading Whisper model: {self.model_name}")
        if self.model is None:
            try:
                self.model = whisper.load_model(self.model_name)
                logger.info(f"Successfully loaded model: {self.model_name}")
            except Exception as e:
                logger.error(f"Error loading model: {str(e)}")
                raise
        return self.model
    
    def transcribe_video(self, video_path, language="ar"):
        """Transcribe video and return result with paragraphs."""
        start_time = time.time()
        logger.info(f"Starting transcription of video: {video_path}")
        
        try:
            # Load model if not already loaded
            model = self.load_model()
            
            # Run transcription
            logger.info(f"Running transcription with language: {language}")
            result = model.transcribe(video_path, language=language)
            
            # Split transcript by pauses
            paragraphs = []
            last_end = None
            current_paragraph = ""
            
            # Loop through each segment in the result
            for segment in result["segments"]:
                # If there was a previous segment, and the gap is big enough, start new paragraph
                if last_end is not None and segment["start"] - last_end > self.pause_threshold:
                    paragraphs.append(current_paragraph.strip())  # Save current paragraph
                    current_paragraph = ""                        # Start new paragraph
                current_paragraph += " " + segment["text"]        # Add segment text
                last_end = segment["end"]                         # Update last_end
            
            # Add any remaining text as the last paragraph
            if current_paragraph:
                paragraphs.append(current_paragraph.strip())
                
            # Calculate processing time
            processing_time = (time.time() - start_time) / 60
            logger.info(f"Transcription completed in {processing_time:.2f} minutes")
                
            return {
                'paragraphs': paragraphs,
                'full_text': '\n\n'.join(paragraphs),
                'processing_time': processing_time
            }
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise
    
    def create_docx(self, paragraphs, output_path=None):
        """Create Word document with RTL support."""
        logger.info("Creating Word document with transcription")
        
        try:
            output_doc = Document()
            
            for para_text in paragraphs:
                p = output_doc.add_paragraph(para_text)
                # Set paragraph direction to Right-To-Left (RTL)
                p_pr = p._p.get_or_add_pPr()
                bidi = OxmlElement('w:bidi')
                bidi.set(qn('w:val'), '1')
                p_pr.append(bidi)
            
            # If no output path is provided, create a temporary file
            if not output_path:
                timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
                filename = f"transcription_{timestamp}.docx"
                output_path = os.path.join(settings.MEDIA_ROOT, 'transcriptions', filename)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            output_doc.save(output_path)
            logger.info(f"Document saved to: {output_path}")
            
            return output_path
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise