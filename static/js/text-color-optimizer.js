/**
 * Text Color Optimizer JavaScript Client
 * Provides client-side functionality for text color optimization
 */

class TextColorOptimizer {
    constructor() {
        this.apiBaseUrl = '/api/v1';
        this.currentScheme = null;
        this.callbacks = {
            onOptimize: null,
            onContrastCheck: null,
            onError: null
        };
    }

    /**
     * Set callback functions
     */
    setCallbacks(callbacks) {
        this.callbacks = { ...this.callbacks, ...callbacks };
    }

    /**
     * Optimize text colors for a given background
     */
    async optimizeColors(backgroundColor, options = {}) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/text-color-optimization`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    background_color: backgroundColor,
                    ...options
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentScheme = data.data;
                this.applyColorScheme(data.data);
                
                if (this.callbacks.onOptimize) {
                    this.callbacks.onOptimize(data.data);
                }
                
                return data.data;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
            throw error;
        }
    }

    /**
     * Check contrast between two colors
     */
    async checkContrast(foregroundColor, backgroundColor) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/color-contrast-check`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    foreground_color: foregroundColor,
                    background_color: backgroundColor
                })
            });

            const data = await response.json();

            if (data.success) {
                if (this.callbacks.onContrastCheck) {
                    this.callbacks.onContrastCheck(data.data);
                }
                return data.data;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            if (this.callbacks.onError) {
                this.callbacks.onError(error);
            }
            throw error;
        }
    }

    /**
     * Apply color scheme to the page
     */
    applyColorScheme(scheme) {
        const root = document.documentElement;
        
        // Update CSS custom properties
        root.style.setProperty('--bg-color', scheme.background_color);
        root.style.setProperty('--text-primary', scheme.recommendations.primary_text.color);
        root.style.setProperty('--text-secondary', scheme.recommendations.secondary_text.color);
        root.style.setProperty('--text-accent', scheme.recommendations.accent_text.color);

        // Add accessibility classes to body
        document.body.classList.add('text-color-optimized');
        
        // Update meta theme color for mobile browsers
        this.updateMetaThemeColor(scheme.background_color);
    }

    /**
     * Update meta theme color for mobile browsers
     */
    updateMetaThemeColor(color) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        metaThemeColor.content = color;
    }

    /**
     * Generate CSS code for the current scheme
     */
    generateCSS(scheme = null) {
        const currentScheme = scheme || this.currentScheme;
        if (!currentScheme) return '';

        return `:root {
    --bg-color: ${currentScheme.background_color};
    --text-primary: ${currentScheme.recommendations.primary_text.color};
    --text-secondary: ${currentScheme.recommendations.secondary_text.color};
    --text-accent: ${currentScheme.recommendations.accent_text.color};
}

.text-primary-optimized { color: var(--text-primary); }
.text-secondary-optimized { color: var(--text-secondary); }
.text-accent-optimized { color: var(--text-accent); }
.bg-optimized { background-color: var(--bg-color); }`;
    }

    /**
     * Generate HTML example
     */
    generateHTMLExample(scheme = null) {
        const currentScheme = scheme || this.currentScheme;
        if (!currentScheme) return '';

        return `<div class="bg-optimized text-primary-optimized">
    <h1 class="text-primary-optimized">عنوان اصلی</h1>
    <p class="text-secondary-optimized">متن ثانویه</p>
    <a href="#" class="text-accent-optimized">لینک تأکیدی</a>
</div>`;
    }

    /**
     * Validate color format
     */
    validateColor(color) {
        const hexPattern = /^#[0-9A-Fa-f]{6}$/;
        const rgbPattern = /^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$/;
        
        return hexPattern.test(color) || rgbPattern.test(color);
    }

    /**
     * Convert RGB to Hex
     */
    rgbToHex(rgb) {
        const result = rgb.match(/\d+/g);
        if (!result || result.length !== 3) return null;
        
        const r = parseInt(result[0]);
        const g = parseInt(result[1]);
        const b = parseInt(result[2]);
        
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }

    /**
     * Get accessibility level badge class
     */
    getAccessibilityBadgeClass(level) {
        switch(level) {
            case 'AAA': return 'badge-success';
            case 'AA': return 'badge-warning';
            default: return 'badge-danger';
        }
    }

    /**
     * Create color preview element
     */
    createColorPreview(colorData, backgroundColor, type) {
        const preview = document.createElement('div');
        preview.className = 'color-preview';
        preview.innerHTML = `
            <div class="color-box" style="background-color: ${colorData.color};"></div>
            <div class="color-info">
                <h5>${type}</h5>
                <p>${colorData.color}</p>
                <p>کنتراست: ${colorData.contrast_ratio}:1</p>
                <span class="badge ${this.getAccessibilityBadgeClass(colorData.accessibility_level)}">
                    ${colorData.accessibility_level}
                </span>
            </div>
        `;
        return preview;
    }

    /**
     * Create alternative scheme element
     */
    createAlternativeScheme(alternative, backgroundColor, index) {
        const scheme = document.createElement('div');
        scheme.className = 'alternative-scheme';
        scheme.dataset.index = index;
        scheme.innerHTML = `
            <h6>${alternative.name}</h6>
            <div class="alternative-colors">
                <div class="alternative-color" style="background-color: ${alternative.primary}" title="متن اصلی"></div>
                <div class="alternative-color" style="background-color: ${alternative.secondary}" title="متن ثانویه"></div>
                <div class="alternative-color" style="background-color: ${alternative.accent}" title="متن تأکیدی"></div>
            </div>
            <div class="mt-2">
                <small class="text-muted">
                    کنتراست: ${alternative.primary_contrast}:1 (${alternative.primary_accessibility})
                </small>
            </div>
        `;
        return scheme;
    }

    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return true;
        }
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';
        notification.innerHTML = `
            ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        `;

        document.body.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    /**
     * Initialize color picker integration
     */
    initializeColorPickers() {
        // Sync color inputs
        const colorInputs = document.querySelectorAll('input[type="color"]');
        const textInputs = document.querySelectorAll('input[type="text"][placeholder*="#"]');

        colorInputs.forEach(input => {
            const textInput = document.getElementById(input.id.replace('-color', '-color-text'));
            if (textInput) {
                input.addEventListener('input', () => {
                    textInput.value = input.value;
                });
            }
        });

        textInputs.forEach(input => {
            const colorInput = document.getElementById(input.id.replace('-text', ''));
            if (colorInput) {
                input.addEventListener('input', () => {
                    if (this.validateColor(input.value)) {
                        colorInput.value = input.value;
                    }
                });
            }
        });
    }

    /**
     * Initialize the optimizer
     */
    init() {
        this.initializeColorPickers();
        
        // Add global styles
        this.addGlobalStyles();
        
        // Initialize accessibility features
        this.initializeAccessibility();
    }

    /**
     * Add global styles for the optimizer
     */
    addGlobalStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .color-preview {
                text-align: center;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-bottom: 15px;
            }
            
            .color-box {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                margin: 0 auto 15px;
                border: 3px solid #fff;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .alternative-scheme {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .alternative-scheme:hover {
                border-color: #007bff;
                box-shadow: 0 2px 10px rgba(0,123,255,0.1);
            }
            
            .alternative-scheme.selected {
                border-color: #007bff;
                background-color: #f8f9fa;
            }
            
            .alternative-colors {
                display: flex;
                justify-content: space-around;
                margin-top: 10px;
            }
            
            .alternative-color {
                width: 30px;
                height: 30px;
                border-radius: 50%;
                border: 2px solid #fff;
                box-shadow: 0 1px 5px rgba(0,0,0,0.1);
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Initialize accessibility features
     */
    initializeAccessibility() {
        // Add keyboard navigation support
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });

        // Add focus indicators
        const focusStyle = document.createElement('style');
        focusStyle.textContent = `
            .keyboard-navigation *:focus {
                outline: 2px solid #007bff !important;
                outline-offset: 2px !important;
            }
        `;
        document.head.appendChild(focusStyle);
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TextColorOptimizer;
}

// Global instance
window.TextColorOptimizer = TextColorOptimizer;
