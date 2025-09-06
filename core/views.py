from django.shortcuts import render

# Create your views here.


def register_models_and_tools(request):
    """One-time registration of models and tools - REMOVE AFTER USE"""
    from django.http import HttpResponse
    from askme.models import LLMModel
    from tool_registry.models import AITool
    from django.utils.text import slugify
    
    if request.method == 'POST':
        try:
            results = []
            
            # Register LLM Models
            models_data = [
                {
                    'name': 'GPT-4o',
                    'provider': 'OpenAI',
                    'model_id': 'gpt-4o',
                    'description': 'GPT-4o is a powerful model for a wide range of tasks including creative content, code generation, and problem-solving.',
                    'icon': 'cpu',
                },
                {
                    'name': 'DeepSeek Chat',
                    'provider': 'DeepSeek',
                    'model_id': 'deepseek-chat',
                    'description': 'DeepSeek Chat provides natural conversational abilities with strong knowledge across various domains.',
                    'icon': 'chat',
                },
                {
                    'name': 'Test Model',
                    'provider': 'Mock',
                    'model_id': 'mock-model',
                    'description': 'A test model that doesn\'t require API keys. Use this for development and testing.',
                    'icon': 'activity',
                },
            ]
            
            for model_data in models_data:
                model, created = LLMModel.objects.update_or_create(
                    name=model_data['name'],
                    provider=model_data['provider'],
                    defaults={
                        'model_id': model_data['model_id'],
                        'description': model_data['description'],
                        'icon': model_data.get('icon', 'chat-dots'),
                        'is_active': True
                    }
                )
                status = "Created" if created else "Updated"
                results.append(f"{status} LLM model: {model.name}")
            
            # Register AI Tools
            tools_data = [
                {
                    'name': 'Ask Me',
                    'description': 'Ask questions to various AI models. Upload files or just type your query to get intelligent responses.',
                    'icon': 'chat-dots',
                    'url_name': 'askme:home',
                    'order': 2,
                },
                {
                    'name': 'Program Ideation',
                    'description': 'Create TV program ideas for Saudi Broadcasting Authority using AI assistance.',
                    'icon': 'lightbulb',
                    'url_name': 'program_ideation:home',
                    'order': 3,
                }
            ]
            
            for tool_data in tools_data:
                slug = slugify(tool_data['name'])
                tool, created = AITool.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'name': tool_data['name'],
                        'description': tool_data['description'],
                        'icon': tool_data['icon'],
                        'url_name': tool_data['url_name'],
                        'order': tool_data['order'],
                        'is_active': True
                    }
                )
                status = "Created" if created else "Updated"
                results.append(f"{status} AI tool: {tool.name}")
            
            results_html = "<br>".join(results)
            return HttpResponse(f"""
            <h2>SUCCESS! Registration Complete</h2>
            <p>{results_html}</p>
            <p><a href="/admin/">Check Admin Panel</a> | <a href="/">Check Dashboard</a></p>
            """)
            
        except Exception as e:
            return HttpResponse(f"Error: {e}")
    
    return HttpResponse("""
    <form method="post">
    <h2>Register AI Models and Tools</h2>
    <p>This will register:</p>
    <ul>
    <li><strong>LLM Models:</strong> GPT-4o, DeepSeek Chat, Test Model</li>
    <li><strong>AI Tools:</strong> Ask Me, Program Ideation</li>
    </ul>
    <input type="submit" value="Register Models and Tools" style="padding: 10px 20px; font-size: 16px;">
    </form>
    """)