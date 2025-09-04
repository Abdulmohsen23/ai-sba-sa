// static/js/subtitle_editor.js
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const subtitleList = document.getElementById('subtitle-list');
    const videoPlayer = document.getElementById('video-player');
    const subtitleDisplay = document.getElementById('subtitle-display');
    const timelineBar = document.getElementById('timeline-bar');
    const timelineMarkers = document.getElementById('timeline-markers');
    const editorContainer = document.getElementById('subtitle-editor-container');
    const stylingOptions = document.getElementById('styling-options');
    const playPauseBtn = document.getElementById('playPauseBtn');
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    
    // State
    let subtitles = [];
    let currentSubtitle = null;
    let hasUnsavedChanges = false;
    
    // Fetch subtitles
    fetch(`/translation/api/projects/${projectId}/subtitles/`)
        .then(response => response.json())
        .then(data => {
            subtitles = data;
            renderSubtitleList();
            renderTimelineMarkers();
        })
        .catch(error => {
            console.error('Error loading subtitles:', error);
            subtitleList.innerHTML = '<div class="alert alert-danger m-2">Failed to load subtitles</div>';
        });
    
    // Format time (seconds to MM:SS.ms)
    function formatTime(seconds) {
        const min = Math.floor(seconds / 60);
        const sec = Math.floor(seconds % 60);
        const ms = Math.floor((seconds % 1) * 1000);
        return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}.${ms.toString().padStart(3, '0')}`;
    }
    
    // Render subtitle list
    function renderSubtitleList() {
        let html = '';
        
        // Determine which text to display in the sidebar
        const isTranslateMode = document.body.dataset.translationMode === 'translate';
        const showTranslated = isTranslateMode && projectLanguage === 'ar';
        
        subtitles.forEach((subtitle, index) => {
            const startTime = formatTime(subtitle.start_time);
            const endTime = formatTime(subtitle.end_time);
            
            // Use the same text that's being shown in the video
            const displayText = showTranslated && subtitle.translated_text ? 
                subtitle.translated_text : subtitle.original_text;
            
            html += `
                <div class="subtitle-item" data-index="${index}">
                    <div class="subtitle-time">${startTime} - ${endTime}</div>
                    <div class="subtitle-text">${displayText}</div>
                </div>
            `;
        });
        
        subtitleList.innerHTML = html;
        
        // Add event listeners
        document.querySelectorAll('.subtitle-item').forEach(item => {
            item.addEventListener('click', function() {
                // Check for unsaved changes
                if (hasUnsavedChanges && currentSubtitle) {
                    if (confirm("You have unsaved changes. Save them now?")) {
                        saveSubtitleChanges();
                    }
                    hasUnsavedChanges = false;
                }
                
                // Get index and load subtitle
                const index = parseInt(this.dataset.index);
                loadSubtitle(index);
                
                // Set active class
                document.querySelectorAll('.subtitle-item').forEach(el => {
                    el.classList.remove('active');
                });
                this.classList.add('active');
                
                // Jump to this point in video
                videoPlayer.currentTime = subtitles[index].start_time;
            });
        });
    }
    
    // Render timeline markers
    function renderTimelineMarkers() {
        if (!videoPlayer.duration) {
            videoPlayer.addEventListener('loadedmetadata', renderTimelineMarkers);
            return;
        }
        
        const duration = videoPlayer.duration;
        timelineMarkers.innerHTML = '';
        
        subtitles.forEach(subtitle => {
            const startPercent = (subtitle.start_time / duration) * 100;
            const endPercent = (subtitle.end_time / duration) * 100;
            const width = endPercent - startPercent;
            
            const marker = document.createElement('div');
            marker.className = 'timeline-marker';
            marker.style.left = `${startPercent}%`;
            marker.style.width = `${width}%`;
            timelineMarkers.appendChild(marker);
        });
    }
    
    // Load subtitle for editing
    function loadSubtitle(index) {
        currentSubtitle = subtitles[index];
        
        // Show editor
        stylingOptions.style.display = 'block';
        
        // Update editor form
        editorContainer.innerHTML = `
            <div class="mb-3">
                <label class="form-label">Original Text (${projectLanguage === 'ar' ? 'Arabic' : 'English'})</label>
                <textarea class="form-control" id="edit-original" rows="2">${currentSubtitle.original_text}</textarea>
            </div>
            ${currentSubtitle.translated_text !== null ? `
            <div class="mb-3">
                <label class="form-label">Translated Text (${projectLanguage === 'ar' ? 'English' : 'Arabic'})</label>
                <textarea class="form-control" id="edit-translated" rows="2">${currentSubtitle.translated_text || ''}</textarea>
            </div>
            ` : ''}
            <button class="btn btn-primary btn-sm w-100" id="save-subtitle">
                <i class="bi bi-save me-1"></i> Save Changes
            </button>
        `;
        
        // Add save event listener
        document.getElementById('save-subtitle').addEventListener('click', saveSubtitleChanges);
        
        // Add change event listeners to detect unsaved changes
        document.getElementById('edit-original').addEventListener('input', function() {
            hasUnsavedChanges = true;
        });
        
        const translatedEl = document.getElementById('edit-translated');
        if (translatedEl) {
            translatedEl.addEventListener('input', function() {
                hasUnsavedChanges = true;
            });
        }
        
        // Update styling controls to match current subtitle
        updateStylingControls();
    }
    
    // Update styling controls to match current subtitle
    function updateStylingControls() {
        if (!currentSubtitle) return;
        
        // Set values for all controls
        document.getElementById('font-family').value = currentSubtitle.font_family;
        document.getElementById('font-size').value = currentSubtitle.font_size;
        document.getElementById('font-size-value').textContent = `${currentSubtitle.font_size}px`;
        document.getElementById('text-color').value = currentSubtitle.font_color;
        document.getElementById('bg-color').value = currentSubtitle.background_color;
        document.getElementById('bg-opacity').value = currentSubtitle.background_opacity;
        document.getElementById('opacity-value').textContent = `${Math.round(currentSubtitle.background_opacity * 100)}%`;
        
        // Toggle styling buttons
        document.getElementById('btn-bold').classList.toggle('active', currentSubtitle.is_bold);
        document.getElementById('btn-italic').classList.toggle('active', currentSubtitle.is_italic);
        document.getElementById('btn-underline').classList.toggle('active', currentSubtitle.is_underline);
        
        // Set alignment
        document.querySelectorAll('[data-align]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.align === currentSubtitle.alignment);
        });
    }
    
    // Save subtitle changes
    function saveSubtitleChanges() {
        if (!currentSubtitle) return;
        
        // Show saving indicator
        showToast('Saving changes...', 'info');
        
        // Get values from form
        const originalText = document.getElementById('edit-original').value;
        const translatedEl = document.getElementById('edit-translated');
        const translatedText = translatedEl ? translatedEl.value : null;
        
        // Prepare data for sending
        const data = {
            id: currentSubtitle.id,
            original_text: originalText
        };
        
        if (translatedText !== null) {
            data.translated_text = translatedText;
        }
        
        // Include styling data
        data.font_family = document.getElementById('font-family').value;
        data.font_size = parseInt(document.getElementById('font-size').value);
        data.font_color = document.getElementById('text-color').value;
        data.background_color = document.getElementById('bg-color').value;
        data.background_opacity = parseFloat(document.getElementById('bg-opacity').value);
        data.is_bold = document.getElementById('btn-bold').classList.contains('active');
        data.is_italic = document.getElementById('btn-italic').classList.contains('active');
        data.is_underline = document.getElementById('btn-underline').classList.contains('active');
        
        // Get alignment
        document.querySelectorAll('[data-align]').forEach(btn => {
            if (btn.classList.contains('active')) {
                data.alignment = btn.dataset.align;
            }
        });
        
        // Update subtitle object with new values
        currentSubtitle.original_text = originalText;
        if (translatedText !== null) {
            currentSubtitle.translated_text = translatedText;
        }
        currentSubtitle.font_family = data.font_family;
        currentSubtitle.font_size = data.font_size;
        currentSubtitle.font_color = data.font_color;
        currentSubtitle.background_color = data.background_color;
        currentSubtitle.background_opacity = data.background_opacity;
        currentSubtitle.is_bold = data.is_bold;
        currentSubtitle.is_italic = data.is_italic;
        currentSubtitle.is_underline = data.is_underline;
        currentSubtitle.alignment = data.alignment;
        
        // Update UI
        const subtitleItem = document.querySelector(`.subtitle-item[data-index="${subtitles.indexOf(currentSubtitle)}"]`);
        if (subtitleItem) {
            // Use the same logic to determine which text to show
            const isTranslateMode = document.body.dataset.translationMode === 'translate';
            const showTranslated = isTranslateMode && projectLanguage === 'ar';
            const displayText = showTranslated && currentSubtitle.translated_text ? 
                currentSubtitle.translated_text : currentSubtitle.original_text;
                
            subtitleItem.querySelector('.subtitle-text').textContent = displayText;
        }
        
        // Get CSRF token
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
        // Save to server
        fetch(`/translation/api/subtitles/${currentSubtitle.id}/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Save successful:', data);
            showToast('Subtitle updated successfully', 'success');
            hasUnsavedChanges = false;
        })
        .catch(error => {
            console.error('Error saving subtitle:', error);
            showToast('Error saving changes: ' + error.message, 'danger');
        });
    }
    
    // Video player subtitle display
    videoPlayer.addEventListener('timeupdate', function() {
        const currentTime = videoPlayer.currentTime;
        timelineBar.style.width = `${(currentTime / videoPlayer.duration) * 100}%`;
        
        // Find active subtitle
        let activeSubtitle = null;
        let activeIndex = -1;
        
        for (let i = 0; i < subtitles.length; i++) {
            if (currentTime >= subtitles[i].start_time && currentTime <= subtitles[i].end_time) {
                activeSubtitle = subtitles[i];
                activeIndex = i;
                break;
            }
        }
        
        // Update UI
        if (activeSubtitle) {
            // Display subtitle text
            // Choose translated or original text based on project settings
            const isTranslateMode = document.body.dataset.translationMode === 'translate';
            const showTranslated = isTranslateMode && projectLanguage === 'ar';
            
            subtitleDisplay.innerHTML = showTranslated && activeSubtitle.translated_text ? 
                activeSubtitle.translated_text : activeSubtitle.original_text;
            
            // Apply styling
            subtitleDisplay.style.fontFamily = activeSubtitle.font_family || 'Arial';
            subtitleDisplay.style.fontSize = `${activeSubtitle.font_size || 32}px`;
            subtitleDisplay.style.color = activeSubtitle.font_color || '#FFFFFF';
            subtitleDisplay.style.backgroundColor = activeSubtitle.background_color 
                ? `${activeSubtitle.background_color}${Math.round(activeSubtitle.background_opacity * 255).toString(16).padStart(2, '0')}` 
                : 'transparent';
            subtitleDisplay.style.fontWeight = activeSubtitle.is_bold ? 'bold' : 'normal';
            subtitleDisplay.style.fontStyle = activeSubtitle.is_italic ? 'italic' : 'normal';
            subtitleDisplay.style.textDecoration = activeSubtitle.is_underline ? 'underline' : 'none';
            subtitleDisplay.style.textAlign = activeSubtitle.alignment || 'center';
            
            // Highlight in list
            document.querySelectorAll('.subtitle-item').forEach((el, idx) => {
                el.classList.toggle('active', idx === activeIndex);
            });
            
            // Auto-scroll to active subtitle in list
            const activeElement = document.querySelector(`.subtitle-item.active`);
            if (activeElement) {
                activeElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        } else {
            // Clear display when no subtitle is active
            subtitleDisplay.innerHTML = '';
            
            // Remove highlight from list
            document.querySelectorAll('.subtitle-item').forEach(el => {
                el.classList.remove('active');
            });
        }
    });
    
    // Handle page unload with unsaved changes
    window.addEventListener('beforeunload', function(e) {
        if (hasUnsavedChanges) {
            // This will trigger a browser confirmation dialog
            e.preventDefault();
            e.returnValue = '';
            return '';
        }
    });
    
    // Video controls
    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', function() {
            if (videoPlayer.paused) {
                videoPlayer.play();
                this.innerHTML = '<i class="bi bi-pause-fill"></i>';
            } else {
                videoPlayer.pause();
                this.innerHTML = '<i class="bi bi-play-fill"></i>';
            }
        });
    }
    
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', function() {
            if (videoPlayer.requestFullscreen) {
                videoPlayer.requestFullscreen();
            } else if (videoPlayer.webkitRequestFullscreen) { /* Safari */
                videoPlayer.webkitRequestFullscreen();
            } else if (videoPlayer.msRequestFullscreen) { /* IE11 */
                videoPlayer.msRequestFullscreen();
            }
        });
    }
    
    // Styling control event listeners
    document.getElementById('font-family').addEventListener('change', function() {
        if (currentSubtitle) {
            currentSubtitle.font_family = this.value;
            hasUnsavedChanges = true;
        }
    });
    
    document.getElementById('font-size').addEventListener('input', function() {
        document.getElementById('font-size-value').textContent = `${this.value}px`;
        if (currentSubtitle) {
            currentSubtitle.font_size = parseInt(this.value);
            hasUnsavedChanges = true;
        }
    });
    
    document.getElementById('text-color').addEventListener('change', function() {
        if (currentSubtitle) {
            currentSubtitle.font_color = this.value;
            hasUnsavedChanges = true;
        }
    });
    
    document.getElementById('bg-color').addEventListener('change', function() {
        if (currentSubtitle) {
            currentSubtitle.background_color = this.value;
            hasUnsavedChanges = true;
        }
    });
    
    document.getElementById('bg-opacity').addEventListener('input', function() {
        document.getElementById('opacity-value').textContent = `${Math.round(this.value * 100)}%`;
        if (currentSubtitle) {
            currentSubtitle.background_opacity = parseFloat(this.value);
            hasUnsavedChanges = true;
        }
    });
    
    // Toggle styling buttons
    document.getElementById('btn-bold').addEventListener('click', function() {
        this.classList.toggle('active');
        if (currentSubtitle) {
            currentSubtitle.is_bold = this.classList.contains('active');
            hasUnsavedChanges = true;
        }
    });
    
    document.getElementById('btn-italic').addEventListener('click', function() {
        this.classList.toggle('active');
        if (currentSubtitle) {
            currentSubtitle.is_italic = this.classList.contains('active');
            hasUnsavedChanges = true;
        }
    });
    
    document.getElementById('btn-underline').addEventListener('click', function() {
        this.classList.toggle('active');
        if (currentSubtitle) {
            currentSubtitle.is_underline = this.classList.contains('active');
            hasUnsavedChanges = true;
        }
    });
    
    // Text alignment buttons
    document.querySelectorAll('[data-align]').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('[data-align]').forEach(el => {
                el.classList.remove('active');
            });
            this.classList.add('active');
            
            if (currentSubtitle) {
                currentSubtitle.alignment = this.dataset.align;
                hasUnsavedChanges = true;
            }
        });
    });
    
    // Save all changes and download video
    document.getElementById('save-all-and-download').addEventListener('click', function() {
        showToast('Saving all changes...', 'info');
        
        // First save current subtitle if there are unsaved changes
        if (hasUnsavedChanges && currentSubtitle) {
            saveSubtitleChanges();
        }
        
        // Prepare data for all subtitles
        const allSubtitlesData = subtitles.map(subtitle => ({
            id: subtitle.id,
            original_text: subtitle.original_text,
            translated_text: subtitle.translated_text,
            font_family: subtitle.font_family,
            font_size: subtitle.font_size,
            font_color: subtitle.font_color,
            background_color: subtitle.background_color,
            background_opacity: subtitle.background_opacity,
            is_bold: subtitle.is_bold,
            is_italic: subtitle.is_italic,
            is_underline: subtitle.is_underline,
            alignment: subtitle.alignment
        }));
        
        // Get CSRF token
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
        // Save all subtitles
        fetch(`/translation/api/projects/${projectId}/save-all-subtitles/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ subtitles: allSubtitlesData })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            showToast('All changes saved successfully!', 'success');
            hasUnsavedChanges = false;
            
            // Determine which language to use for subtitles in the video
            const isTranslateMode = document.body.dataset.translationMode === 'translate';
            const subtitleLang = isTranslateMode && projectLanguage === 'ar' ? 'translated' : 'original';
            
            // Now redirect to the download page
            window.location.href = `/translation/projects/${projectId}/direct-download/?subtitle_language=${subtitleLang}`;
        })
        .catch(error => {
            console.error('Error saving all subtitles:', error);
            showToast('Error saving changes: ' + error.message, 'danger');
        });
    });
    
    // Helper functions
    function getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }
    
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        const toastContainer = document.getElementById('toast-container') || createToastContainer();
        toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }
    
    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    }
});