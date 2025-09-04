from django import forms
from .models import TranslationProject, Subtitle

class TranslationProjectForm(forms.ModelForm):
    class Meta:
        model = TranslationProject
        fields = ['title', 'source_language', 'translation_mode', 'video_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project title'}),
            'source_language': forms.Select(attrs={'class': 'form-select'}),
            'translation_mode': forms.Select(attrs={'class': 'form-select'}),
            'video_file': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
        }

class SubtitleEditForm(forms.ModelForm):
    class Meta:
        model = Subtitle
        fields = ['original_text', 'translated_text']
        widgets = {
            'original_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'translated_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }