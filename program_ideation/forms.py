from django import forms
from .models import ProgramIdea , IdeaNote

class LanguageSelectionForm(forms.Form):
    """Form for selecting language preference."""
    LANGUAGE_CHOICES = [
        ('ar', 'العربية (Arabic)'),
        ('en', 'English (الإنجليزية)'),
    ]
    
    language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        widget=forms.RadioSelect,
        label="Which language do you prefer? / أي لغة تفضل؟"
    )

class StartIdeationForm(forms.Form):
    """Form for starting the ideation process."""
    IDEA_CHOICES = [
        (True, 'لدي فكرة محددة'),
        (False, 'ليس لدي فكرة محددة'),
    ]
    
    # FIXED: Changed to TypedChoiceField to support coerce
    has_specific_idea = forms.TypedChoiceField(
        choices=IDEA_CHOICES,
        widget=forms.RadioSelect,
        label="لنبدأ في صناعة البرنامج:",
        coerce=lambda x: x == 'True'  # Now valid
    )

class InitialConceptForm(forms.Form):
    """Form for providing initial concept."""
    HAS_CONCEPT_CHOICES = [
        (True, 'اكتب هنا التصور الاولي'),
        (False, 'لا, اعطني افكار'),
    ]
    
    # FIXED: Changed to TypedChoiceField to support coerce
    has_initial_concept = forms.TypedChoiceField(
        choices=HAS_CONCEPT_CHOICES,
        widget=forms.RadioSelect,
        label="هل لديك تصور أولي عن البرنامج:",
        coerce=lambda x: x == 'True'  # Now valid
    )
    
    initial_concept = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'اكتب هنا التصور الاولي...'}),
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        has_concept = cleaned_data.get('has_initial_concept')
        initial_concept = cleaned_data.get('initial_concept')
        
        if has_concept and not initial_concept:
            self.add_error('initial_concept', 'يرجى كتابة التصور الأولي')
        
        return cleaned_data

class ProgramDetailsForm(forms.ModelForm):
    """Form for program details."""
    class Meta:
        model = ProgramIdea
        fields = [
            'program_name', 'general_idea', 'target_audience',
            'program_objectives', 'program_type', 'program_duration',
            'episode_count', 'filming_location'
        ]
        widgets = {
            'program_name': forms.TextInput(attrs={'id': 'id_program_name','placeholder': 'اكتب هنا'}),
            'general_idea': forms.Textarea(attrs={'id': 'id_general_idea','rows': 3, 'placeholder': 'اكتب هنا'}),
            'target_audience': forms.Textarea(attrs={'id': 'id_target_audience','rows': 3, 'placeholder': 'اكتب هنا'}),
            'program_objectives': forms.Textarea(attrs={'id': 'id_program_objectives','rows': 3, 'placeholder': 'اكتب هنا'}),
            'program_type': forms.TextInput(attrs={'id': 'id_program_type','placeholder': 'اكتب هنا'}),
            'program_duration': forms.TextInput(attrs={'id': 'id_program_duration','placeholder': 'اكتب هنا'}),
            'episode_count': forms.TextInput(attrs={'id': 'id_episode_count','placeholder': 'اكتب هنا'}),
            'filming_location': forms.Textarea(attrs={'id': 'id_filming_location','rows': 3, 'placeholder': 'اكتب هنا'}),
        }
        labels = {
            'program_name': 'اسم البرنامج:',
            'general_idea': 'الفكرة العامة:',
            'target_audience': 'الجمهور المستهدف:',
            'program_objectives': 'أهداف البرنامج:',
            'program_type': 'نوع البرنامج:',
            'program_duration': 'مدة البرنامج:',
            'episode_count': 'عدد الحلقات:',
            'filming_location': 'موقع أو أسلوب التصوير:',
        }

# Add this to program_ideation/forms.py

class IdeaNoteForm(forms.ModelForm):
    """Form for adding notes to idea fields."""
    class Meta:
        model = IdeaNote
        fields = ['field_name', 'note_content']
        widgets = {
            'field_name': forms.Select(attrs={'class': 'form-select'}),
            'note_content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your note or enhancement request...'}),
        }
    
    def __init__(self, *args, **kwargs):
        idea = kwargs.pop('idea', None)
        language = kwargs.pop('language', 'en')
        super().__init__(*args, **kwargs)
        
        if idea:
            self.instance.idea = idea
        
        # Translate field choices based on language
        if language == 'ar':
            # Define Arabic field labels
            arabic_choices = [
                ('program_name', 'اسم البرنامج'),
                ('general_idea', 'الفكرة العامة'),
                ('target_audience', 'الجمهور المستهدف'),
                ('program_objectives', 'أهداف البرنامج'),
                ('program_type', 'نوع البرنامج'),
                ('program_duration', 'مدة البرنامج'),
                ('episode_count', 'عدد الحلقات'),
                ('filming_location', 'موقع أو أسلوب التصوير'),
            ]
            self.fields['field_name'].choices = arabic_choices
            self.fields['field_name'].label = "الحقل"
            self.fields['note_content'].label = "الملاحظة أو طلب التحسين"
            self.fields['note_content'].widget.attrs['placeholder'] = "أدخل ملاحظتك أو طلب التحسين..."
        else:
            self.fields['field_name'].label = "Field"
            self.fields['note_content'].label = "Note or Enhancement Request"
