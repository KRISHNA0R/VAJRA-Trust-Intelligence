// Status configuration
// Decision configuration - Five-tier system
const DECISION_CONFIG = {
    'AUTHENTIC': {
        alertClass: 'alert-success',
        title: 'AUTHENTIC',
        text: 'High confidence authentic image.',
        statText: 'AUTHENTIC',
        statColor: 'text-success',
        iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
        badgeClass: 'badge-success'
    },
    'LIKELY_AUTHENTIC': {
        alertClass: 'alert-info',
        title: 'LIKELY AUTHENTIC',
        text: 'Moderate confidence authentic image.',
        statText: 'LIKELY AUTHENTIC',
        statColor: 'text-info',
        iconPath: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
        badgeClass: 'badge-info'
    },
    'INCONCLUSIVE': {
        alertClass: 'alert-warning',
        title: 'INCONCLUSIVE',
        text: 'Unable to determine authenticity with confidence.',
        statText: 'INCONCLUSIVE',
        statColor: 'text-warning',
        iconPath: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z',
        badgeClass: 'badge-warning'
    },
    'LIKELY_FORGED': {
        alertClass: 'alert-error',
        title: 'LIKELY FORGED',
        text: 'Moderate confidence forged image.',
        statText: 'LIKELY FORGED',
        statColor: 'text-error',
        iconPath: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
        badgeClass: 'badge-error'
    },
    'FORGED': {
        alertClass: 'alert-error',
        title: 'FORGED',
        text: 'High confidence forged image.',
        statText: 'FORGED',
        statColor: 'text-error',
        iconPath: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
        badgeClass: 'badge-error'
    }
};

// Decision logic function
function determineDecision(integrity, evidenceReliability) {
    // BUGFIX-009: Handle invalid/corrupted data
    // If integrity or reliability is NaN, null, or clearly invalid, return INCONCLUSIVE
    if (integrity == null || evidenceReliability == null || 
        isNaN(integrity) || isNaN(evidenceReliability) ||
        integrity === 0 || evidenceReliability === 0) {
        return 'INCONCLUSIVE';
    }
    
    const integrityPercent = Math.round(integrity * 100);
    const reliabilityPercent = Math.round(evidenceReliability * 100);
    
    // Decision thresholds based on your requirements
    if (integrityPercent >= 70 && reliabilityPercent >= 40) {
        return 'AUTHENTIC';
    } else if (integrityPercent >= 55 && integrityPercent < 70) {
        return 'LIKELY_AUTHENTIC';
    } else if (integrityPercent >= 45 && integrityPercent < 55) {
        return 'INCONCLUSIVE';
    } else if (integrityPercent >= 30 && integrityPercent < 45 && reliabilityPercent >= 40) {
        return 'LIKELY_FORGED';
    } else if (integrityPercent < 30 && reliabilityPercent >= 50) {
        return 'FORGED';
    } else {
        return 'INCONCLUSIVE'; // Default for edge cases
    }
}

// 🎨 UPDATED VERSION WITH SMOOTH COLORMAP - NO BLACK REGIONS! 🎨

// DOM elements are defined in HTML - using global elements object

// Check for missing elements
for (const [name, element] of Object.entries(elements)) {
    if (!element) {
        console.error(`Missing DOM element: ${name}`);
    }
}

// File validation
function validateFile(file) {
    const allowedTypes = ['image/jpeg', 'image/png', 'video/mp4', 'video/quicktime'];
    const maxImageSize = 10 * 1024 * 1024; // 10MB
    const maxVideoSize = 50 * 1024 * 1024; // 50MB
    
    if (!allowedTypes.includes(file.type)) {
        showError('Unsupported file type. Please upload JPG, PNG, MP4 or MOV files.');
        return false;
    }
    
    const isVideo = file.type.startsWith('video/');
    const maxSize = isVideo ? maxVideoSize : maxImageSize;
    
    if (file.size > maxSize) {
        const maxSizeMB = maxSize / (1024 * 1024);
        showError(`File too large. Maximum size: ${maxSizeMB}MB.`);
        return false;
    }
    
    return true;
}

// Show error
function showError(message) {
    elements.errorText.textContent = message;
    elements.errorAlert.classList.remove('hidden');
    setTimeout(() => {
        elements.errorAlert.classList.add('hidden');
    }, 5000);
}

