/**
 * Django RemixIcon Widget JavaScript
 * Provides autocomplete functionality for RemixIcon selection
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeIconWidgets();
    });

    // Also initialize when Django admin adds new inline forms
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('formset:added', function() {
            setTimeout(initializeIconWidgets, 100);
        });
    }

    function initializeIconWidgets() {
        const widgets = document.querySelectorAll('.remix-icon-widget');
        widgets.forEach(initializeWidget);
    }

    function initializeWidget(widget) {
        // Skip if already initialized
        if (widget.classList.contains('initialized')) {
            return;
        }
        widget.classList.add('initialized');

        const searchInput = widget.querySelector('.icon-search-input');
        const searchResults = widget.querySelector('.icon-search-results');
        const hiddenInput = widget.querySelector('input[type="hidden"]');
        const preview = widget.querySelector('.icon-preview');

        if (!searchInput || !searchResults || !hiddenInput) {
            console.error('Required elements not found in icon widget', {
                searchInput: !!searchInput,
                searchResults: !!searchResults,
                hiddenInput: !!hiddenInput
            });
            return;
        }

        let currentSelection = -1;
        let searchTimeout = null;

        // Set initial value
        if (hiddenInput.value) {
            updatePreview(hiddenInput.value);
        }

        // Search input event handlers
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();

            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                performSearch(query);
            }, 150);
        });

        searchInput.addEventListener('focus', function() {
            if (searchResults.children.length > 0) {
                showResults();
            } else if (!this.value.trim()) {
                performSearch('');
            }
        });

        searchInput.addEventListener('blur', function() {
            // Delay hiding to allow click on results
            setTimeout(hideResults, 150);
        });

        searchInput.addEventListener('keydown', function(e) {
            const results = searchResults.querySelectorAll('.icon-search-result');

            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    currentSelection = Math.min(currentSelection + 1, results.length - 1);
                    updateSelection(results);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    currentSelection = Math.max(currentSelection - 1, -1);
                    updateSelection(results);
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (currentSelection >= 0 && results[currentSelection]) {
                        selectIcon(results[currentSelection]);
                    }
                    break;
                case 'Escape':
                    hideResults();
                    searchInput.blur();
                    break;
            }
        });

        // Search results event handlers
        searchResults.addEventListener('mousedown', function(e) {
            e.preventDefault(); // Prevent blur event
        });

        searchResults.addEventListener('click', function(e) {
            const result = e.target.closest('.icon-search-result');
            if (result) {
                selectIcon(result);
            }
        });

        function performSearch(query) {
            showLoading();

            const searchUrl = searchInput.getAttribute('data-icon-search-url');
            if (!searchUrl) {
                console.error('Search URL not found');
                showError('Configuration error');
                return;
            }

            const params = new URLSearchParams({
                q: query,
                limit: 50
            });

            fetch(`${searchUrl}?${params}`)
                .then(response => response.json())
                .then(data => {
                    displayResults(data.results);
                })
                .catch(error => {
                    console.error('Icon search error:', error);
                    showError('Error loading icons');
                });
        }

        function displayResults(results) {
            searchResults.innerHTML = '';
            currentSelection = -1;

            if (results.length === 0) {
                searchResults.innerHTML = '<div class="no-results">No icons found</div>';
                showResults();
                return;
            }

            results.forEach(function(result, index) {
                const div = document.createElement('div');
                div.className = 'icon-search-result';
                div.dataset.value = result.value;

                // Create icon element
                const iconEl = document.createElement('i');
                iconEl.className = result.icon || result.value;

                // Create label element
                const labelEl = document.createElement('span');
                labelEl.className = 'icon-label';
                labelEl.textContent = result.label;

                // Create value element (small text showing full icon name)
                const valueEl = document.createElement('small');

                // Append all elements
                div.appendChild(iconEl);
                div.appendChild(labelEl);
                div.appendChild(valueEl);

                searchResults.appendChild(div);
            });

            showResults();
        }

        function selectIcon(resultElement) {
            const value = resultElement.dataset.value;

            // Update hidden input (this is what gets saved)
            hiddenInput.value = value;

            // Update search input display
            searchInput.value = value;

            // Trigger change event for Django
            const event = new Event('change', { bubbles: true });
            hiddenInput.dispatchEvent(event);

            // Update preview
            updatePreview(value);

            // Hide results
            hideResults();
        }

        function updatePreview(iconValue) {
            if (!preview) return;

            const iconElement = preview.querySelector('i');
            const nameElement = preview.querySelector('.icon-name, .icon-text');

            if (iconValue) {
                iconElement.className = iconValue;
                if (nameElement) {
                    nameElement.textContent = iconValue;
                }
                preview.style.display = 'flex';
            } else {
                iconElement.className = '';
                if (nameElement) {
                    nameElement.textContent = '';
                }
                preview.style.display = 'none';
            }
        }

        function updateSelection(results) {
            results.forEach(function(result, index) {
                result.classList.toggle('selected', index === currentSelection);
            });

            // Scroll to selected item
            if (currentSelection >= 0 && results[currentSelection]) {
                results[currentSelection].scrollIntoView({
                    block: 'nearest'
                });
            }
        }

        function showResults() {
            searchResults.classList.add('show');
        }

        function hideResults() {
            searchResults.classList.remove('show');
        }

        function showLoading() {
            searchResults.innerHTML = '<div class="loading">Loading icons...</div>';
            showResults();
        }

        function showError(message) {
            searchResults.innerHTML = `<div class="no-results">${message}</div>`;
            showResults();
        }

        function getSearchUrl(widget) {
            // Try to get URL from data attribute or construct it
            const searchUrl = searchInput.dataset.iconSearchUrl ||
                             widget.dataset.iconSearchUrl ||
                             '/admin/django_remix_icon/search/';
            return searchUrl;
        }
    }

    // Utility function to get CSRF token for Django
    function getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : null;
    }

    // Export for potential external use
    window.DjangoRemixIcon = {
        initializeWidget: initializeWidget,
        initializeIconWidgets: initializeIconWidgets
    };

})();
