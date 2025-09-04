from django import forms
from .models import Question, LLMModel, Conversation


class QuestionForm(forms.ModelForm):
    """Form for submitting questions to LLM models."""
    
    llm_model = forms.ModelChoiceField(
        queryset=LLMModel.objects.filter(is_active=True),
        empty_label=None,
        label='Select AI Model',
        widget=forms.RadioSelect
    )
    
    class Meta:
        model = Question
        fields = ['content', 'file', 'llm_model']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Ask me anything...',
                'class': 'form-control'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.txt,.pdf,.docx,.jpg,.jpeg,.png'
            })
        }
        labels = {
            'content': 'Question',
            'file': 'Upload Media (Optional)',
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validate file size (limit to 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be no more than 10MB.')
            
            # Validate file extension
            ext = file.name.split('.')[-1].lower()
            valid_extensions = ['txt', 'pdf', 'docx', 'jpg', 'jpeg', 'png']
            if ext not in valid_extensions:
                raise forms.ValidationError(f'Unsupported file format. Please upload a file in one of these formats: {", ".join(valid_extensions)}.')
            
            # Set file_type field value
            self.instance.file_type = ext
        
        return file


class FollowUpQuestionForm(forms.ModelForm):
    """Form for follow-up questions in a conversation."""
    
    class Meta:
        model = Question
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ask a follow-up question...',
                'class': 'form-control'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.txt,.pdf,.docx,.jpg,.jpeg,.png'
            })
        }
        labels = {
            'content': 'Your follow-up question',  # Explicit label for the text field
            'file': 'Attach File (Optional)',
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validate file size (limit to 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be no more than 10MB.')
            
            # Validate file extension
            ext = file.name.split('.')[-1].lower()
            valid_extensions = ['txt', 'pdf', 'docx', 'jpg', 'jpeg', 'png']
            if ext not in valid_extensions:
                raise forms.ValidationError(f'Unsupported file format. Please upload a file in one of these formats: {", ".join(valid_extensions)}.')
            
            # Set file_type field value (will be set in the view)
            return file
        
        return file