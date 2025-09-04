import os
import threading
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def process_llm_request(question_id):
    """Process LLM request in a separate thread."""
    # Import here to avoid circular imports
    from askme.models import Question, Response, Conversation
    from askme.services import LLMService, ContentFilterService
    
    def _process():
        logger.info(f"Starting LLM processing for question ID: {question_id}")
        try:
            # Get the question
            question = Question.objects.get(id=question_id)
            question.status = 'processing'
            question.save()
            
            # Check for sensitive content
            is_sensitive, sensitive_details = ContentFilterService.check_sensitive_content(question.content)
            
            # Prepare file path if a file was uploaded
            file_path = None
            file_type = None
            if question.file and question.file.name:
                file_path = os.path.join(settings.MEDIA_ROOT, question.file.name)
                file_type = question.file_type
                logger.info(f"Processing file: {file_path} of type {file_type}")
            
            # Create service and generate response
            service = LLMService()
            
            # Get conversation ID for context
            conversation_id = question.conversation_id
            
            # Update conversation title if it's the first question
            if question.sequence == 1:
                conversation = question.conversation
                # Generate title from first question
                title = question.content[:50] + ('...' if len(question.content) > 50 else '')
                conversation.title = title
                conversation.save()
            
            # Generate response with file content if available
            result = service.generate_response(
                provider=question.llm_model.provider,
                model_id=question.llm_model.model_id,
                prompt=question.content,
                conversation_id=conversation_id,
                file_path=file_path,
                file_type=file_type
            )
            
            if result['success']:
                # Create response
                response = Response.objects.create(
                    question=question,
                    content=result['content'],
                    processing_time=result['processing_time'],
                    sensitive_content_detected=is_sensitive
                )
                
                # Update question status
                question.status = 'completed'
                question.save()
                
                logger.info(f"LLM processing completed for question ID: {question_id}")
                
                return {
                    'success': True,
                    'question_id': question.id,
                    'response_id': response.id
                }
            else:
                # Update question status to failed
                question.status = 'failed'
                question.error_message = result.get('error', 'Unknown error')
                question.save()
                
                logger.error(f"LLM processing failed for question ID: {question_id}")
                
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }
        
        except Exception as e:
            logger.error(f"Error processing question ID {question_id}: {str(e)}")
            # Update question status to failed
            try:
                question = Question.objects.get(id=question_id)
                question.status = 'failed'
                question.error_message = str(e)
                question.save()
            except:
                pass
            
            return {
                'success': False,
                'error': str(e)
            }
    
    # Start processing in a separate thread
    thread = threading.Thread(target=_process)
    thread.daemon = True
    thread.start()
    
    return {
        'success': True,
        'message': f'Processing started for question ID: {question_id}'
    }