// Handle file
async function handleFile(file) {
    if (!validateFile(file)) {
        return;
    }
    
    // Check authentication
    const token = localStorage.getItem('access_token');
    if (!token) {
        showError('Please login first. Redirecting to login page...');
        setTimeout(() => {
            window.location.href = '/web/login.html';
        }, 2000);
        return;
    }
    
    // Hide errors and results
    elements.errorAlert.classList.add('hidden');
    elements.resultPanel.classList.add('hidden');
    
    // Hide upload card and show loading state
    elements.uploadCard.classList.add('hidden');
    elements.loadingState.classList.remove('hidden');
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/detect', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            console.error('API error:', error);
            
            // Handle authentication errors
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                showError('Session expired. Please login again...');
                setTimeout(() => {
                    window.location.href = '/web/login.html';
                }, 2000);
                return;
            }
            
            throw new Error(error.detail || 'Detection failed');
        }
        
        const result = await response.json();
        displayResult(result);
        
    } catch (error) {
        console.error('Detection error:', error);
        showError(error.message || 'An error occurred during detection');
        resetUpload();
    }
}

// Display results
function displayResult(data) {
    // Determine if this is TruFor response
    const isTruFor = data.model === 'TruFor';
    
    // Update status based on TruFor response format
    let status, config;
    if (isTruFor) {
        // Calculate evidence reliability from confidence map
        let evidenceReliability = 0.5; // Default
        if (data.confidence_map) {
            const confData = data.confidence_map.flat();
            const avgConfidence = confData.reduce((sum, val) => sum + val, 0) / confData.length;
            evidenceReliability = avgConfidence;
        }
        
        // Determine decision using new five-tier system
        status = determineDecision(data.integrity, evidenceReliability);
        config = DECISION_CONFIG[status];
        
        // Update status alert
        elements.statusAlert.className = `alert ${config.alertClass} shadow-lg`;
        elements.statusIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${config.iconPath}" />`;
        elements.statusTitle.textContent = config.title;
        elements.statusText.textContent = config.text;
        
        // Update statistics
        elements.resultStatus.textContent = config.statText;
        elements.resultStatus.className = `stat-value text-2xl ${config.statColor}`;
        elements.resultDesc.textContent = `Model: ${data.model} | Filename: ${data.filename}`;
        
        // Update evidence reliability
        if (data.confidence_map) {
            const confData = data.confidence_map.flat();
            const avgConfidence = confData.reduce((sum, val) => sum + val, 0) / confData.length;
            const reliabilityPercent = Math.round(avgConfidence * 100);
            elements.confidenceText.textContent = `${reliabilityPercent}%`;
            elements.confidenceBar.value = reliabilityPercent;
        } else {
            // Handle invalid or missing confidence data
            const confidence = (data.confidence != null && !isNaN(data.confidence)) 
                ? Math.round(data.confidence * 100) 
                : 0;
            elements.confidenceBar.value = confidence;
            elements.confidenceText.textContent = `${confidence}%`;
        }
        
        // Show detection score for TruFor
        if (data.detection_score !== undefined) {
            elements.detectionScoreStat.style.display = 'block';
            const detectionScore = Math.round(data.detection_score * 100);
            elements.detectionScoreBar.value = detectionScore;
            elements.detectionScoreText.textContent = `${detectionScore}%`;
        }
        
        // Show TruFor visualization
        if (data.prediction_map) {
            elements.truforVisualization.classList.remove('hidden');
            elements.detectionScoreStat.style.display = 'block';
            elements.fakeLikelihoodStat.style.display = 'block';
            displayTruForVisualization(data);
            
            // Display portrait mode detection note
            if (data.portrait_note) {
                // Create or update portrait note element
                let portraitNoteElement = document.getElementById('portraitNote');
                if (!portraitNoteElement) {
                    portraitNoteElement = document.createElement('div');
                    portraitNoteElement.id = 'portraitNote';
                    portraitNoteElement.className = 'mt-4 p-3 bg-blue-100 border border-blue-300 rounded-lg text-sm text-blue-800';
                    elements.truforVisualization.querySelector('.card-body').appendChild(portraitNoteElement);
                }
                portraitNoteElement.textContent = data.portrait_note;
                portraitNoteElement.style.display = 'block';
            } else {
                // Hide portrait note if not detected
                const portraitNoteElement = document.getElementById('portraitNote');
                if (portraitNoteElement) {
                    portraitNoteElement.style.display = 'none';
                }
            }
        }
        
        // Update technical details
        const details = {
            model: data.model,
            is_fake: data.is_fake,
            confidence: data.confidence,
            detection_score: data.detection_score,
            image_size: data.image_size,
            has_confidence_map: data.has_confidence_map,
            has_noiseprint: data.has_noiseprint,
            prediction_map_size: data.prediction_map ? data.prediction_map.length : 0
        };
        elements.technicalDetails.textContent = JSON.stringify(details, null, 2);
        
    } else {
        // Legacy format for other models
        config = DECISION_CONFIG[data.status] || DECISION_CONFIG['INCONCLUSIVE'];
        
        // Update status alert
        elements.statusAlert.className = `alert ${config.alertClass} shadow-lg`;
        elements.statusIcon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${config.iconPath}" />`;
        elements.statusTitle.textContent = config.title;
        elements.statusText.textContent = config.text;
        
        // Update statistics
        elements.resultStatus.textContent = config.statText;
        elements.resultStatus.className = `stat-value text-2xl ${config.statColor}`;
        elements.resultDesc.textContent = `Request ID: ${data.request_id || 'N/A'}`;
        
        // Update confidence
        const score = (data.score != null && !isNaN(data.score)) ? data.score : 0;
        const confidence = Math.round(score * 100);
        elements.confidenceBar.value = confidence;
        elements.confidenceText.textContent = `${confidence}%`;
        
        // Hide TruFor-specific elements
        elements.truforVisualization.classList.add('hidden');
        elements.detectionScoreStat.style.display = 'none';
        
        // Update technical details
        const details = {
            ...data.vendor_raw,
            media_type: data.media_type,
            score_scale: data.score_scale
        };
        elements.technicalDetails.textContent = JSON.stringify(details, null, 2);
    }
    
    // Hide loading, show results
    elements.loadingState.classList.add('hidden');
    elements.resultPanel.classList.remove('hidden');
}

