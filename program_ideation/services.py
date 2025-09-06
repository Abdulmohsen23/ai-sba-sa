import logging
from django.conf import settings
from askme.services import LLMService

logger = logging.getLogger(__name__)


class ProgramIdeationService:
    """Service for program ideation using LLM."""
    
    def __init__(self, language='ar'):
        self.language = language
        self.llm_service = LLMService()
    
    def get_idea_suggestions(self):
        """Get program idea suggestions."""
        if self.language == 'ar':
            prompt = """أنت مستشار إبداعي لهيئة الإذاعة والتلفزيون السعودية. اقترح 5 أفكار مبتكرة لبرامج جديدة تناسب المملكة العربية السعودية، وتتماشى مع السياق الإعلامي الحالي. ملاحظة رجاءا عدم كتابة علامة * و علامة التنصيص "".

قدم اقتراحاتك بالتنسيق التالي:

===== اسم البرنامج =====
اقتراح 1: [عنوان البرنامج المقترح الأول]
اقتراح 2: [عنوان البرنامج المقترح الثاني]
اقتراح 3: [عنوان البرنامج المقترح الثالث]
اقتراح 4: [عنوان البرنامج المقترح الرابع]
اقتراح 5: [عنوان البرنامج المقترح الخامس]

===== الفكرة العامة =====
اقتراح 1: [وصف موجز للفكرة الأولى]
اقتراح 2: [وصف موجز للفكرة الثانية]
اقتراح 3: [وصف موجز للفكرة الثالثة]
اقتراح 4: [وصف موجز للفكرة الرابعة]
اقتراح 5: [وصف موجز للفكرة الخامسة]

===== الجمهور المستهدف =====
اقتراح 1: [وصف للجمهور المستهدف للفكرة الأولى]
اقتراح 2: [وصف للجمهور المستهدف للفكرة الثانية]
اقتراح 3: [وصف للجمهور المستهدف للفكرة الثالثة]
اقتراح 4: [وصف للجمهور المستهدف للفكرة الرابعة]
اقتراح 5: [وصف للجمهور المستهدف للفكرة الخامسة]

استخدم التنسيق بالضبط كما هو موضح، مع الحفاظ على العناوين المميزة بخمسة علامات مساواة (=====) قبل وبعد اسم الحقل. لا تقدم اي اقتراح متعلق بالموسيقى !!."""
        else:
            prompt = """You are a creative consultant for the Saudi Broadcasting Authority. Suggest 5 innovative ideas for new programs suitable for the Kingdom of Saudi Arabia, in line with the current media context.

Provide your suggestions in the following format:

===== Program Name =====
Suggestion 1: [first proposed program title]
Suggestion 2: [second proposed program title]
Suggestion 3: [third proposed program title]
Suggestion 4: [fourth proposed program title]
Suggestion 5: [fifth proposed program title]

===== General Idea =====
Suggestion 1: [brief description of the first idea]
Suggestion 2: [brief description of the second idea]
Suggestion 3: [brief description of the third idea]
Suggestion 4: [brief description of the fourth idea]
Suggestion 5: [brief description of the fifth idea]

===== Target Audience =====
Suggestion 1: [description of target audience for the first idea]
Suggestion 2: [description of target audience for the second idea]
Suggestion 3: [description of target audience for the third idea]
Suggestion 4: [description of target audience for the fourth idea]
Suggestion 5: [description of target audience for the fifth idea]

Use the exact formatting as shown, keeping the headings marked with five equals signs (=====) before and after the field name."""
        
        # Use the default (first) LLM model
        model = self._get_default_model()
        
        try:
            result = self.llm_service.generate_response(
                provider=model.provider,
                model_id=model.model_id,
                prompt=prompt
            )
            
            if result['success']:
                return result['content']
            else:
                logger.error(f"Error generating idea suggestions: {result.get('error')}")
                return self._get_error_message()
        except Exception as e:
            logger.error(f"Exception in get_idea_suggestions: {str(e)}")
            return self._get_error_message()
    
    def process_initial_concept(self, concept):
        """Process initial concept and provide suggestions."""
        if self.language == 'ar':
            prompt = f"""أنت مستشار إبداعي لهيئة الإذاعة والتلفزيون السعودية. بناءً على التصور الأولي التالي، اقترح 5 عناوين مختلفة ونطاق للفكرة. ملاحظة رجاءا عدم كتابة علامة * و علامة التنصيص "".:

التصور الأولي: {concept}

قدم اقتراحاتك بالتنسيق التالي:

===== اسم البرنامج =====
اقتراح 1: [عنوان البرنامج المقترح الأول]
اقتراح 2: [عنوان البرنامج المقترح الثاني]
اقتراح 3: [عنوان البرنامج المقترح الثالث]
اقتراح 4: [عنوان البرنامج المقترح الرابع]
اقتراح 5: [عنوان البرنامج المقترح الخامس]

===== الفكرة العامة =====
اقتراح 1: [وصف موجز للفكرة الأولى]
اقتراح 2: [وصف موجز للفكرة الثانية]
اقتراح 3: [وصف موجز للفكرة الثالثة]
اقتراح 4: [وصف موجز للفكرة الرابعة]
اقتراح 5: [وصف موجز للفكرة الخامسة]

===== الجمهور المستهدف =====
اقتراح 1: [وصف للجمهور المستهدف للفكرة الأولى]
اقتراح 2: [وصف للجمهور المستهدف للفكرة الثانية]
اقتراح 3: [وصف للجمهور المستهدف للفكرة الثالثة]
اقتراح 4: [وصف للجمهور المستهدف للفكرة الرابعة]
اقتراح 5: [وصف للجمهور المستهدف للفكرة الخامسة]


استخدم التنسيق بالضبط كما هو موضح، مع الحفاظ على العناوين المميزة بخمسة علامات مساواة (=====) قبل وبعد اسم الحقل. لا تقدم اي اقتراح متعلق بالموسيقى !!."""
        else:
            prompt = f"""You are a creative consultant for the Saudi Broadcasting Authority. Based on the following initial concept, suggest different titles and scope for the idea:

Initial concept: {concept}

Provide your suggestions in the following format:

===== Program Name =====
Suggestion 1: [proposed program title]
Suggestion 2: [proposed program title]
Suggestion 3: [proposed program title]
Suggestion 4: [proposed program title]
Suggestion 5: [proposed program title]

===== General Idea =====
Suggestion 1: [brief description of the idea]
Suggestion 2: [brief description of the idea]
Suggestion 3: [brief description of the idea]

===== Target Audience =====
Suggestion 1: [description of target audience]
Suggestion 2: [description of target audience]

Use the exact formatting as shown, keeping the headings marked with five equals signs (=====) before and after the field name."""
        
        # Use the default (first) LLM model
        model = self._get_default_model()
        
        try:
            result = self.llm_service.generate_response(
                provider=model.provider,
                model_id=model.model_id,
                prompt=prompt
            )
            
            if result['success']:
                return result['content']
            else:
                logger.error(f"Error processing initial concept: {result.get('error')}")
                return self._get_error_message()
        except Exception as e:
            logger.error(f"Exception in process_initial_concept: {str(e)}")
            return self._get_error_message()
    
    def get_missing_data_proposals(self, idea):
        """Get proposals for missing data."""
        missing_fields = idea.get_missing_fields()
        
        # Translate field names to Arabic labels for prompt
        field_labels = {
            'program_name': 'اسم البرنامج',
            'general_idea': 'الفكرة العامة',
            'target_audience': 'الجمهور المستهدف',
            'program_objectives': 'أهداف البرنامج',
            'program_type': 'نوع البرنامج',
            'program_duration': 'مدة البرنامج',
            'episode_count': 'عدد الحلقات',
            'filming_location': 'موقع أو أسلوب التصوير'
        }
        
        # Create prompt based on available data
        available_data = ""
        for field in ['program_name', 'general_idea', 'target_audience', 'program_objectives', 
                      'program_type', 'program_duration', 'episode_count', 'filming_location']:
            if field not in missing_fields and getattr(idea, field):
                available_data += f"{field_labels[field]}: {getattr(idea, field)}\n"
        
        missing_fields_labels = [field_labels[field] for field in missing_fields]
        missing_fields_str = ", ".join(missing_fields_labels)
        
        if self.language == 'ar':
            prompt = f"""أنت مستشار إبداعي لهيئة الإذاعة والتلفزيون السعودية. بناءً على المعلومات المتوفرة عن فكرة البرنامج، اقترح بيانات للحقول الناقصة. ملاحظة رجاءا عدم كتابة علامة * و علامة التنصيص "".

البيانات المتوفرة:
{available_data}

الحقول الناقصة: {missing_fields_str}

قم بتقديم اقتراحات لكل حقل ناقص بالتنسيق التالي فقط للحقول الناقصة!!:

===== {field_labels[missing_fields[0]]} =====
اقتراح 1: [النص المقترح للحقل]
اقتراح 2: [النص المقترح للحقل]

{f"===== {field_labels[missing_fields[1]]} =====" if len(missing_fields) > 1 else ""}
{f"اقتراح 1: [النص المقترح للحقل]" if len(missing_fields) > 1 else ""}
{f"اقتراح 2: [النص المقترح للحقل]" if len(missing_fields) > 1 else ""}

وهكذا لباقي الحقول الناقصة. قدم اقتراحين مختلفين على الأقل لكل حقل ناقص، مع مراعاة انسجامها مع البيانات المتوفرة.

استخدم التنسيق بالضبط كما هو موضح، مع الحفاظ على العناوين المميزة بخمسة علامات مساواة (=====) قبل وبعد اسم الحقل. لا تقدم اي اقتراح متعلق بالموسيقى !!."""
        else:
            prompt = f"""You are a creative consultant for the Saudi Broadcasting Authority. Based on the available information about the program idea, suggest data for the missing fields.

Available data:
{available_data}

Missing fields: {missing_fields_str}

Provide suggestions for each missing field in the following format:

===== {field_labels[missing_fields[0]]} =====
Suggestion 1: [suggested text for the field]
Suggestion 2: [suggested text for the field]

{f"===== {field_labels[missing_fields[1]]} =====" if len(missing_fields) > 1 else ""}
{f"Suggestion 1: [suggested text for the field]" if len(missing_fields) > 1 else ""}
{f"Suggestion 2: [suggested text for the field]" if len(missing_fields) > 1 else ""}

And so on for the remaining missing fields. Provide at least two different suggestions for each missing field, ensuring consistency with the available data.

Use the exact formatting as shown, keeping the headings marked with five equals signs (=====) before and after the field name."""
        
        # Use the default (first) LLM model
        model = self._get_default_model()
        
        try:
            result = self.llm_service.generate_response(
                provider=model.provider,
                model_id=model.model_id,
                prompt=prompt
            )
            
            if result['success']:
                return result['content']
            else:
                logger.error(f"Error generating missing data proposals: {result.get('error')}")
                return self._get_error_message()
        except Exception as e:
            logger.error(f"Exception in get_missing_data_proposals: {str(e)}")
            return self._get_error_message()
    
    def generate_discussion_questions(self, idea):
        """Generate discussion questions for the idea workshop."""
        # Collect all available data about the idea
        idea_data = ""
        for field in ['program_name', 'general_idea', 'target_audience', 'program_objectives', 
                      'program_type', 'program_duration', 'episode_count', 'filming_location']:
            if getattr(idea, field):
                idea_data += f"{field}: {getattr(idea, field)}\n"
        
        if self.language == 'ar':
            prompt = f"""أنت مستشار إبداعي لهيئة الإذاعة والتلفزيون السعودية. بناءً على معلومات البرنامج المقترح، قم بإعداد أسئلة نقاش لورشة عمل لمناقشة وتطوير الفكرة.

معلومات البرنامج:
{idea_data}

قم بإعداد 10 أسئلة نقاش مهمة تساعد في:
1. استكشاف جوانب الفكرة بعمق
2. تحديد التحديات المحتملة وكيفية التغلب عليها
3. تطوير عناصر البرنامج
4. ضمان جاذبية البرنامج للجمهور المستهدف

قدم الأسئلة في تنسيق واضح ومنظم، مع تقسيمها إلى محاور مناسبة. لا تقدم اي سؤال او اقتراح متعلق بالموسيقى !!."""
        else:
            prompt = f"""You are a creative consultant for the Saudi Broadcasting Authority. Based on the proposed program information, prepare discussion questions for a workshop to discuss and develop the idea.

Program information:
{idea_data}

Prepare 10 important discussion questions that help:
1. Explore aspects of the idea in depth
2. Identify potential challenges and how to overcome them
3. Develop program elements
4. Ensure the program's appeal to the target audience

Present the questions in a clear, organized format, dividing them into appropriate axes."""
        
        # Use the default (first) LLM model
        model = self._get_default_model()
        
        try:
            result = self.llm_service.generate_response(
                provider=model.provider,
                model_id=model.model_id,
                prompt=prompt
            )
            
            if result['success']:
                return result['content']
            else:
                logger.error(f"Error generating discussion questions: {result.get('error')}")
                return self._get_error_message()
        except Exception as e:
            logger.error(f"Exception in generate_discussion_questions: {str(e)}")
            return self._get_error_message()
    
    def generate_program_format(self, idea):
        """Generate program format."""
        # Collect all available data about the idea
        idea_data = ""
        for field in ['program_name', 'general_idea', 'target_audience', 'program_objectives', 
                      'program_type', 'program_duration', 'episode_count', 'filming_location']:
            if getattr(idea, field):
                idea_data += f"{field}: {getattr(idea, field)}\n"
        
        if self.language == 'ar':
            prompt = f"""أنت مستشار إبداعي لهيئة الإذاعة والتلفزيون السعودية. بناءً على معلومات البرنامج، قم بإعداد تنسيق تفصيلي للبرنامج.

معلومات البرنامج:
{idea_data}

قم بإعداد تنسيق البرنامج متضمناً:
1. هيكل البرنامج (فقرات/أقسام)
2. تفاصيل كل فقرة وهدفها
3. التسلسل المنطقي للفقرات
4. التوقيت المقترح لكل فقرة
5. العناصر البصرية الرئيسية
6. أسلوب التقديم المقترح

قدم التنسيق بشكل تفصيلي ومنظم. لا تقدم اي اقتراح متعلق بالموسيقى !!."""
        else:
            prompt = f"""You are a creative consultant for the Saudi Broadcasting Authority. Based on the program information, prepare a detailed format for the program.

Program information:
{idea_data}

Prepare the program format including:
1. Program structure (segments/sections)
2. Details of each segment and its purpose
3. Logical sequence of segments
4. Proposed timing for each segment
5. Key visual elements
6. Proposed presentation style

Present the format in a detailed and organized manner."""
        
        # Use the default (first) LLM model
        model = self._get_default_model()
        
        try:
            result = self.llm_service.generate_response(
                provider=model.provider,
                model_id=model.model_id,
                prompt=prompt
            )
            
            if result['success']:
                return result['content']
            else:
                logger.error(f"Error generating program format: {result.get('error')}")
                return self._get_error_message()
        except Exception as e:
            logger.error(f"Exception in generate_program_format: {str(e)}")
            return self._get_error_message()
    
    def generate_program_script(self, idea):
        """Generate program script."""
        # Collect all available data about the idea
        idea_data = ""
        for field in ['program_name', 'general_idea', 'target_audience', 'program_objectives', 
                      'program_type', 'program_duration', 'episode_count', 'filming_location']:
            if getattr(idea, field):
                idea_data += f"{field}: {getattr(idea, field)}\n"
        
        if self.language == 'ar':
            prompt = f"""أنت مستشار إبداعي لهيئة الإذاعة والتلفزيون السعودية. بناءً على معلومات البرنامج، قم بإعداد نموذج لنص حلقة من البرنامج.

معلومات البرنامج:
{idea_data}

قم بإعداد نص البرنامج متضمناً:
1. مقدمة البرنامج
2. نصوص المقدم/المقدمين
3. تسلسل الفقرات
4. أمثلة للحوارات المحتملة
5. الانتقالات بين الفقرات
6. خاتمة البرنامج

اكتب النص بشكل احترافي يناسب البث التلفزيوني، مع مراعاة طبيعة البرنامج وجمهوره المستهدف. لا تقدم اي اقتراح متعلق بالموسيقى !!."""
        else:
            prompt = f"""You are a creative consultant for the Saudi Broadcasting Authority. Based on the program information, prepare a model script for an episode of the program.

Program information:
{idea_data}

Prepare the program script including:
1. Program introduction
2. Presenter(s) scripts
3. Sequence of segments
4. Examples of potential dialogues
5. Transitions between segments
6. Program conclusion

Write the script professionally, suitable for television broadcasting, taking into account the nature of the program and its target audience."""
        
        # Use the default (first) LLM model
        model = self._get_default_model()
        
        try:
            result = self.llm_service.generate_response(
                provider=model.provider,
                model_id=model.model_id,
                prompt=prompt
            )
            
            if result['success']:
                return result['content']
            else:
                logger.error(f"Error generating program script: {result.get('error')}")
                return self._get_error_message()
        except Exception as e:
            logger.error(f"Exception in generate_program_script: {str(e)}")
            return self._get_error_message()
    
    def generate_visual_proposals(self, idea):
        """Generate visual material proposals."""
        # Collect all available data about the idea
        idea_data = ""
        for field in ['program_name', 'general_idea', 'target_audience', 'program_objectives', 
                      'program_type', 'program_duration', 'episode_count', 'filming_location']:
            if getattr(idea, field):
                idea_data += f"{field}: {getattr(idea, field)}\n"
        
        if self.language == 'ar':
            prompt = f"""أنت مستشار إبداعي لهيئة الإذاعة والتلفزيون السعودية. بناءً على معلومات البرنامج، قم بتقديم مقترحات للمواد البصرية للبرنامج.

معلومات البرنامج:
{idea_data}

قدم مقترحات مفصلة للعناصر البصرية التالية:
1. شعار البرنامج (وصف التصميم، الألوان، العناصر)
2. تصميم الاستوديو/موقع التصوير (الديكور، الإضاءة، الأثاث)
3. الجرافيكس (أسلوب، ألوان، عناصر متحركة)
4. الفواصل والمقدمة (وصف أسلوب التصوير،الأسلوب)
5. العناصر البصرية الفريدة التي تميز البرنامج

قدم المقترحات بشكل تفصيلي مع مراعاة طبيعة البرنامج وجمهوره المستهدف. لا تقدم اي اقتراح متعلق بالموسيقى !!."""
        else:
            prompt = f"""You are a creative consultant for the Saudi Broadcasting Authority. Based on the program information, provide proposals for the visual materials of the program.

Program information:
{idea_data}

Provide detailed proposals for the following visual elements:
1. Program logo (design description, colors, elements)
2. Studio/filming location design (decor, lighting, furniture)
3. Graphics (style, colors, moving elements)
4. Breaks and introduction (description of filming style, style)
5. Unique visual elements that distinguish the program

Present the proposals in detail, taking into account the nature of the program and its target audience."""
        
        # Use the default (first) LLM model
        model = self._get_default_model()
        
        try:
            result = self.llm_service.generate_response(
                provider=model.provider,
                model_id=model.model_id,
                prompt=prompt
            )
            
            if result['success']:
                return result['content']
            else:
                logger.error(f"Error generating visual proposals: {result.get('error')}")
                return self._get_error_message()
        except Exception as e:
            logger.error(f"Exception in generate_visual_proposals: {str(e)}")
            return self._get_error_message()
    
    def process_idea_note(self, note):
        """Process a note and generate enhancement suggestions."""
        # Get the field content
        idea = note.idea
        field_name = note.field_name
        field_content = getattr(idea, field_name, "")
        
        # Get field label
        field_label = note.get_field_name_display()
        if self.language == 'ar':
            field_label = note.get_field_label_arabic()
        
        # Prepare prompt based on language
        if self.language == 'ar':
            prompt = f"""أنت مستشار إبداعي لهيئة الإذاعة والتلفزيون السعودية. المستخدم يرغب في تحسين محتوى حقل. ملاحظة رجاءا عدم كتابة علامة * و علامة التنصيص "". "{field_label}" في فكرة برنامج.

المحتوى الحالي: {field_content}

ملاحظة المستخدم: {note.note_content}

قدم اقتراحات لتحسين هذا الحقل بناءً على ملاحظة المستخدم بالتنسيق التالي:

===== {field_label} =====
اقتراح 1: [النص المقترح للحقل]
اقتراح 2: [النص المقترح للحقل]
اقتراح 3: [النص المقترح للحقل]

كل اقتراح يجب أن يكون مستقلاً بذاته ويمكن استخدامه مباشرة كمحتوى جديد للحقل.
استخدم التنسيق بالضبط كما هو موضح، مع الحفاظ على العنوان المميز بخمسة علامات مساواة (=====) قبل وبعد اسم الحقل. لا تقدم اي اقتراح متعلق بالموسيقى !!."""
        else:
            prompt = f"""You are a creative consultant for the Saudi Broadcasting Authority. The user wants to enhance the content of the "{field_label}" field in a program idea.

Current content: {field_content}

User's note: {note.note_content}

Provide suggestions to enhance this field based on the user's note using the following format:

===== {field_label} =====
Suggestion 1: [suggested text for the field]
Suggestion 2: [suggested text for the field]
Suggestion 3: [suggested text for the field]

Each suggestion should be self-contained and can be used directly as new content for the field.
Use the exact formatting as shown, keeping the heading marked with five equals signs (=====) before and after the field name."""
        
        # Use the default model
        model = self._get_default_model()
        
        try:
            result = self.llm_service.generate_response(
                provider=model.provider,
                model_id=model.model_id,
                prompt=prompt
            )
            
            if result['success']:
                return result['content']
            else:
                logger.error(f"Error processing note: {result.get('error')}")
                return self._get_error_message()
        except Exception as e:
            logger.error(f"Exception in process_idea_note: {str(e)}")
            return self._get_error_message()
    
    def _get_default_model(self):
        """Get the default LLM model to use."""
        from askme.models import LLMModel
        
        # Try to get a model that's meant for this type of creative work
        try:
            # First try to get an active DeepSeek model specifically
            model = LLMModel.objects.filter(is_active=True, provider__iexact='OpenAI').first()
            
            if not model:
                # Then try OpenAI as fallback 
                model = LLMModel.objects.filter(is_active=True, provider__iexact='deepseek').first()
                
            if not model:
                # Fall back to any active model
                model = LLMModel.objects.filter(is_active=True).first()
                
            if not model:
                # If no active models, get any model
                model = LLMModel.objects.first()
            
            # Log which model we're using (helpful for debugging)
            if model:
                logger.info(f"Program Ideation using model: {model.name} ({model.provider})")
            
            return model
        except Exception as e:
            logger.error(f"Error getting default model: {str(e)}")
            # Return a mock model for emergency fallback
            from types import SimpleNamespace
            return SimpleNamespace(provider='Mock', model_id='mock-model')

    # Update your program_ideation/services.py - Enhanced _get_default_model method

    # def _get_default_model(self):
    #     """Get the default LLM model with GPT-5 as priority."""
    #     from askme.models import LLMModel
    #     from django.utils import timezone
        
    #     try:
    #         # Updated model preferences with GPT-5 as top priority
    #         model_preferences = [
    #             {'provider': 'openai', 'model_prefix': 'gpt-5', 'reliable': True, 'priority': 2},      # GPT-5 family
    #             {'provider': 'openai', 'model_prefix': 'gpt-4', 'reliable': True, 'priority': 3},      # GPT-4 family fallback
    #             {'provider': 'anthropic', 'reliable': True, 'priority': 4},                            # Claude fallback
    #             {'provider': 'deepseek', 'reliable': False, 'priority': 1},                           # DeepSeek (slow)
    #         ]
            
    #         for preference in model_preferences:
    #             # Build query filters
    #             filters = {'is_active': True, 'provider__iexact': preference['provider']}
                
    #             # If there's a model prefix (like gpt-5), prioritize those models
    #             if 'model_prefix' in preference:
    #                 models = LLMModel.objects.filter(
    #                     **filters,
    #                     model_id__startswith=preference['model_prefix']
    #                 ).order_by('name')
                    
    #                 if models.exists():
    #                     model = models.first()
    #                     logger.info(f"Using preferred model: {model.name} ({model.provider}/{model.model_id})")
    #                     return model
                
    #             # Fall back to any model from this provider
    #             model = LLMModel.objects.filter(**filters).first()
    #             if model:
    #                 if preference.get('reliable', True):
    #                     logger.info(f"Using reliable model: {model.name} ({model.provider})")
    #                 else:
    #                     logger.warning(f"Using less reliable model: {model.name} ({model.provider}) - may have timeout issues")
    #                 return model
            
    #         # Final fallbacks
    #         model = LLMModel.objects.filter(is_active=True).first()
    #         if model:
    #             logger.info(f"Fallback to available model: {model.name} ({model.provider})")
    #             return model
                
    #         model = LLMModel.objects.first()
    #         if model:
    #             logger.warning(f"Last resort model: {model.name} ({model.provider})")
    #             return model
            
    #         # Emergency mock model
    #         logger.error("No LLM models found - using mock model")
    #         from types import SimpleNamespace
    #         return SimpleNamespace(provider='Mock', model_id='mock-model', name='Emergency Mock Model')
            
    #     except Exception as e:
    #         logger.error(f"Error getting default model: {str(e)}")
    #         from types import SimpleNamespace
    #         return SimpleNamespace(provider='Mock', model_id='mock-model', name='Error Fallback Mock Model')
    
    def _get_error_message(self):
        """Get error message based on language."""
        if self.language == 'ar':
            return "عذراً، حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى لاحقاً."
        else:
            return "Sorry, an error occurred while processing your request. Please try again later."
        
        # 3. UPDATE services.py - Add this method to ProgramIdeationService class
    # ============================================

    def process_multi_field_note(self, note):
        """Process a note that references multiple fields."""
        idea = note.idea
        
        # Get all fields associated with this note
        fields_info = []
        for field in note.note_fields.all():
            field_label = field.get_field_label_arabic() if self.language == 'ar' else field.get_field_name_display()
            fields_info.append(f"{field_label}: {field.current_content or '(فارغ)' if self.language == 'ar' else '(Empty)'}")
        
        fields_text = "\n".join(fields_info)
        
        if self.language == 'ar':
            prompt = f"""أنت مستشار إبداعي لهيئة الإذاعة والتلفزيون السعودية. ملاحظة رجاءا عدم كتابة علامة * و علامة التنصيص "". 
                                                        
    المستخدم لديه ملاحظة على عدة حقول من فكرة البرنامج:

    الحقول المعنية:
    {fields_text}

    ملاحظة المستخدم: {note.note_content}

    قدم اقتراحات تحسين منفصلة لكل حقل معني بالملاحظة، مع مراعاة العلاقة بين الحقول. فقط للحقول المعنية.

    استخدم التنسيق التالي لكل حقل:

    ===== [اسم الحقل] =====
    اقتراح 1: [النص المقترح للحقل]
    اقتراح 2: [النص المقترح للحقل]
    اقتراح 3: [النص المقترح للحقل]

    استخدم التنسيق بالضبط كما هو موضح، مع الحفاظ على العناوين المميزة بخمسة علامات مساواة. لا تقدم اي اقتراح متعلق بالموسيقى !!."""
        else:
            prompt = f"""You are a creative consultant for the Saudi Broadcasting Authority.

    The user has a note on multiple fields of a program idea:

    Related fields:
    {fields_text}

    Note type: {note.get_note_type_display() if hasattr(note, 'get_note_type_display') else 'Enhancement'}
    Priority: {note.get_priority_display() if hasattr(note, 'get_priority_display') else 'Medium'}

    User's note: {note.note_content}

    Provide separate improvement suggestions for each field mentioned in the note, considering the relationship between fields.

    Use the following format for each field:

    ===== [Field Name] =====
    Suggestion 1: [suggested text for the field]
    Suggestion 2: [suggested text for the field]
    Suggestion 3: [suggested text for the field]

    Use the exact formatting as shown, keeping the headings marked with five equals signs."""
        
        # Get LLM response
        model = self._get_default_model()
        
        try:
            result = self.llm_service.generate_response(
                provider=model.provider,
                model_id=model.model_id,
                prompt=prompt
            )
            
            if result['success']:
                return result['content']
            else:
                return self._get_error_message()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Exception in process_multi_field_note: {str(e)}")
            return self._get_error_message()