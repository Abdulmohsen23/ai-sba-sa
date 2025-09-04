from django.core.management.base import BaseCommand
from askme.models import Question, Conversation, LLMModel

def run():
    # Get a default LLM model
    default_model = LLMModel.objects.first()
    if not default_model:
        print("No LLM models found. Please create at least one model first.")
        return
        
    # Find questions without conversations
    questions_without_conv = Question.objects.filter(conversation__isnull=True)
    
    if not questions_without_conv.exists():
        print("No questions without conversations found.")
        return
        
    print(f"Found {questions_without_conv.count()} questions without conversations.")
    
    # Group questions by user
    user_questions = {}
    for question in questions_without_conv:
        if question.user_id not in user_questions:
            user_questions[question.user_id] = []
        user_questions[question.user_id].append(question)
    
    # Create a conversation for each user's questions
    for user_id, questions in user_questions.items():
        # Create conversation
        title = questions[0].content[:50] + ('...' if len(questions[0].content) > 50 else '')
        conv = Conversation.objects.create(
            user_id=user_id,
            title=title,
            llm_model=questions[0].llm_model or default_model
        )
        print(f"Created conversation '{title}' for user ID {user_id}")
        
        # Assign questions to conversation
        for i, question in enumerate(questions):
            question.conversation = conv
            question.sequence = i + 1
            question.save()
            print(f"  Assigned question ID {question.id} to conversation")
    
    print("Done!")

if __name__ == "__main__":
    run()