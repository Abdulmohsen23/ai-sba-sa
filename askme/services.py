import time
import logging
from django.conf import settings
from .file_utils import extract_text_from_file

logger = logging.getLogger(__name__)

class ContentFilterService:
    """Service to check for sensitive content."""
    
    @staticmethod
    def check_sensitive_content(text):
        """
        Check if the text contains sensitive content
        Returns tuple (is_sensitive, details)
        """
        # Basic implementation - for a production system, use a more robust solution
        sensitive_keywords = ['password', 'credit card', 'social security', 'passport', 'id number']
        
        found_keywords = [keyword for keyword in sensitive_keywords if keyword in text.lower()]
        is_sensitive = len(found_keywords) > 0
        
        return is_sensitive, found_keywords


class LLMService:
    """Base service for LLM interactions."""
    
    def __init__(self):
        pass
    
    def generate_response(self, provider, model_id, prompt, conversation_id=None, file_path=None, file_type=None):
        """Generate response using the appropriate LLM provider."""
        start_time = time.time()
        
        try:
            # Process file if provided
            file_content = ""
            if file_path and file_type:
                file_content = extract_text_from_file(file_path, file_type)
                if file_content:
                    prompt = f"Here is a file I'm attaching:\n\n{file_content}\n\nMy question about this content: {prompt}"
            
            # Get conversation history if provided
            conversation_history = []
            if conversation_id:
                from askme.models import Question
                questions = Question.objects.filter(conversation_id=conversation_id).order_by('sequence')
                
                for q in questions:
                    if q.content == prompt:  # Skip the current question
                        continue
                    
                    # Include file content from previous questions if available
                    q_content = q.content
                    if q.file and q.file_type:
                        # Don't re-process files for history, just mention they were there
                        q_content = f"[Question with {q.file_type.upper()} file attachment]: {q.content}"
                    
                    conversation_history.append({"role": "user", "content": q_content})
                    if hasattr(q, 'response'):
                        conversation_history.append({"role": "assistant", "content": q.response.content})
            
            # Add current prompt
            messages = conversation_history + [{"role": "user", "content": prompt}]
            
            # Choose provider
            if provider.lower() == 'anthropic':
                response = self._generate_anthropic(model_id, messages)
            elif provider.lower() == 'openai':
                response = self._generate_openai(model_id, messages)
            elif provider.lower() == 'deepseek':
                response = self._generate_deepseek(model_id, messages)
            elif provider.lower() == 'mock':
                # Mock provider for development/testing
                history_summary = f" (with {len(conversation_history)//2} previous exchanges)" if conversation_history else ""
                file_summary = " with file attachment" if file_path else ""
                response = f"This is a mock response to: '{prompt[:30]}...'{history_summary}{file_summary}"
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
            processing_time = time.time() - start_time
                
            return {
                'content': response,
                'processing_time': processing_time,
                'success': True
            }
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                'content': None,
                'processing_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    def _generate_anthropic(self, model_id, messages):
        """Generate response using Anthropic Claude."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            # Convert to Anthropic format
            response = client.messages.create(
                model=model_id,
                max_tokens=1000,
                messages=messages
            )
            
            return response.content[0].text
        except ImportError:
            logger.warning("Anthropic SDK not installed. Using mock response.")
            return f"[Mock Anthropic Response] Would respond to conversation with {len(messages)} messages"
        except Exception as e:
            logger.error(f"Error with Anthropic API: {str(e)}")
            raise
    
    # def _generate_openai(self, model_id, messages):
    #     """Generate response using OpenAI."""
    #     try:
    #         import openai
    #         client = openai.Client(api_key=settings.OPENAI_API_KEY)
            
    #         response = client.chat.completions.create(
    #             model=model_id,
    #             messages=messages,
    #             max_tokens=1000
    #         )
            
    #         return response.choices[0].message.content
    #     except ImportError:
    #         logger.warning("OpenAI SDK not installed. Using mock response.")
    #         return f"[Mock OpenAI Response] Would respond to conversation with {len(messages)} messages"
    #     except Exception as e:
    #         logger.error(f"Error with OpenAI API: {str(e)}")
    #         raise

    # Replace your _generate_openai method in askme/services.py with this:

    # Replace your _generate_openai method in askme/services.py with this:

    # Replace your _generate_openai method with this debugging version:

    # def _generate_openai(self, model_id, messages):
    #     """Generate response using OpenAI with detailed error debugging."""
    #     try:
    #         import requests
    #         import json
            
    #         api_key = settings.OPENAI_API_KEY
            
    #         # Debug: Log the request details
    #         logger.info(f"DEBUG: OpenAI API call starting")
    #         logger.info(f"DEBUG: Model ID: {model_id}")
    #         logger.info(f"DEBUG: API key present: {bool(api_key)}")
    #         logger.info(f"DEBUG: API key starts with 'sk-': {api_key.startswith('sk-') if api_key else False}")
    #         logger.info(f"DEBUG: Messages count: {len(messages)}")
    #         logger.info(f"DEBUG: First message: {messages[0] if messages else 'No messages'}")
            
    #         # Prepare headers with authentication
    #         headers = {
    #             "Authorization": f"Bearer {api_key}",
    #             "Content-Type": "application/json"
    #         }
            
    #         # Prepare request payload
    #         data = {
    #             "model": model_id,
    #             "messages": messages,
    #             "max_tokens": 1000,
    #             "temperature": 0.7
    #         }
            
    #         logger.info(f"DEBUG: Request data: {json.dumps(data, indent=2)}")
            
    #         # Make API request with timeout
    #         response = requests.post(
    #             "https://api.openai.com/v1/chat/completions",
    #             headers=headers,
    #             data=json.dumps(data),
    #             timeout=60
    #         )
            
    #         logger.info(f"DEBUG: Response status: {response.status_code}")
    #         logger.info(f"DEBUG: Response headers: {dict(response.headers)}")
            
    #         # Check for errors and log the exact error
    #         if response.status_code != 200:
    #             error_text = response.text
    #             logger.error(f"DEBUG: OpenAI API error details:")
    #             logger.error(f"DEBUG: Status code: {response.status_code}")
    #             logger.error(f"DEBUG: Error response: {error_text}")
                
    #             try:
    #                 error_json = response.json()
    #                 logger.error(f"DEBUG: Error JSON: {json.dumps(error_json, indent=2)}")
    #             except:
    #                 logger.error(f"DEBUG: Could not parse error as JSON")
                
    #             return f"[OpenAI API Error {response.status_code}] {error_text[:200]}..."
            
    #         # Parse response
    #         response_data = response.json()
    #         logger.info(f"DEBUG: Successful response received")
            
    #         if 'choices' not in response_data or not response_data['choices']:
    #             logger.error(f"DEBUG: Invalid response structure: {response_data}")
    #             return f"[OpenAI Invalid Response] Mock response for {len(messages)} messages"
                
    #         return response_data["choices"][0]["message"]["content"]
        
    #     except Exception as e:
    #         logger.error(f"DEBUG: Exception in OpenAI call: {str(e)}")
    #         import traceback
    #         logger.error(f"DEBUG: Full traceback: {traceback.format_exc()}")
    #         return f"[OpenAI Exception] {str(e)}"

    # Replace your _generate_openai method with this corrected version:

    # Replace your _generate_openai method with this GPT-5 compatible version:

    # Update your _generate_openai method to debug the response content:

    # Replace your _generate_openai method with this enhanced version:

    def _generate_openai(self, model_id, messages):
        """Generate response using OpenAI with enhanced error handling."""
        try:
            import requests
            import json
            
            api_key = settings.OPENAI_API_KEY
            
            # Prepare headers with authentication
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare request payload with model-specific parameters
            data = {
                "model": model_id,
                "messages": messages
            }
            
            # Configure parameters based on model type
            if model_id.startswith('gpt-5'):
                # GPT-5 has strict parameter requirements
                data["max_completion_tokens"] = 1000
                timeout_seconds = 120  # Longer timeout for GPT-5
                logger.info(f"OpenAI API call starting for GPT-5 model: {model_id} (using default parameters, {timeout_seconds}s timeout)")
            else:
                # GPT-4 and older models support more parameters
                data["max_tokens"] = 1000
                data["temperature"] = 0.7
                timeout_seconds = 60  # Normal timeout for other models
                logger.info(f"OpenAI API call starting for model: {model_id} ({timeout_seconds}s timeout)")
            
            logger.info(f"Request data: {json.dumps(data, indent=2)}")
            logger.info(f"About to make POST request with {timeout_seconds}s timeout...")
            
            # Make API request with enhanced timeout handling
            try:
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    data=json.dumps(data),
                    timeout=timeout_seconds
                )
                logger.info(f"POST request completed. Status: {response.status_code}")
                
            except requests.exceptions.Timeout:
                logger.error(f"API request timed out after {timeout_seconds} seconds")
                return f"[{model_id} Timeout] API call exceeded {timeout_seconds} seconds"
                
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error during API call: {str(e)}")
                return f"[{model_id} Connection Error] Could not connect to OpenAI API"
                
            except Exception as e:
                logger.error(f"Unexpected error during API request: {str(e)}")
                return f"[{model_id} Request Error] {str(e)}"
            
            logger.info(f"OpenAI API call completed with status: {response.status_code}")
            
            # Check for errors
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"OpenAI API error: {response.status_code} - {error_text}")
                return f"[OpenAI API Error {response.status_code}] {error_text[:100]}..."
            
            # Parse response
            try:
                response_data = response.json()
                logger.info("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Raw response: {response.text[:500]}")
                return f"[{model_id} JSON Error] Invalid response format"
            
            if 'choices' not in response_data or not response_data['choices']:
                logger.error(f"Invalid response structure: {response_data}")
                return f"[{model_id} Invalid Response] No choices in response"
            
            # Extract the actual response content
            try:
                response_content = response_data["choices"][0]["message"]["content"]
                logger.info(f"Response content extracted successfully")
                logger.info(f"Response length: {len(response_content) if response_content else 0} characters")
                logger.info(f"Response preview: {response_content[:100] if response_content else 'EMPTY'}...")
                
                if not response_content:
                    logger.error(f"{model_id} returned empty content")
                    return f"[{model_id} Empty Response] The model returned no content"
                
                return response_content
                
            except (KeyError, IndexError) as e:
                logger.error(f"Error extracting response content: {str(e)}")
                logger.error(f"Response structure: {response_data}")
                return f"[{model_id} Extraction Error] Could not extract response content"
        
        except Exception as e:
            logger.error(f"Unexpected error in _generate_openai: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return f"[{model_id} Unexpected Error] {str(e)}"
    # Step 1: Update your askme/services.py - Enhanced OpenAI method with GPT-5 support

    # def _generate_openai(self, model_id, messages):
    #     """Generate response using OpenAI (GPT-4, GPT-5, etc.) with enhanced error handling."""
    #     try:
    #         import openai
    #         client = openai.Client(api_key=settings.OPENAI_API_KEY)
            
    #         # Enhanced parameters for GPT-5
    #         request_params = {
    #             "model": model_id,
    #             "messages": messages,
    #             "max_tokens": 1000,
    #             "temperature": 0.7,
    #             "timeout": 60  # Add timeout for reliability
    #         }
            
    #         # Add GPT-5 specific parameters if using GPT-5
    #         if model_id.startswith('gpt-5'):
    #             # GPT-5 supports reasoning_effort and verbosity parameters
    #             request_params.update({
    #                 "reasoning_effort": "medium",  # Options: minimal, low, medium, high
    #                 "verbosity": "medium"          # Options: low, medium, high
    #             })
    #             logger.info(f"Using GPT-5 model: {model_id} with enhanced parameters")
            
    #         response = client.chat.completions.create(**request_params)
            
    #         return response.choices[0].message.content
            
    #     except openai.RateLimitError:
    #         logger.warning("OpenAI rate limit hit - using fallback")
    #         return f"[OpenAI Rate Limited] Would respond to conversation with {len(messages)} messages"
    #     except openai.APITimeoutError:
    #         logger.warning("OpenAI API timeout - using fallback") 
    #         return f"[OpenAI Timeout] Would respond to conversation with {len(messages)} messages"
    #     except ImportError:
    #         logger.warning("OpenAI SDK not installed. Using mock response.")
    #         return f"[Mock OpenAI Response] Would respond to conversation with {len(messages)} messages"
    #     except Exception as e:
    #         logger.error(f"Error with OpenAI API: {str(e)}")
    #         return f"[OpenAI Error] Would respond to conversation with {len(messages)} messages"

    # def _generate_deepseek(self, model_id, messages):
    #     """Generate response using DeepSeek."""
    #     try:
    #         import requests
    #         import json
            
    #         api_key = settings.DEEPSEEK_API_KEY
            
    #         # Prepare headers with authentication
    #         headers = {
    #             "Authorization": f"Bearer {api_key}",
    #             "Content-Type": "application/json"
    #         }
            
    #         # Prepare request payload
    #         data = {
    #             "model": model_id,
    #             "messages": messages,
    #             "max_tokens": 1000
    #         }
            
    #         # Make API request
    #         response = requests.post(
    #             "https://api.deepseek.com/v1/chat/completions",
    #             headers=headers,
    #             data=json.dumps(data)
    #         )
            
    #         # Check for errors
    #         if response.status_code != 200:
    #             logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
    #             raise Exception(f"DeepSeek API error: {response.status_code}")
            
    #         # Parse response
    #         response_data = response.json()
    #         return response_data["choices"][0]["message"]["content"]
        
    #     except ImportError:
    #         logger.warning("Requests library not installed. Using mock response.")
    #         return f"[Mock DeepSeek Response] Would respond to conversation with {len(messages)} messages"
    #     except Exception as e:
    #         logger.error(f"Error with DeepSeek API: {str(e)}")
    #         raise    

    # Add this to your askme/services.py - Replace the _generate_deepseek method


    # Replace your _generate_deepseek method in askme/services.py with this:

    def _generate_deepseek(self, model_id, messages):
        """Generate response using DeepSeek with strict timeout handling."""
        try:
            import requests
            import json
            
            api_key = settings.DEEPSEEK_API_KEY
            
            # Prepare headers with authentication
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare request payload
            data = {
                "model": model_id,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            logger.info(f"🔍 DeepSeek API call starting for model: {model_id}")
            
            # Make API request with STRICT 30-second timeout
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                data=json.dumps(data),
                timeout=30  # STRICT 30-second timeout
            )
            
            logger.info(f"✅ DeepSeek API call completed with status: {response.status_code}")
            
            # Check for errors
            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return f"[DeepSeek API Error {response.status_code}] Mock response for {len(messages)} messages"
            
            # Parse response
            response_data = response.json()
            
            if 'choices' not in response_data or not response_data['choices']:
                logger.error(f"DeepSeek API returned invalid response: {response_data}")
                return f"[DeepSeek Invalid Response] Mock response for {len(messages)} messages"
                
            return response_data["choices"][0]["message"]["content"]
        
        except requests.exceptions.Timeout:
            logger.warning("⏰ DeepSeek API timeout (30s) - using mock response")
            return f"[DeepSeek Timeout] This is a mock response for your Program Ideation request. DeepSeek API took too long to respond."
        
        except requests.exceptions.ConnectionError:
            logger.warning("🌐 DeepSeek API connection error - using mock response")
            return f"[DeepSeek Connection Error] Mock response for {len(messages)} messages"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"🚨 DeepSeek API request error: {str(e)}")
            return f"[DeepSeek Request Error] Mock response for {len(messages)} messages"
            
        except json.JSONDecodeError as e:
            logger.error(f"🚨 DeepSeek API JSON decode error: {str(e)}")
            return f"[DeepSeek JSON Error] Mock response for {len(messages)} messages"
            
        except Exception as e:
            logger.error(f"🚨 DeepSeek API unexpected error: {str(e)}")
            return f"[DeepSeek Unexpected Error] Mock response for {len(messages)} messages"

    # def _generate_deepseek(self, model_id, messages):
    #     """Generate response using DeepSeek with proper timeout handling."""
    #     try:
    #         import requests
    #         import json
            
    #         api_key = settings.DEEPSEEK_API_KEY
            
    #         # Prepare headers with authentication
    #         headers = {
    #             "Authorization": f"Bearer {api_key}",
    #             "Content-Type": "application/json"
    #         }
            
    #         # Prepare request payload
    #         data = {
    #             "model": model_id,
    #             "messages": messages,
    #             "max_tokens": 1000,
    #             "temperature": 0.7,
    #             "timeout": 45  # Add timeout to the API request
    #         }
            
    #         # Make API request with timeout
    #         response = requests.post(
    #             "https://api.deepseek.com/v1/chat/completions",
    #             headers=headers,
    #             data=json.dumps(data),
    #             timeout=45  # 45 second timeout for the HTTP request
    #         )
            
    #         # Check for errors
    #         if response.status_code != 200:
    #             logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
    #             # If API fails, use mock response instead of crashing
    #             return f"[DeepSeek API Error - Using Mock] Would respond to conversation with {len(messages)} messages"
            
    #         # Parse response
    #         response_data = response.json()
            
    #         if 'choices' not in response_data or not response_data['choices']:
    #             logger.error(f"DeepSeek API returned invalid response: {response_data}")
    #             return f"[DeepSeek API Invalid Response - Using Mock] Would respond to conversation with {len(messages)} messages"
                
    #         return response_data["choices"][0]["message"]["content"]
        
    #     except requests.exceptions.Timeout:
    #         logger.warning("DeepSeek API timeout - using mock response")
    #         return f"[DeepSeek Timeout - Using Mock] Would respond to conversation with {len(messages)} messages"
    #     except requests.exceptions.RequestException as e:
    #         logger.error(f"DeepSeek API request error: {str(e)}")
    #         return f"[DeepSeek Request Error - Using Mock] Would respond to conversation with {len(messages)} messages"
    #     except ImportError:
    #         logger.warning("Requests library not installed. Using mock response.")
    #         return f"[Mock DeepSeek Response] Would respond to conversation with {len(messages)} messages"
    #     except Exception as e:
    #         logger.error(f"Error with DeepSeek API: {str(e)}")
    #         return f"[DeepSeek Error - Using Mock] Would respond to conversation with {len(messages)} messages"