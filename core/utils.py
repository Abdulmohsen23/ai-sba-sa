import os
import uuid
from django.utils import timezone


def get_file_upload_path(instance, filename):
    """
    Generate a unique file path for uploads.
    Format: uploads/<model_name>/<year>/<month>/<day>/<uuid>_<filename>
    """
    now = timezone.now()
    model_name = instance.__class__.__name__.lower()
    
    # Get the file extension
    _, ext = os.path.splitext(filename)
    
    # Generate a unique filename with UUID
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    
    # Construct path: uploads/model_name/YYYY/MM/DD/uuid_filename
    return os.path.join(
        'uploads',
        model_name,
        f"{now.year}",
        f"{now.month:02d}",
        f"{now.day:02d}",
        unique_filename
    )


def log_user_activity(user, tool_name, action, details=None, request=None):
    """
    Log user activity in the database.
    
    Args:
        user: The user performing the action
        tool_name: Name of the AI tool being used
        action: Description of the action performed
        details: Additional details as JSON-serializable dict
        request: The request object, to extract IP address
    """
    from core.models import UserActivity
    
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
    
    UserActivity.objects.create(
        user=user,
        tool_name=tool_name,
        action=action,
        details=details,
        ip_address=ip_address
    )