// Display TruFor visualization
function displayTruForVisualization(data) {
    // Store current image data for visualization
    window.currentImageData = data;
    
    // Function to setup canvas and draw visualizations
    function setupVisualizationsWithAspectRatio() {
        // Get actual image dimensions
        const imgWidth = elements.originalImage.naturalWidth;
        const imgHeight = elements.originalImage.naturalHeight;
        
        // Calculate aspect ratio preserving dimensions with max size 300px
        // BUGFIX-007: Limit max size to prevent browser crash with large images
        const maxSize = 300;
        const maxCanvasPixels = 300 * 300; // Maximum 90K pixels to prevent memory issues
        let canvasWidth, canvasHeight;
        
        if (imgWidth > imgHeight) {
            // Landscape
            canvasWidth = Math.min(maxSize, Math.sqrt(maxCanvasPixels * (imgWidth / imgHeight)));
            canvasHeight = Math.round(canvasWidth * (imgHeight / imgWidth));
        } else {
            // Portrait or square
            canvasHeight = Math.min(maxSize, Math.sqrt(maxCanvasPixels * (imgHeight / imgWidth)));
            canvasWidth = Math.round(canvasHeight * (imgWidth / imgHeight));
        }
        
        // Ensure dimensions are at least 1px
        canvasWidth = Math.max(1, Math.floor(canvasWidth));
        canvasHeight = Math.max(1, Math.floor(canvasHeight));
        
        
        // Set canvas size to match aspect ratio (both element properties and CSS style)
        elements.predictionOverlay.width = canvasWidth;
        elements.predictionOverlay.height = canvasHeight;
        elements.predictionOverlay.style.width = canvasWidth + 'px';
        elements.predictionOverlay.style.height = canvasHeight + 'px';
        
        elements.predictionHeatmap.width = canvasWidth;
        elements.predictionHeatmap.height = canvasHeight;
        elements.predictionHeatmap.style.width = canvasWidth + 'px';
        elements.predictionHeatmap.style.height = canvasHeight + 'px';
        
        elements.confidenceMap.width = canvasWidth;
        elements.confidenceMap.height = canvasHeight;
        elements.confidenceMap.style.width = canvasWidth + 'px';
        elements.confidenceMap.style.height = canvasHeight + 'px';
        
        elements.noiseprintMap.width = canvasWidth;
        elements.noiseprintMap.height = canvasHeight;
        elements.noiseprintMap.style.width = canvasWidth + 'px';
        elements.noiseprintMap.style.height = canvasHeight + 'px';
        
        
        // Redraw all visualizations with correct aspect ratio
        if (data.prediction_map) {
            drawHeatmap(elements.predictionHeatmap, data.prediction_map, 'forgery');
            drawPredictionOverlay(elements.predictionOverlay, data.prediction_map);
        }
        
        if (data.confidence_map) {
            drawHeatmap(elements.confidenceMap, data.confidence_map, 'confidence');
        }
        
        if (data.noiseprint_map) {
            drawHeatmap(elements.noiseprintMap, data.noiseprint_map, 'noiseprint');
        }
    }
    
    // Display original image
    if (data.original_image_url) {
        elements.originalImage.onload = setupVisualizationsWithAspectRatio;
        elements.originalImage.src = data.original_image_url;
        
        // Handle case where image is already cached and loaded
        if (elements.originalImage.complete && elements.originalImage.naturalWidth > 0) {
            setupVisualizationsWithAspectRatio();
        }
    } else {
        // If no original image URL, we'll need to create one from the uploaded file
        // For now, we'll show a placeholder
        elements.originalImage.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxOCIgZmlsbD0iIzk5YTNhZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIFByZXZpZXc8L3RleHQ+PC9zdmc+';
    }
    
    // Note: All visualizations are drawn in the onload handler to ensure correct aspect ratio
    // This prevents the issue of drawing with wrong dimensions before image loads
    
    // Update Integrity Score and Fake Likelihood
    if (data.integrity !== undefined) {
        const integrityPercent = Math.round(data.integrity * 100);
        const fakeLikelihoodPercent = Math.round((1 - data.integrity) * 100);
        
        // Update integrity score
        elements.integrityScore.textContent = integrityPercent;
        
        // Update label and progress bar
        if (data.integrity > 0.5) {
            elements.integrityLabel.textContent = 'AUTHENTIC';
            elements.integrityBar.className = 'bg-green-600 h-3 rounded-full transition-all duration-500';
        } else {
            elements.integrityLabel.textContent = 'FAKE';
            elements.integrityBar.className = 'bg-red-600 h-3 rounded-full transition-all duration-500';
        }
        
        // Update progress bar width
        elements.integrityBar.style.width = `${integrityPercent}%`;
        
        // Update fake likelihood (if element exists)
        if (elements.fakeLikelihoodText) {
            elements.fakeLikelihoodText.textContent = fakeLikelihoodPercent;
            elements.fakeLikelihoodBar.style.width = `${fakeLikelihoodPercent}%`;
        }
        
    }
}

