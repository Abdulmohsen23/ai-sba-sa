from django import forms
from .models import VideoFile, SubtitleProject


class VideoUploadForm(forms.Form):
    """Form for uploading video and setting subtitle preferences."""
    
    file = forms.FileField(
        label='Video File',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'video/*',
            'id': 'id_file'
        })
    )
    
    source_language = forms.ChoiceField(
        choices=[
            ('ar', 'Arabic'),
            ('en', 'English'),
        ],
        initial='ar',
        label='Video Language',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    subtitle_mode = forms.ChoiceField(
        choices=[
            ('same', 'Same as video language'),
            ('translate', 'Translate to other language'),
        ],
        initial='same',
        label='Subtitle Type',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    target_language = forms.ChoiceField(
        choices=[
            ('', '-- Select --'),
            ('ar', 'Arabic'),
            ('en', 'English'),
        ],
        required=False,
        label='Translate to',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'target-language'
        })
    )
    
    retention = forms.ChoiceField(
        choices=VideoFile.RETENTION_CHOICES,
        initial='5days',
        label='Video Retention',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        subtitle_mode = cleaned_data.get('subtitle_mode')
        target_language = cleaned_data.get('target_language')
        source_language = cleaned_data.get('source_language')
        
        if subtitle_mode == 'translate':
            if not target_language:
                raise forms.ValidationError('Please select a target language for translation.')
            if target_language == source_language:
                raise forms.ValidationError('Target language must be different from source language.')
        
        # Validate file
        file = cleaned_data.get('file')
        if file:
            # Validate file size (limit to 500MB)
            if file.size > 500 * 1024 * 1024:
                raise forms.ValidationError('File size must be no more than 500MB.')
            
            # Validate file extension
            ext = file.name.split('.')[-1].lower()
            valid_extensions = ['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm']
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Unsupported file format. Please upload: {", ".join(valid_extensions)}'
                )
        
        return cleaned_data