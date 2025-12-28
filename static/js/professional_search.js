/**
 * Professional Search Engine for Asia Salman Shop
 * موتور جستجوی حرفه‌ای برای فروشگاه آسیا سلمان
 */
class ProfessionalSearchEngine {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/api/search';
        this.suggestionsUrl = options.suggestionsUrl || '/api/search/suggestions';
        this.trackClickUrl = options.trackClickUrl || '/api/search/track-click';
        this.debounceDelay = options.debounceDelay || 300;
        this.minQueryLength = options.minQueryLength || 2;
        this.cache = new Map();
        this.cacheTimeout = options.cacheTimeout || 300000; // 5 minutes
        this.selectedSuggestionIndex = -1;
        this.currentQuery = '';
        this.currentFilters = {};
        this.currentSort = 'relevance';
        
        // Initialize
        this.init();
    }
    
    init() {
        this.setupSearchInput();
        this.setupSuggestions();
        this.setupFilters();
        this.setupSorting();
        this.setupPagination();
    }
    
    /**
     * Setup search input with auto-focus and event handlers
     */
    setupSearchInput() {
        const searchInput = document.getElementById('productSearch');
        if (!searchInput) return;
        
        // Auto-focus on page load (only on shop page)
        if (window.location.pathname.includes('/shop')) {
            setTimeout(() => {
                searchInput.focus();
            }, 100);
        }
        
        // Clear button
        const clearBtn = document.createElement('button');
        clearBtn.type = 'button';
        clearBtn.className = 'btn btn-link text-muted p-0 position-absolute';
        clearBtn.style.cssText = 'right: 45px; top: 50%; transform: translateY(-50%); z-index: 10; display: none;';
        clearBtn.innerHTML = '<i class="fas fa-times"></i>';
        clearBtn.setAttribute('aria-label', 'پاک کردن جستجو');
        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            searchInput.focus();
            this.hideSuggestions();
            clearBtn.style.display = 'none';
            this.currentQuery = '';
        });
        
        const inputGroup = searchInput.closest('.input-group');
        if (inputGroup) {
            inputGroup.style.position = 'relative';
            inputGroup.appendChild(clearBtn);
            
            // Show/hide clear button
            searchInput.addEventListener('input', () => {
                clearBtn.style.display = searchInput.value.length > 0 ? 'block' : 'none';
            });
        }
    }
    
    /**
     * Setup search suggestions with debouncing
     */
    setupSuggestions() {
        const searchInput = document.getElementById('productSearch');
        if (!searchInput) return;
        
        let searchTimeout;
        
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            this.currentQuery = query;
            
            clearTimeout(searchTimeout);
            
            if (query.length < this.minQueryLength) {
                this.hideSuggestions();
                return;
            }
            
            searchTimeout = setTimeout(() => {
                this.fetchSuggestions(query);
            }, this.debounceDelay);
        });
        
        // Keyboard navigation
        searchInput.addEventListener('keydown', (e) => {
            const suggestions = document.querySelectorAll('.search-suggestion');
            
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    if (suggestions.length > 0) {
                        this.selectedSuggestionIndex = Math.min(
                            this.selectedSuggestionIndex + 1,
                            suggestions.length - 1
                        );
                        this.updateSuggestionSelection(suggestions);
                    }
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    if (suggestions.length > 0) {
                        this.selectedSuggestionIndex = Math.max(
                            this.selectedSuggestionIndex - 1,
                            -1
                        );
                        this.updateSuggestionSelection(suggestions);
                    }
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (this.selectedSuggestionIndex >= 0 && suggestions.length > 0) {
                        // User selected a suggestion, click it
                        suggestions[this.selectedSuggestionIndex].click();
                    } else {
                        // User pressed Enter without selecting, perform search
                        this.hideSuggestions();
                        this.performSearch();
                    }
                    break;
                case 'Escape':
                    this.hideSuggestions();
                    this.selectedSuggestionIndex = -1;
                    break;
            }
        });
        
        // Close suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.input-group') && !e.target.closest('.search-autocomplete')) {
                this.hideSuggestions();
            }
        });
    }
    
    /**
     * Fetch search suggestions from API
     */
    async fetchSuggestions(query) {
        const cacheKey = `suggestions_${query}`;
        
        // Check cache
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                this.displaySuggestions(cached.data);
                return;
            }
        }
        
        try {
            const context = JSON.stringify(this.currentFilters);
            const url = `${this.suggestionsUrl}?q=${encodeURIComponent(query)}&limit=10&context=${encodeURIComponent(context)}`;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Cache results
            this.cache.set(cacheKey, {
                data: data.suggestions || [],
                timestamp: Date.now()
            });
            
            this.displaySuggestions(data.suggestions || []);
        } catch (error) {
            // Only log errors that are not related to tracking prevention
            if (!error.message || !error.message.includes('Tracking Prevention')) {
                console.error('Error fetching suggestions:', error);
            }
            this.hideSuggestions();
        }
    }
    
    /**
     * Display suggestions in dropdown
     */
    displaySuggestions(suggestions) {
        const autocomplete = document.getElementById('searchAutocomplete');
        if (!autocomplete) return;
        
        if (suggestions.length === 0) {
            autocomplete.innerHTML = '<div class="search-suggestion"><div class="suggestion-text text-muted">نتیجه‌ای یافت نشد</div></div>';
            autocomplete.classList.add('show');
            return;
        }
        
        autocomplete.innerHTML = '';
        
        // Group suggestions by type
        const grouped = {
            brand: [],
            model: [],
            category: [],
            product: []
        };
        
        suggestions.forEach(suggestion => {
            if (grouped[suggestion.type]) {
                grouped[suggestion.type].push(suggestion);
            }
        });
        
        // Display grouped suggestions
        Object.keys(grouped).forEach(type => {
            if (grouped[type].length === 0) return;
            
            const typeLabels = {
                brand: 'برندها',
                model: 'مدل‌ها',
                category: 'دسته‌بندی‌ها',
                product: 'محصولات'
            };
            
            const groupDiv = document.createElement('div');
            groupDiv.className = 'suggestion-group';
            
            const header = document.createElement('div');
            header.className = 'suggestion-group-header';
            header.textContent = typeLabels[type] || type;
            groupDiv.appendChild(header);
            
            grouped[type].forEach(suggestion => {
                const item = this.createSuggestionItem(suggestion);
                groupDiv.appendChild(item);
            });
            
            autocomplete.appendChild(groupDiv);
        });
        
        autocomplete.classList.add('show');
        this.selectedSuggestionIndex = -1;
    }
    
    /**
     * Create a suggestion item element
     */
    createSuggestionItem(suggestion) {
        const item = document.createElement('div');
        item.className = 'search-suggestion';
        item.setAttribute('role', 'option');
        item.setAttribute('tabindex', '0');
        
        const icon = document.createElement('i');
        icon.className = `${suggestion.icon || 'fas fa-search'} suggestion-icon`;
        
        const text = document.createElement('div');
        text.className = 'suggestion-text';
        text.textContent = suggestion.text_fa || suggestion.text;
        
        const meta = document.createElement('div');
        meta.className = 'suggestion-meta';
        if (suggestion.type === 'product' && suggestion.sku) {
            meta.textContent = `کد: ${suggestion.sku}`;
        } else if (suggestion.type === 'brand') {
            meta.textContent = 'برند';
        } else if (suggestion.type === 'model') {
            meta.textContent = 'مدل خودرو';
        } else if (suggestion.type === 'category') {
            meta.textContent = 'دسته‌بندی';
        }
        
        item.appendChild(icon);
        item.appendChild(text);
        if (meta.textContent) {
            item.appendChild(meta);
        }
        
        // Click handler
        item.addEventListener('click', () => {
            this.handleSuggestionClick(suggestion);
        });
        
        // Keyboard handler
        item.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.handleSuggestionClick(suggestion);
            }
        });
        
        return item;
    }
    
    /**
     * Handle suggestion click
     */
    handleSuggestionClick(suggestion) {
        const searchInput = document.getElementById('productSearch');
        
        if (suggestion.type === 'product') {
            // Navigate to product page
            window.location.href = `/product/${suggestion.id}`;
        } else if (suggestion.type === 'brand') {
            // Set brand filter and search
            if (searchInput) {
                searchInput.value = suggestion.text_fa || suggestion.text;
                this.currentFilters.brand_id = suggestion.id;
                this.performSearch();
            }
        } else if (suggestion.type === 'model') {
            // Add model to search query
            if (searchInput) {
                const currentValue = searchInput.value.trim();
                searchInput.value = `${currentValue} ${suggestion.text_fa || suggestion.text}`;
                this.performSearch();
            }
        } else if (suggestion.type === 'category') {
            // Set category filter and search
            if (searchInput) {
                searchInput.value = suggestion.text_fa || suggestion.text;
                this.currentFilters.category_id = suggestion.id;
                this.performSearch();
            }
        } else {
            // Generic search - just use the suggestion text
            if (searchInput) {
                searchInput.value = suggestion.text_fa || suggestion.text;
                this.performSearch();
            }
        }
        
        this.hideSuggestions();
    }
    
    /**
     * Update suggestion selection (keyboard navigation)
     */
    updateSuggestionSelection(suggestions) {
        suggestions.forEach((item, index) => {
            item.classList.toggle('active', index === this.selectedSuggestionIndex);
            if (index === this.selectedSuggestionIndex) {
                item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }
        });
    }
    
    /**
     * Hide suggestions dropdown
     */
    hideSuggestions() {
        const autocomplete = document.getElementById('searchAutocomplete');
        if (autocomplete) {
            autocomplete.classList.remove('show');
        }
        this.selectedSuggestionIndex = -1;
    }
    
    /**
     * Setup filters
     */
    setupFilters() {
        // Filter form submission
        const filterForm = document.querySelector('.filter-section form');
        if (filterForm) {
            filterForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.collectFilters();
                
                // Get search query from input
                const searchInput = document.getElementById('productSearch');
                const searchQuery = searchInput ? searchInput.value.trim() : '';
                
                // Build URL with all filters
                const params = new URLSearchParams();
                if (searchQuery) {
                    params.append('search', searchQuery);
                }
                params.append('page', '1');
                
                // Add form filters
                const brandSelect = document.querySelector('select[name="brand_id"]');
                if (brandSelect && brandSelect.value) {
                    params.append('brand_id', brandSelect.value);
                }
                
                const vehicleTypeSelect = document.querySelector('select[name="vehicle_type_id"]');
                if (vehicleTypeSelect && vehicleTypeSelect.value) {
                    params.append('vehicle_type_id', vehicleTypeSelect.value);
                }
                
                // Navigate to shop page with all filters
                window.location.href = `/shop?${params.toString()}`;
            });
        }
    }
    
    /**
     * Collect filters from form
     */
    collectFilters() {
        this.currentFilters = {};
        
        const brandSelect = document.querySelector('select[name="brand_id"]');
        if (brandSelect && brandSelect.value) {
            this.currentFilters.brand_id = parseInt(brandSelect.value);
        }
        
        const vehicleTypeSelect = document.querySelector('select[name="vehicle_type_id"]');
        if (vehicleTypeSelect && vehicleTypeSelect.value) {
            this.currentFilters.vehicle_type_id = parseInt(vehicleTypeSelect.value);
        }
        
        // Add more filters as needed
    }
    
    /**
     * Setup sorting
     */
    setupSorting() {
        // This will be implemented when sorting UI is added
    }
    
    /**
     * Setup pagination
     */
    setupPagination() {
        // Pagination is handled by server-side rendering
    }
    
    /**
     * Perform search
     */
    async performSearch(query = null) {
        const searchInput = document.getElementById('productSearch');
        const finalQuery = query || (searchInput ? searchInput.value.trim() : '');
        
        // If query is empty, clear search and show all products
        if (!finalQuery || finalQuery.length === 0) {
            const params = new URLSearchParams();
            params.append('page', '1');
            
            Object.keys(this.currentFilters).forEach(key => {
                if (this.currentFilters[key]) {
                    params.append(key, this.currentFilters[key]);
                }
            });
            
            window.location.href = `/shop?${params.toString()}`;
            return;
        }
        
        // Build URL with filters
        const params = new URLSearchParams();
        params.append('search', finalQuery);  // Use 'search' instead of 'q'
        params.append('page', '1');
        params.append('per_page', '12');
        
        Object.keys(this.currentFilters).forEach(key => {
            if (this.currentFilters[key]) {
                params.append(key, this.currentFilters[key]);
            }
        });
        
        if (this.currentSort && this.currentSort !== 'relevance') {
            params.append('sort', this.currentSort);
        }
        
        // Navigate to shop page with search parameters
        window.location.href = `/shop?${params.toString()}`;
    }
    
    /**
     * Track product click from search results
     */
    async trackClick(productId, query, rank) {
        try {
            await fetch(this.trackClickUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    product_id: productId,
                    query: query,
                    rank: rank
                })
            });
        } catch (error) {
            console.error('Error tracking click:', error);
        }
    }
    
    /**
     * Highlight search terms in text
     */
    highlightText(text, query) {
        if (!query || !text) return text;
        
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<mark class="search-highlight">$1</mark>');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (typeof ProfessionalSearchEngine !== 'undefined') {
        try {
            window.searchEngine = new ProfessionalSearchEngine({
                apiUrl: '/api/search',
                suggestionsUrl: '/api/search/suggestions',
                trackClickUrl: '/api/search/track-click',
                debounceDelay: 300,
                minQueryLength: 2
            });
            
            // Log initialization success (only in development)
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.log('Professional Search Engine initialized successfully');
            }
        } catch (error) {
            console.error('Failed to initialize Professional Search Engine:', error);
        }
    } else {
        console.warn('ProfessionalSearchEngine class not found. Make sure professional_search.js is loaded.');
    }
});