// Improved JET colormap function (blue to red) - smoother transitions
function jetColormap(value, channel) {
    // Clamp value to [0, 1]
    value = Math.max(0, Math.min(1, value));
    
    // Smoother JET colormap with better transitions
    if (channel === 0) { // Red
        if (value < 0.125) return 0;
        if (value < 0.375) return 4 * (value - 0.125);
        if (value < 0.625) return 1;
        if (value < 0.875) return 1 - 4 * (value - 0.625);
        return 0;
    } else if (channel === 1) { // Green
        if (value < 0.25) return 4 * value;
        if (value < 0.5) return 1;
        if (value < 0.75) return 1 - 4 * (value - 0.5);
        return 0;
    } else { // Blue
        if (value < 0.25) return 0.5 + 2 * value;
        if (value < 0.5) return 1 - 2 * (value - 0.25);
        return 0;
    }
}

// Simple and smooth colormap (blue to red) - no black regions
function smoothColormap(value) {
    // Clamp value to [0, 1]
    value = Math.max(0, Math.min(1, value));
    
    // Simple linear interpolation from blue to red
    // Blue (0,0,255) -> Cyan (0,255,255) -> Green (0,255,0) -> Yellow (255,255,0) -> Red (255,0,0)
    
    if (value < 0.25) {
        // Blue to Cyan: (0,0,255) to (0,255,255)
        const t = value * 4;
        return [0, t, 1];
    } else if (value < 0.5) {
        // Cyan to Green: (0,255,255) to (0,255,0)
        const t = (value - 0.25) * 4;
        return [0, 1, 1 - t];
    } else if (value < 0.75) {
        // Green to Yellow: (0,255,0) to (255,255,0)
        const t = (value - 0.5) * 4;
        return [t, 1, 0];
    } else {
        // Yellow to Red: (255,255,0) to (255,0,0)
        const t = (value - 0.75) * 4;
        return [1, 1 - t, 0];
    }
}

