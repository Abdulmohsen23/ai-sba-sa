# translation/tasks.py

"""
This is a placeholder file to maintain imports in other files.
The application now uses synchronous processing instead of Celery tasks.
"""

def process_video(project_id):
    """
    Function to process a video for the given project.
    This is a synchronous version that doesn't use Celery.
    """
    from .services import TranslationService
    service = TranslationService(project_id)
    return service.process_video()