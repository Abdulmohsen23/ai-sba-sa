import time
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from core.utils import log_user_activity


class UserActivityMiddleware(MiddlewareMixin):
    """Middleware to log user activity for specific views."""
    
    # List of URL names to log
    TRACKED_URL_NAMES = [
        'transcription:upload',
        # Add more URL names to track as needed
    ]
    
    def process_request(self, request):
        """Store the start time of the request."""
        request.start_time = time.time()
    
    def process_response(self, request, response):
        """Log user activity for tracked views."""
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        
        try:
            # Try to resolve the URL to get the URL name
            resolver_match = resolve(request.path_info)
            url_name = resolver_match.url_name
            namespace = resolver_match.namespace
            
            # Construct the full URL name (with namespace)
            if namespace:
                full_url_name = f"{namespace}:{url_name}"
            else:
                full_url_name = url_name
            
            # Check if this view should be tracked
            if full_url_name in self.TRACKED_URL_NAMES:
                # Determine the tool name from the namespace
                tool_name = namespace if namespace else "unknown"
                
                # Calculate response time
                if hasattr(request, 'start_time'):
                    response_time = time.time() - request.start_time
                else:
                    response_time = None
                
                # Prepare details
                details = {
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                }
                
                if response_time:
                    details['response_time'] = round(response_time, 3)
                
                # Log the activity
                log_user_activity(
                    user=request.user,
                    tool_name=tool_name,
                    action=f"{request.method} {url_name}",
                    details=details,
                    request=request
                )
        except:
            # Fail silently - logging should not affect the response
            pass
        
        return response