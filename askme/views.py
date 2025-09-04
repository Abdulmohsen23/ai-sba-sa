from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import Question, Response, LLMModel, Conversation
from .forms import QuestionForm, FollowUpQuestionForm
from .tasks import process_llm_request
from core.utils import log_user_activity
import logging

logger = logging.getLogger(__name__)


@login_required
def home(request):
    """Ask Me tool home page."""
    # Get available LLM models
    models = LLMModel.objects.filter(is_active=True)
    
    # Get user's recent conversations
    recent_conversations = Conversation.objects.filter(
        user=request.user, is_active=True
    ).order_by('-updated_at')[:5]
    
    # Create form
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create a new conversation
                conversation = Conversation.objects.create(
                    user=request.user,
                    title="New Conversation",  # Will be updated after first response
                    llm_model=form.cleaned_data['llm_model']
                )
                
                # Create Question instance
                question = form.save(commit=False)
                question.user = request.user
                question.status = 'pending'
                question.conversation = conversation
                question.sequence = 1  # First question in conversation
                question.save()
                
                # Log the activity
                log_user_activity(
                    user=request.user,
                    tool_name='askme',
                    action='submit_question',
                    details={
                        'question_id': question.id,
                        'model_id': question.llm_model.id,
                        'has_file': bool(question.file)
                    },
                    request=request
                )
                
                # Start processing
                process_llm_request(question.id)
                
                messages.success(request, 'Question submitted. Processing your request...')
                return redirect('askme:conversation', conversation_id=conversation.id)
            
            except Exception as e:
                logger.error(f"Error submitting question: {str(e)}")
                messages.error(request, f'Error submitting question: {str(e)}')
                return redirect('askme:home')
    else:
        form = QuestionForm()
    
    context = {
        'title': 'Ask Me',
        'form': form,
        'models': models,
        'recent_conversations': recent_conversations,
    }
    
    return render(request, 'askme/home.html', context)


@login_required
def conversation_detail(request, conversation_id):
    """Show conversation details with all questions and responses."""
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    questions = conversation.questions.all().order_by('sequence')
    
    # Handle follow-up question
    if request.method == 'POST':
        form = FollowUpQuestionForm(request.POST, request.FILES)  # Add request.FILES here
        if form.is_valid():
            try:
                # Create follow-up question
                question = form.save(commit=False)
                question.user = request.user
                question.status = 'pending'
                question.conversation = conversation
                question.llm_model = conversation.llm_model
                
                # Handle file upload
                if 'file' in request.FILES:
                    question.file = request.FILES['file']
                    file_ext = question.file.name.split('.')[-1].lower()
                    question.file_type = file_ext
                
                question.save()  # sequence will be auto-set
                
                # Log the activity
                log_user_activity(
                    user=request.user,
                    tool_name='askme',
                    action='submit_followup',
                    details={
                        'question_id': question.id,
                        'conversation_id': conversation.id,
                        'has_file': bool(question.file)  # Add this line
                    },
                    request=request
                )
                
                # Start processing
                process_llm_request(question.id)
                
                messages.success(request, 'Follow-up question submitted. Processing your request...')
                return redirect('askme:conversation', conversation_id=conversation.id)
                
            except Exception as e:
                logger.error(f"Error submitting follow-up: {str(e)}")
                messages.error(request, f'Error submitting follow-up: {str(e)}')
                return redirect('askme:conversation', conversation_id=conversation.id)
    else:
        form = FollowUpQuestionForm()
    
    context = {
        'title': conversation.title,
        'conversation': conversation,
        'questions': questions,
        'form': form
    }
    
    return render(request, 'askme/conversation.html', context)


@login_required
def question_detail(request, question_id):
    """Show question details and response."""
    question = get_object_or_404(Question, id=question_id, user=request.user)
    
    context = {
        'title': 'Question Details',
        'question': question,
    }
    
    return render(request, 'askme/detail.html', context)


@login_required
def conversation_list(request):
    """List all user's conversations."""
    conversations = Conversation.objects.filter(
        user=request.user, is_active=True
    ).order_by('-updated_at')
    
    context = {
        'title': 'My Conversations',
        'conversations': conversations,
    }
    
    return render(request, 'askme/conversation_list.html', context)


@login_required
def check_status(request, question_id):
    """Check question status (for AJAX polling)."""
    question = get_object_or_404(Question, id=question_id, user=request.user)
    
    data = {
        'status': question.status,
        'updated_at': question.updated_at.isoformat(),
    }
    
    if question.status == 'completed' and hasattr(question, 'response'):
        data['response_id'] = question.response.id
        data['response_content'] = question.response.content
    elif question.status == 'failed':
        data['error'] = question.error_message or 'An error occurred while processing your question.'
    
    return JsonResponse(data)


def debug_api_keys(request):
    """Debug view to check if API keys are loaded."""
    return JsonResponse({
        'openai_key_set': bool(settings.OPENAI_API_KEY),
        'anthropic_key_set': bool(settings.ANTHROPIC_API_KEY)
    })