from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AITool


def dashboard(request):
    """Main dashboard displaying available AI tools."""
    tools = AITool.objects.filter(is_active=True)
    
    context = {
        'tools': tools,
        'title': 'AI Tools Dashboard'
    }
    
    return render(request, 'dashboard.html', context)