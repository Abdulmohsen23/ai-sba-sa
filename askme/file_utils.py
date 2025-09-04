import os
import logging
import tempfile
from django.conf import settings

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path, file_type):
    """Extract text content from various file types."""
    try:
        if file_type.lower() in ['txt']:
            # Simple text file
            with open(file_path, 'r', errors='ignore') as f:
                return f.read()
                
        elif file_type.lower() in ['pdf']:
            # PDF file
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                return "[PDF content could not be extracted - PyPDF2 not installed]"
                
        elif file_type.lower() in ['docx']:
            # Word document
            try:
                import docx
                doc = docx.Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            except ImportError:
                return "[DOCX content could not be extracted - python-docx not installed]"
                
        elif file_type.lower() in ['jpg', 'jpeg', 'png']:
            # Image file - would require OCR
            return "[This is an image file. Please ask specific questions about the image.]"
            
        else:
            return f"[Unsupported file type: {file_type}]"
            
    except Exception as e:
        logger.error(f"Error extracting text from file: {str(e)}")
        return f"[Error extracting file content: {str(e)}]"