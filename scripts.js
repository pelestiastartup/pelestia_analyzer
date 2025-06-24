document.addEventListener('DOMContentLoaded', function() {
    // Wizard Functionality
    const wizardToggle = document.getElementById('wizard-mode-toggle');
    const wizardContainer = document.getElementById('template-wizard');
    const wizardFields = document.getElementById('wizard-fields');
    const generateBtn = document.getElementById('generate-content');
    const manualBtn = document.getElementById('manual-mode');
    const contentEditor = document.getElementById('content-editor');
    
    // Template-specific forms
    const templateForms = {
        'blog-industry-insights': [
            { type: 'text', id: 'industry', label: 'What industry are you writing about?', required: true },
            { type: 'textarea', id: 'trends', label: 'List 2-3 key trends (separate with commas)', required: true },
            { type: 'select', id: 'tone', label: 'Tone of voice', options: ['Professional', 'Conversational', 'Authoritative'], required: true }
        ],
        'social-product-feature': [
            { type: 'text', id: 'product', label: 'Product name', required: true },
            { type: 'textarea', id: 'benefits', label: 'Key benefits (one per line)', required: true },
            { type: 'select', id: 'audience', label: 'Target audience', options: ['General', 'Business', 'Youth', 'Parents'], required: true },
            { type: 'checkbox', id: 'emoji', label: 'Include emojis?', checked: true }
        ]
    };
    
    // Show/hide wizard based on toggle
    if (wizardToggle) {
        wizardToggle.addEventListener('change', function() {
            if(this.checked) {
                wizardContainer.style.display = 'block';
                contentEditor.style.display = 'none';
            } else {
                wizardContainer.style.display = 'none';
                contentEditor.style.display = 'block';
            }
        });
    }
    
    // When template changes, update the form
    document.querySelectorAll('.template-item').forEach(item => {
        item.addEventListener('click', function() {
            const templateId = this.getAttribute('onclick').match(/template=([^']+)/)[1];
            updateWizardForm(templateId);
        });
    });
    
    // Generate content from form
    if (generateBtn) {
        generateBtn.addEventListener('click', function() {
            const templateId = new URLSearchParams(window.location.search).get('template');
            generateContentFromForm(templateId);
        });
    }
    
    // Switch to manual mode
    if (manualBtn) {
        manualBtn.addEventListener('click', function() {
            wizardToggle.checked = false;
            wizardContainer.style.display = 'none';
            contentEditor.style.display = 'block';
        });
    }
    
    function updateWizardForm(templateId) {
        const formConfig = templateForms[templateId] || [];
        wizardFields.innerHTML = '';
        
        formConfig.forEach(field => {
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'wizard-field';
            
            const label = document.createElement('label');
            label.htmlFor = field.id;
            label.textContent = field.label;
            
            fieldDiv.appendChild(label);
            
            if(field.type === 'text' || field.type === 'textarea') {
                const input = document.createElement(field.type);
                input.id = field.id;
                input.name = field.id;
                input.required = field.required || false;
                if(field.type === 'textarea') {
                    input.rows = 3;
                }
                fieldDiv.appendChild(input);
            } 
            else if(field.type === 'select') {
                const select = document.createElement('select');
                select.id = field.id;
                select.name = field.id;
                select.required = field.required || false;
                
                field.options.forEach(option => {
                    const opt = document.createElement('option');
                    opt.value = option;
                    opt.textContent = option;
                    select.appendChild(opt);
                });
                
                fieldDiv.appendChild(select);
            }
            else if(field.type === 'checkbox') {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = field.id;
                checkbox.name = field.id;
                checkbox.checked = field.checked || false;
                
                fieldDiv.appendChild(checkbox);
            }
            
            wizardFields.appendChild(fieldDiv);
        });
        
        // Show wizard if enabled
        if(wizardToggle && wizardToggle.checked) {
            wizardContainer.style.display = 'block';
            contentEditor.style.display = 'none';
        }
    }
    
    function generateContentFromForm(templateId) {
        const formData = {};
        const formConfig = templateForms[templateId] || [];
        
        formConfig.forEach(field => {
            const element = document.getElementById(field.id);
            if(element) {
                if(element.type === 'checkbox') {
                    formData[field.id] = element.checked;
                } else {
                    formData[field.id] = element.value;
                }
            }
        });
        
        // Generate content based on template and form data
        let generatedContent = '';
        
        switch(templateId) {
            case 'blog-industry-insights':
                generatedContent = generateIndustryInsights(formData);
                break;
            case 'social-product-feature':
                generatedContent = generateProductFeature(formData);
                break;
            default:
                generatedContent = 'Generated content will appear here';
        }
        
        // Fill the editor and show it
        if (contentEditor) {
            contentEditor.value = generatedContent;
            if (wizardToggle) {
                wizardToggle.checked = false;
            }
            if (wizardContainer) {
                wizardContainer.style.display = 'none';
            }
            contentEditor.style.display = 'block';
        }
    }
    
    // Content generation functions
    function generateIndustryInsights(data) {
        const trends = data.trends.split(',').map(t => t.trim());
        let trendsHtml = trends.map(t => `<li>${t}</li>`).join('');
        
        return `<h1>${data.industry} Industry Insights</h1>
                <h2>Introduction</h2>
                <p>In this post, we'll explore the latest trends in ${data.industry} and how they might impact your business.</p>
                <h2>Key Trends</h2>
                <ul>${trendsHtml}</ul>
                <h2>Conclusion</h2>
                <p>To stay competitive in ${data.industry}, businesses should consider these emerging trends.</p>`;
    }
    
    function generateProductFeature(data) {
        const benefits = data.benefits.split('\n').filter(b => b.trim());
        let benefitsHtml = benefits.map(b => `<li>${b}</li>`).join('');
        const emoji = data.emoji ? '🚀 ' : '';
        
        return `<p>${emoji}<strong>Feature Spotlight: ${data.product}</strong></p>
                <p>We're excited to highlight ${data.product}, designed specifically for ${data.audience}.</p>
                <p>Key Benefits:</p>
                <ul>${benefitsHtml}</ul>
                <p>#${data.product.replace(/\s+/g, '')} #${data.audience}</p>`;
    }
    
    // Initialize with current template if wizard elements exist
    if (wizardContainer) {
        const currentTemplate = new URLSearchParams(window.location.search).get('template') || 'blog-industry-insights';
        updateWizardForm(currentTemplate);
    }

    // ----------------------------------------------------------------------
    // Content Generation Functionality
    const originalGenerateBtn = document.querySelector('.generate-btn');
    
    if (originalGenerateBtn) {
        originalGenerateBtn.addEventListener('click', async function() {
            const originalText = originalGenerateBtn.textContent;
            originalGenerateBtn.disabled = true;
            originalGenerateBtn.textContent = 'Generating...';
            
            const existingError = document.querySelector('.ai-message');
            if (existingError) {
                existingError.remove();
            }
            
            const contentType = document.getElementById('content-type').value;
            const contentTopic = document.getElementById('content-topic').value;
            const tone = document.getElementById('tone').value;
            
            if (!contentTopic.trim()) {
                const errorMsg = document.createElement('div');
                errorMsg.className = 'message ai-message';
                errorMsg.style.color = '#d9534f';
                errorMsg.textContent = 'Please enter a topic/description';
                document.querySelector('.ai-generator-form').appendChild(errorMsg);
                originalGenerateBtn.disabled = false;
                originalGenerateBtn.textContent = originalText;
                return;
            }
            
            try {
                const response = await fetch('/generate-content', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        content_type: contentType,
                        topic: contentTopic,
                        tone: tone
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                let resultsContainer = document.querySelector('.ai-results');
                
                if (!resultsContainer) {
                    resultsContainer = document.createElement('div');
                    resultsContainer.className = 'ai-results';
                    document.querySelector('.ai-generator').appendChild(resultsContainer);
                }
                
                if (data.post_text || data.hashtags || data.cta) {
                    resultsContainer.innerHTML = `
                        <h3>Generated Content</h3>
                        <div class="ai-result-item">
                            <h4>Post Text</h4>
                            <p>${data.post_text || 'No content generated'}</p>
                        </div>
                        <div class="ai-result-item">
                            <h4>Hashtags</h4>
                            <p>${data.hashtags || '#NoHashtags'}</p>
                        </div>
                        <div class="ai-result-item">
                            <h4>Call-to-Action</h4>
                            <p>${data.cta || 'No call-to-action provided'}</p>
                        </div>
                    `;
                    
                    resultsContainer.style.display = 'block';
                    resultsContainer.scrollIntoView({ 
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
                
            } catch (error) {
                console.error('Error:', error);
                const resultsContainer = document.querySelector('.ai-results') || document.querySelector('.ai-generator');
                const errorMsg = document.createElement('div');
                errorMsg.className = 'message ai-message';
                errorMsg.style.color = '#d9534f';
                errorMsg.textContent = 'Error: Could not generate content. ' + error.message;
                resultsContainer.appendChild(errorMsg);
                
                if (resultsContainer.classList.contains('ai-results')) {
                    resultsContainer.style.display = 'block';
                }
            } finally {
                originalGenerateBtn.disabled = false;
                originalGenerateBtn.textContent = originalText;
            }
        });
    }
    
    // Image Generation Functionality - Updated Version
    const generateImageBtn = document.getElementById('generateImageBtn');
    if (generateImageBtn) {
        generateImageBtn.addEventListener('click', async function() {
            const originalText = generateImageBtn.textContent;
            generateImageBtn.disabled = true;
            generateImageBtn.textContent = 'Generating...';
            
            // Clear previous results and errors
            const previewContainer = document.querySelector('.image-preview-container');
            previewContainer.innerHTML = '<div class="loading-spinner"></div>';
            
            const existingError = previewContainer.querySelector('.error-message');
            if (existingError) {
                existingError.remove();
            }
            
            const imageDesc = document.getElementById('image-description').value;
            const imageStyle = document.getElementById('image-style').value;
            
            if (!imageDesc.trim()) {
                const errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.textContent = 'Please enter an image description';
                previewContainer.appendChild(errorMsg);
                generateImageBtn.disabled = false;
                generateImageBtn.textContent = originalText;
                return;
            }
            
            try {
                // Show loading state
                previewContainer.innerHTML = `
                    <div class="loading-state">
                        <div class="spinner"></div>
                        <p>Generating your image...</p>
                    </div>
                `;
                
                const response = await fetch('/generate-image', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        description: imageDesc,
                        style: imageStyle
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.message || 'Failed to generate image');
                }
                
                const data = await response.json();
                
                if (!data.images || !data.images[0]) {
                    throw new Error('No image URL returned from server');
                }
                
                // Create image element if it doesn't exist
                let img = document.getElementById('generated-image');
                if (!img) {
                    img = document.createElement('img');
                    img.id = 'generated-image';
                    img.alt = 'Generated image preview';
                    img.style.maxWidth = '100%';
                    img.style.maxHeight = '100%';
                    previewContainer.appendChild(img);
                }
                
                // Load the image first to ensure it's valid
                await new Promise((resolve, reject) => {
                    img.onload = resolve;
                    img.onerror = () => reject(new Error('Failed to load generated image'));
                    img.src = data.images[0];
                });
                
                // Create download button
                let downloadBtn = document.getElementById('download-btn');
                if (!downloadBtn) {
                    downloadBtn = document.createElement('button');
                    downloadBtn.id = 'download-btn';
                    downloadBtn.className = 'download-btn';
                    downloadBtn.textContent = 'Download Image';
                    previewContainer.parentNode.appendChild(downloadBtn);
                    
                    downloadBtn.addEventListener('click', () => {
                        try {
                            const link = document.createElement('a');
                            link.href = img.src;
                            link.download = `pelestia-${Date.now()}.png`;
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        } catch (e) {
                            console.error('Download failed:', e);
                            alert('Could not download image. Please try again.');
                        }
                    });
                }
                
                downloadBtn.style.display = 'inline-block';
                
            } catch (error) {
                console.error('Image generation error:', error);
                previewContainer.innerHTML = `
                    <div class="error-message">
                        <p>Error: ${error.message}</p>
                        <p>Please try again with a different description.</p>
                    </div>
                `;
            } finally {
                generateImageBtn.disabled = false;
                generateImageBtn.textContent = originalText;
            }
        });
    }

    // Customer Experience Tools Functionality
    const toolCards = document.querySelectorAll('.tool-card');
    const modalOverlay = document.querySelector('.modal-overlay');
    const modalContainer = document.querySelector('.modal-container');
    const closeModalBtn = document.querySelector('.close-modal');
    
    if (toolCards.length > 0) {
        toolCards.forEach(card => {
            card.addEventListener('click', function() {
                const toolId = this.getAttribute('data-tool');
                const modalContent = document.querySelector(`#${toolId}-content`);
                
                document.querySelector('.modal-content').innerHTML = modalContent.innerHTML;
                
                modalOverlay.style.display = 'block';
                modalContainer.style.display = 'block';
                document.body.style.overflow = 'hidden';
                
                initToolJS(toolId);
            });
        });
    }
    
    function closeModal() {
        modalOverlay.style.display = 'none';
        modalContainer.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeModal);
    }
    
    function initToolJS(toolId) {
        if (toolId === 'sentiment-analyzer') {
            const analyzeBtn = document.querySelector('#analyze-sentiment');
            if (analyzeBtn) {
                analyzeBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    analyzeSentiment();
                });
            }
        }
        else if (toolId === 'journey-mapper') {
            const generateBtn = document.querySelector('#generate-journey');
            if (generateBtn) {
                generateBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    analyzeJourney();
                });
            }
        }
        else if (toolId === 'reply-generator') {
            const generateBtn = document.querySelector('#generate-reply');
            if (generateBtn) {
                generateBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    generateReply();
                });
            }
        }
        else if (toolId === 'cx-score') {
            const calculateBtn = document.querySelector('#calculate-score');
            if (calculateBtn) {
                calculateBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    calculateCXScore();
                });
            }
        }
    }
    
    async function analyzeSentiment() {
        const text = document.querySelector('#feedback-text').value;
        const includeDialect = document.querySelector('#dialect-checkbox').checked;
        const analyzeBtn = document.querySelector('#analyze-sentiment');
        const results = document.querySelector('#sentiment-results');
        
        if (!text.trim()) {
            alert('Please enter some feedback to analyze');
            return;
        }
        
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = 'Analyzing...';
        
        try {
            const response = await fetch('/analyze-sentiment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feedback_text: text,
                    include_dialect: includeDialect
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            results.innerHTML = `
                <h3>Analysis Results</h3>
                <div style="display: flex; justify-content: space-between; margin: 20px 0;">
                    <div style="text-align: center; padding: 15px; background: rgba(0,128,0,0.1); border-radius: 8px; width: 30%;">
                        <h4>Positive</h4>
                        <p style="font-size: 1.5em; font-weight: bold;">${data.sentiment.positive || 0}%</p>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255,165,0,0.1); border-radius: 8px; width: 30%;">
                        <h4>Neutral</h4>
                        <p style="font-size: 1.5em; font-weight: bold;">${data.sentiment.neutral || 0}%</p>
                    </div>
                    <div style="text-align: center; padding: 15px; background: rgba(255,0,0,0.1); border-radius: 8px; width: 30%;">
                        <h4>Negative</h4>
                        <p style="font-size: 1.5em; font-weight: bold;">${data.sentiment.negative || 0}%</p>
                    </div>
                </div>
                <h4>Detected Emotions:</h4>
                <div style="margin-bottom: 20px;">
                    ${data.emotions.map(emotion => `<span style="display: inline-block; background: #f0f0f0; padding: 5px 15px; border-radius: 20px; margin-right: 10px; margin-bottom: 10px;">${emotion}</span>`).join('')}
                </div>
                ${data.cultural_insights ? `<h4>Cultural Insights:</h4><p style="background: #f9f9f9; padding: 15px; border-radius: 8px;">${data.cultural_insights}</p>` : ''}
                <h4>Recommended Response:</h4>
                <p style="background: #f9f9f9; padding: 15px; border-radius: 8px;">${data.recommendation}</p>
                ${data.improvements ? `<h4>Suggested Improvements:</h4><p style="background: #f9f9f9; padding: 15px; border-radius: 8px;">${data.improvements}</p>` : ''}
            `;
            
            results.style.display = 'block';
            results.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
        } catch (error) {
            console.error('Error:', error);
            alert('Analysis failed: ' + error.message);
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analyze Feedback';
        }
    }
    
    async function analyzeJourney() {
        const stages = [];
        const stageElements = document.querySelectorAll('.journey-stage');
        
        stageElements.forEach(stage => {
            const name = stage.querySelector('.stage-name').value;
            const description = stage.querySelector('.stage-description').value;
            if (name && description) {
                stages.push({
                    name: name,
                    description: description
                });
            }
        });
        
        if (stages.length === 0) {
            alert('Please add at least one journey stage');
            return;
        }
        
        const analyzeBtn = document.querySelector('#generate-journey');
        const results = document.querySelector('#journey-results');
        
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = 'Analyzing...';
        
        try {
            const response = await fetch('/analyze-customer-journey', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    stages: stages
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            let resultsHTML = '<h3>Journey Analysis</h3>';
            
            if (data.friction_points && data.friction_points.length > 0) {
                resultsHTML += `
                    <h4>Friction Points:</h4>
                    <ul style="margin-bottom: 20px;">
                        ${data.friction_points.map(point => `<li>${point}</li>`).join('')}
                    </ul>
                `;
            }
            
            if (data.opportunities && data.opportunities.length > 0) {
                resultsHTML += `
                    <h4>Opportunities:</h4>
                    <ul style="margin-bottom: 20px;">
                        ${data.opportunities.map(opp => `<li>${opp}</li>`).join('')}
                    </ul>
                `;
            }
            
            if (data.optimizations && data.optimizations.length > 0) {
                resultsHTML += `
                    <h4>Recommended Optimizations:</h4>
                    <ul style="margin-bottom: 20px;">
                        ${data.optimizations.map(opt => `<li>${opt}</li>`).join('')}
                    </ul>
                `;
            }
            
            if (data.metrics) {
                resultsHTML += '<h4>Key Metrics by Stage:</h4>';
                for (const [stage, metrics] of Object.entries(data.metrics)) {
                    resultsHTML += `
                        <div style="margin-bottom: 15px;">
                            <h5>${stage}:</h5>
                            <div>
                                ${metrics.map(metric => `<span style="display: inline-block; background: #f0f0f0; padding: 5px 15px; border-radius: 20px; margin-right: 10px; margin-bottom: 10px;">${metric}</span>`).join('')}
                            </div>
                        </div>
                    `;
                }
            }
            
            results.innerHTML = resultsHTML;
            results.style.display = 'block';
            results.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
        } catch (error) {
            console.error('Error:', error);
            alert('Analysis failed: ' + error.message);
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Generate Journey Map';
        }
    }
    
    async function generateReply() {
        const feedback = document.querySelector('#customer-feedback').value;
        const includeContext = document.querySelector('#context-checkbox').checked;
        const generateBtn = document.querySelector('#generate-reply');
        const results = document.querySelector('#reply-results');
        
        if (!feedback.trim()) {
            alert('Please enter customer feedback');
            return;
        }
        
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
        
        try {
            const response = await fetch('/generate-customer-response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feedback_text: feedback,
                    include_context: includeContext
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            results.innerHTML = `
                <h3>Generated Response</h3>
                <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="white-space: pre-wrap;">${data.response}</p>
                </div>
                <button id="copy-reply" class="analyze-btn" style="background: #4CAF50;">Copy to Clipboard</button>
            `;
            
            document.getElementById('copy-reply').addEventListener('click', function() {
                navigator.clipboard.writeText(data.response)
                    .then(() => alert('Response copied to clipboard!'))
                    .catch(err => console.error('Could not copy text: ', err));
            });
            
            results.style.display = 'block';
            results.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
        } catch (error) {
            console.error('Error:', error);
            alert('Generation failed: ' + error.message);
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Response';
        }
    }
    
    async function calculateCXScore() {
        const satisfaction = document.querySelector('#satisfaction-score').value;
        const ease = document.querySelector('#ease-score').value;
        const support = document.querySelector('#support-score').value;
        const recommend = document.querySelector('#recommend-score').value;
        const calculateBtn = document.querySelector('#calculate-score');
        const results = document.querySelector('#score-results');
        
        calculateBtn.disabled = true;
        calculateBtn.textContent = 'Calculating...';
        
        try {
            const response = await fetch('/calculate-cx-score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    answers: {
                        satisfaction: satisfaction,
                        ease_of_use: ease,
                        support_quality: support,
                        likelihood_to_recommend: recommend
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            let resultsHTML = `
                <h3>CX Score: ${data.score}/100</h3>
                <div style="margin: 20px 0; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden;">
                    <div style="height: 100%; width: ${data.score}%; background: ${data.score >= 80 ? '#4CAF50' : data.score >= 50 ? '#FFC107' : '#F44336'};"></div>
                </div>
            `;
            
            if (data.strengths && data.strengths.length > 0) {
                resultsHTML += `
                    <h4>Strengths:</h4>
                    <ul style="margin-bottom: 20px;">
                        ${data.strengths.map(strength => `<li>${strength}</li>`).join('')}
                    </ul>
                `;
            }
            
            if (data.improvements && data.improvements.length > 0) {
                resultsHTML += `
                    <h4>Areas for Improvement:</h4>
                    <ul style="margin-bottom: 20px;">
                        ${data.improvements.map(improvement => `<li>${improvement}</li>`).join('')}
                    </ul>
                `;
            }
            
            if (data.recommendations && data.recommendations.length > 0) {
                resultsHTML += `
                    <h4>Recommendations:</h4>
                    <ul>
                        ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                `;
            }
            
            results.innerHTML = resultsHTML;
            results.style.display = 'block';
            results.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
        } catch (error) {
            console.error('Error:', error);
            alert('Calculation failed: ' + error.message);
        } finally {
            calculateBtn.disabled = false;
            calculateBtn.textContent = 'Calculate Score';
        }
    }
});