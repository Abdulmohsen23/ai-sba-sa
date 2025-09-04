// shared_ideation_utils.js
// Shared utilities for program ideation templates

const IdeationUtils = {
    // Language detection
    isRTL: function() {
        return document.documentElement.lang === 'ar' || 
               document.querySelector('[dir="rtl"]') !== null;
    },
    
    // Field mapping for both languages
    fieldMapping: {
        'اسم البرنامج': 'program_name',
        'الفكرة العامة': 'general_idea',
        'الجمهور المستهدف': 'target_audience',
        'أهداف البرنامج': 'program_objectives',
        'نوع البرنامج': 'program_type',
        'مدة البرنامج': 'program_duration',
        'عدد الحلقات': 'episode_count',
        'موقع أو أسلوب التصوير': 'filming_location',
        'موقع التصوير': 'filming_location',
        'Program Name': 'program_name',
        'General Idea': 'general_idea',
        'Target Audience': 'target_audience',
        'Program Objectives': 'program_objectives',
        'Program Type': 'program_type',
        'Program Duration': 'program_duration',
        'Episode Count': 'episode_count',
        'Filming Location': 'filming_location'
    },
    
    // Get field label based on field ID
    getFieldLabel: function(fieldId) {
        const isRTL = this.isRTL();
        const labels = {
            'program_name': isRTL ? 'اسم البرنامج' : 'Program Name',
            'general_idea': isRTL ? 'الفكرة العامة' : 'General Idea',
            'target_audience': isRTL ? 'الجمهور المستهدف' : 'Target Audience',
            'program_objectives': isRTL ? 'أهداف البرنامج' : 'Program Objectives',
            'program_type': isRTL ? 'نوع البرنامج' : 'Program Type',
            'program_duration': isRTL ? 'مدة البرنامج' : 'Program Duration',
            'episode_count': isRTL ? 'عدد الحلقات' : 'Episode Count',
            'filming_location': isRTL ? 'موقع التصوير' : 'Filming Location'
        };
        return labels[fieldId] || fieldId;
    },
    
    // Parse suggestions from LLM response
    parseSections: function(content) {
        const sectionRegex = /={3,}\s*([^=]+?)\s*={3,}([\s\S]*?)(?=={3,}|$)/g;
        let match;
        const sections = [];
        
        while ((match = sectionRegex.exec(content)) !== null) {
            const fieldName = match[1].trim();
            const fieldContent = match[2].trim();
            
            if (fieldName && fieldContent) {
                sections.push({
                    fieldName: fieldName,
                    content: fieldContent,
                    fieldId: this.fieldMapping[fieldName] || this.detectFieldType(fieldName, fieldContent)
                });
            }
        }
        
        return sections;
    },
    
    // Extract individual suggestions from content
    extractSuggestions: function(content) {
        const suggestions = [];
        const lines = content.split('\n').filter(line => line.trim());
        
        // Patterns to identify suggestions
        const patterns = [
            /^(اقتراح|Suggestion)\s*\d+\s*:\s*(.+)/i,
            /^\d+\.\s*(.+)/,
            /^[-•*]\s*(.+)/,
            /\*\*(اقتراح|Suggestion)\s*\d+\*\*\s*:\s*(.+)/i
        ];
        
        let currentSuggestion = '';
        
        for (const line of lines) {
            let matched = false;
            
            for (const pattern of patterns) {
                const match = line.match(pattern);
                if (match) {
                    if (currentSuggestion) {
                        suggestions.push(currentSuggestion.trim());
                    }
                    currentSuggestion = match[match.length - 1];
                    matched = true;
                    break;
                }
            }
            
            if (!matched) {
                if (currentSuggestion) {
                    currentSuggestion += ' ' + line;
                } else if (line.trim()) {
                    currentSuggestion = line;
                }
            }
        }
        
        if (currentSuggestion) {
            suggestions.push(currentSuggestion.trim());
        }
        
        // If no suggestions found, treat the whole content as one suggestion
        if (suggestions.length === 0 && content.trim()) {
            suggestions.push(content.trim());
        }
        
        return suggestions;
    },
    
    // Detect field type from content
    detectFieldType: function(fieldName, content) {
        const nameLC = fieldName.toLowerCase();
        const contentLC = content.toLowerCase();
        
        if (nameLC.includes('name') || nameLC.includes('اسم') || nameLC.includes('title') || nameLC.includes('عنوان')) {
            return 'program_name';
        }
        if (nameLC.includes('idea') || nameLC.includes('فكرة') || nameLC.includes('concept') || contentLC.length > 200) {
            return 'general_idea';
        }
        if (nameLC.includes('audience') || nameLC.includes('جمهور') || nameLC.includes('demographic')) {
            return 'target_audience';
        }
        if (nameLC.includes('objective') || nameLC.includes('أهداف') || nameLC.includes('goal')) {
            return 'program_objectives';
        }
        if (nameLC.includes('type') || nameLC.includes('نوع') || nameLC.includes('format')) {
            return 'program_type';
        }
        if (nameLC.includes('duration') || nameLC.includes('مدة') || nameLC.includes('length')) {
            return 'program_duration';
        }
        if (nameLC.includes('episode') || nameLC.includes('حلقات') || nameLC.includes('count')) {
            return 'episode_count';
        }
        if (nameLC.includes('location') || nameLC.includes('موقع') || nameLC.includes('filming')) {
            return 'filming_location';
        }
        
        return 'program_name'; // Default
    },
    
    // Apply suggestion to form field
    applySuggestion: function(fieldId, text, buttonElement) {
        const field = document.getElementById(`id_${fieldId}`);
        
        if (field) {
            field.value = text;
            this.highlightField(field);
            
            // Mark as applied
            if (buttonElement) {
                const suggestionItem = buttonElement.closest('.suggestion-item');
                if (suggestionItem) {
                    suggestionItem.classList.add('applied');
                }
            }
            
            this.showToast(this.isRTL() ? 'تم تطبيق الاقتراح بنجاح!' : 'Suggestion applied successfully!');
            
            // Scroll to field
            field.scrollIntoView({ behavior: 'smooth', block: 'center' });
            field.focus();
            
            return true;
        } else {
            this.showToast(this.isRTL() ? 'لم يتم العثور على الحقل' : 'Field not found', 'error');
            return false;
        }
    },
    
    // Highlight field with animation
    highlightField: function(field) {
        field.style.transition = 'all 0.3s ease';
        field.style.backgroundColor = '#d4edda';
        field.style.border = '2px solid #28a745';
        
        setTimeout(() => {
            field.style.backgroundColor = '';
            field.style.border = '';
        }, 2000);
    },
    
    // Copy text to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast(this.isRTL() ? 'تم نسخ الاقتراح!' : 'Suggestion copied!');
            }).catch(() => {
                this.fallbackCopy(text);
            });
        } else {
            this.fallbackCopy(text);
        }
    },
    
    // Fallback copy method
    fallbackCopy: function(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        this.showToast(this.isRTL() ? 'تم نسخ الاقتراح!' : 'Suggestion copied!');
    },
    
    // Show toast notification
    showToast: function(message, type = 'success') {
        let toast = document.getElementById('ideation-toast');
        if (!toast) {
            // Create toast if it doesn't exist
            toast = document.createElement('div');
            toast.id = 'ideation-toast';
            toast.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: none;
                align-items: center;
                gap: 10px;
                z-index: 9999;
                color: white;
                animation: slideInUp 0.3s ease;
            `;
            document.body.appendChild(toast);
        }
        
        toast.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle-fill' : 'exclamation-circle-fill'}"></i>
            <span>${message}</span>
        `;
        toast.style.background = type === 'success' ? '#28a745' : '#dc3545';
        toast.style.display = 'flex';
        
        setTimeout(() => {
            toast.style.display = 'none';
        }, 3000);
    },
    
    // Validate field content
    validateField: function(fieldId, text) {
        // Add validation rules as needed
        if (fieldId === 'episode_count') {
            // Check if it's a valid number
            const num = parseInt(text);
            if (isNaN(num) || num < 1) {
                this.showToast(this.isRTL() ? 'عدد الحلقات يجب أن يكون رقماً صحيحاً' : 'Episode count must be a valid number', 'error');
                return false;
            }
        }
        
        if (fieldId === 'program_duration') {
            // Check if it contains a number
            if (!text.match(/\d+/)) {
                this.showToast(this.isRTL() ? 'المدة يجب أن تحتوي على رقم' : 'Duration must contain a number', 'error');
                return false;
            }
        }
        
        return true;
    },
    
    // Initialize auto-save
    initAutoSave: function(formId, callback) {
        let autoSaveTimeout;
        const form = document.getElementById(formId);
        if (!form) return;
        
        const fields = form.querySelectorAll('input, textarea, select');
        
        fields.forEach(field => {
            field.addEventListener('input', () => {
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(() => {
                    if (callback) {
                        callback(field);
                    }
                    console.log('Auto-save triggered for field:', field.name);
                }, 2000);
            });
        });
    },
    
    // Setup polling for async updates
    setupPolling: function(url, checkFunction, successCallback, interval = 5000) {
        const pollingInterval = setInterval(() => {
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    if (checkFunction(html)) {
                        clearInterval(pollingInterval);
                        if (successCallback) {
                            successCallback(html);
                        }
                    }
                })
                .catch(error => {
                    console.error('Polling error:', error);
                    clearInterval(pollingInterval);
                });
        }, interval);
        
        // Clean up on page unload
        window.addEventListener('beforeunload', () => {
            clearInterval(pollingInterval);
        });
        
        return pollingInterval;
    }
};