// Draw heatmap on canvas - UPDATED VERSION WITH SMOOTH COLORMAP
function drawHeatmap(canvas, data, type) {
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Create image data
    const imageData = ctx.createImageData(width, height);
    const pixels = imageData.data;
    
    // Draw heatmap based on type
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const dataX = Math.floor((x / width) * data[0].length);
            const dataY = Math.floor((y / height) * data.length);
            const pixelIndex = (y * width + x) * 4;
            
            if (dataY < data.length && dataX < data[dataY].length) {
                const value = data[dataY][dataX];
                
                if (type === 'forgery') {
                    // Anomaly map: Smooth colormap (blue to red) - no black regions
                    const normalizedValue = Math.max(0, Math.min(1, value));
                    const [r, g, b] = smoothColormap(normalizedValue);
                    
                    pixels[pixelIndex] = Math.round(255 * r);     // Red
                    pixels[pixelIndex + 1] = Math.round(255 * g); // Green
                    pixels[pixelIndex + 2] = Math.round(255 * b); // Blue
                    pixels[pixelIndex + 3] = 255; // Alpha
                    
                } else if (type === 'confidence') {
                    // Confidence map: grayscale with slight contrast enhancement
                    const normalizedValue = Math.max(0, Math.min(1, value));
                    // Apply slight contrast enhancement: map [0.3, 0.9] to [0, 1]
                    const enhancedValue = Math.max(0, Math.min(1, (normalizedValue - 0.3) / 0.6));
                    const intensity = Math.round(255 * enhancedValue);
                    
                    pixels[pixelIndex] = intensity;     // Red
                    pixels[pixelIndex + 1] = intensity; // Green
                    pixels[pixelIndex + 2] = intensity; // Blue
                    pixels[pixelIndex + 3] = 255;       // Alpha
                    
                } else if (type === 'noiseprint') {
                    // Noiseprint++: grayscale
                    const normalizedValue = Math.max(0, Math.min(1, value));
                    const intensity = Math.round(255 * normalizedValue);
                    
                    pixels[pixelIndex] = intensity;     // Red
                    pixels[pixelIndex + 1] = intensity; // Green
                    pixels[pixelIndex + 2] = intensity; // Blue
                    pixels[pixelIndex + 3] = 255;       // Alpha
                }
            } else {
                // Fill out-of-bounds pixels with black
                pixels[pixelIndex] = 0;
                pixels[pixelIndex + 1] = 0;
                pixels[pixelIndex + 2] = 0;
                pixels[pixelIndex + 3] = 255;
            }
        }
    }
    
    ctx.putImageData(imageData, 0, 0);
}

// Draw prediction overlay on original image
function drawPredictionOverlay(canvas, data) {
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    
    // Set canvas size to match display size
    canvas.width = width;
    canvas.height = height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Create image data
    const imageData = ctx.createImageData(width, height);
    const pixels = imageData.data;
    
    // Convert 2D array to 1D for processing
    const flatData = data.flat();
    const minVal = Math.min(...flatData);
    const maxVal = Math.max(...flatData);
    const range = maxVal - minVal;
    
    // Draw overlay
    for (let i = 0; i < pixels.length; i += 4) {
        const pixelIndex = Math.floor(i / 4);
        const x = pixelIndex % width;
        const y = Math.floor(pixelIndex / width);
        
        // Map 2D data to 1D pixel index
        const dataX = Math.floor((x / width) * data[0].length);
        const dataY = Math.floor((y / height) * data.length);
        
        if (dataY < data.length && dataX < data[dataY].length) {
            const value = data[dataY][dataX];
            const normalizedValue = range > 0 ? (value - minVal) / range : 0;
            
            // Only show overlay for high confidence predictions
            if (normalizedValue > 0.5) {
                const intensity = (normalizedValue - 0.5) * 2; // Scale from 0.5-1 to 0-1
                pixels[i] = 255;     // Red
                pixels[i + 1] = 0;   // Green
                pixels[i + 2] = 0;   // Blue
                pixels[i + 3] = Math.round(intensity * 128); // Alpha
            }
        }
    }
    
    ctx.putImageData(imageData, 0, 0);
}

// Reset upload
function resetUpload() {
    elements.uploadCard.classList.remove('hidden');
    elements.uploadZone.classList.remove('hidden');
    elements.loadingState.classList.add('hidden');
    elements.resultPanel.classList.add('hidden');
    elements.errorAlert.classList.add('hidden');
    elements.truforVisualization.classList.add('hidden');
    elements.detectionScoreStat.style.display = 'none';
    elements.fileInput.value = '';
    
    // Clear current image data
    window.currentImageData = null;
}

// Drag and drop events
if (elements.uploadZone) {
    elements.uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.add('border-primary', 'bg-base-200');
    });

    elements.uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.remove('border-primary', 'bg-base-200');
    });

    elements.uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.remove('border-primary', 'bg-base-200');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
} else {
    console.error('uploadZone element not found!');
}

// File selection event
if (elements.fileInput) {
    elements.fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
} else {
    console.error('fileInput element not found!');
}

// Theme toggle
elements.themeToggle.addEventListener('change', (e) => {
    const theme = e.target.checked ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
});

// Initialize theme
window.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    elements.themeToggle.checked = savedTheme === 'dark';
});