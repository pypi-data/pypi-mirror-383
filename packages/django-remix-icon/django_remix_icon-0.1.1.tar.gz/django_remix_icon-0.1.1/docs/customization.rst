Customization
=============

This guide covers how to customize Django RemixIcon to fit your project's needs.

Widget Customization
--------------------

Custom CSS Styling
~~~~~~~~~~~~~~~~~~~

You can override the default widget styles by including custom CSS:

.. code-block:: css

    /* Custom styles for the icon widget */
    .remix-icon-widget {
        max-width: 500px; /* Increase widget width */
    }

    .icon-search-input {
        padding: 12px 16px; /* Larger padding */
        border-radius: 8px; /* Rounded corners */
        border: 2px solid #e1e5e9; /* Thicker border */
        font-size: 16px; /* Larger font */
    }

    .icon-search-input:focus {
        border-color: #007cba;
        box-shadow: 0 0 0 3px rgba(0, 124, 186, 0.1);
    }

    /* Customize search results */
    .icon-search-results {
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        max-height: 300px; /* Increase dropdown height */
    }

    .icon-search-result {
        padding: 12px 16px; /* Match input padding */
    }

    .icon-search-result:hover {
        background-color: #f8f9fa;
    }

    .icon-search-result.selected {
        background-color: #007cba;
    }

    /* Customize icon preview */
    .icon-preview {
        border-radius: 8px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }

    .icon-preview i {
        font-size: 24px; /* Larger preview icon */
        color: #007cba;
    }

Dark Theme Support
~~~~~~~~~~~~~~~~~~

Add dark theme styles for better integration:

.. code-block:: css

    /* Dark theme styles */
    @media (prefers-color-scheme: dark) {
        .remix-icon-widget {
            --bg-color: #2d3748;
            --border-color: #4a5568;
            --text-color: #f7fafc;
            --hover-bg: #4a5568;
            --focus-color: #63b3ed;
        }

        .icon-search-input {
            background-color: var(--bg-color);
            border-color: var(--border-color);
            color: var(--text-color);
        }

        .icon-search-input:focus {
            border-color: var(--focus-color);
            box-shadow: 0 0 0 3px rgba(99, 179, 237, 0.2);
        }

        .icon-search-results {
            background-color: var(--bg-color);
            border-color: var(--border-color);
        }

        .icon-search-result:hover {
            background-color: var(--hover-bg);
        }

        .icon-preview {
            background-color: var(--bg-color);
            border-color: var(--border-color);
            color: var(--text-color);
        }
    }

Custom Widget Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can create your own widget based on the provided ones:

.. code-block:: python

    # widgets.py
    from django_remix_icon.widgets import IconSelectWidget

    class CustomIconWidget(IconSelectWidget):
        template_name = 'myapp/custom_icon_widget.html'

        class Media:
            css = {
                'all': (
                    'django_remix_icon/css/icon_select.css',
                    'myapp/css/custom_icon_widget.css',
                )
            }
            js = (
                'django_remix_icon/js/icon_select.js',
                'myapp/js/custom_icon_widget.js',
            )

        def __init__(self, attrs=None):
            default_attrs = {'class': 'my-custom-icon-widget'}
            if attrs:
                default_attrs.update(attrs)
            super().__init__(default_attrs)

    # forms.py
    from django import forms
    from .widgets import CustomIconWidget

    class MyForm(forms.Form):
        icon = forms.CharField(widget=CustomIconWidget())

Template Customization
----------------------

Custom Icon Rendering
~~~~~~~~~~~~~~~~~~~~~~

Override the default template tags behavior by creating custom template tags:

.. code-block:: python

    # templatetags/my_icon_tags.py
    from django import template
    from django.utils.safestring import mark_safe
    from django_remix_icon.templatetags.remix_icon_tags import remix_icon as base_remix_icon

    register = template.Library()

    @register.simple_tag
    def my_remix_icon(icon_name, **kwargs):
        """Custom icon rendering with additional features"""
        # Add default CSS class
        css_classes = kwargs.get('class', '').split()
        css_classes.append('my-icon')
        kwargs['class'] = ' '.join(css_classes)

        # Add data attributes for JavaScript
        kwargs['data-icon'] = icon_name

        return base_remix_icon(icon_name, **kwargs)

Custom Inclusion Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~

Override the included templates:

.. code-block:: html

    <!-- templates/django_remix_icon/icon_with_text.html -->
    {% load remix_icon_tags %}
    <div class="icon-text-wrapper"{% for key, value in attrs.items %} {{ key }}="{{ value }}"{% endfor %}>
        {% if is_valid_icon %}
            <span class="icon-container">
                {% remix_icon icon_name %}
            </span>
        {% endif %}
        {% if text %}
            <span class="text-container">{{ text }}</span>
        {% endif %}
    </div>

Field Customization
-------------------

Custom Field with Additional Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extend the IconField to add custom functionality:

.. code-block:: python

    # fields.py
    from django_remix_icon.fields import IconField as BaseIconField
    from django.core.exceptions import ValidationError

    class CategoryIconField(BaseIconField):
        """IconField that only allows category-related icons"""

        def __init__(self, *args, **kwargs):
            self.allowed_categories = kwargs.pop('allowed_categories', ['user', 'home', 'business'])
            super().__init__(*args, **kwargs)

        def validate(self, value, model_instance):
            super().validate(value, model_instance)
            if value:
                # Check if icon belongs to allowed categories
                if not any(cat in value.lower() for cat in self.allowed_categories):
                    raise ValidationError(
                        f"Icon must be from categories: {', '.join(self.allowed_categories)}"
                    )

    # Usage in models
    class Category(models.Model):
        name = models.CharField(max_length=100)
        icon = CategoryIconField(allowed_categories=['folder', 'tag', 'bookmark'])

Custom Form Field
~~~~~~~~~~~~~~~~~

Create a custom form field with additional validation:

.. code-block:: python

    # forms.py
    from django import forms
    from django_remix_icon.fields import IconFormField as BaseIconFormField
    from django_remix_icon.remix_icons import get_icon_names

    class FilteredIconFormField(BaseIconFormField):
        def __init__(self, icon_filter=None, *args, **kwargs):
            self.icon_filter = icon_filter or []
            super().__init__(*args, **kwargs)

            if self.icon_filter:
                # Filter choices based on the filter
                all_icons = get_icon_names()
                filtered_icons = [
                    icon for icon in all_icons
                    if any(f in icon.lower() for f in self.icon_filter)
                ]
                self.choices = [(icon, icon.replace('ri-', '').replace('-', ' ').title())
                               for icon in filtered_icons]

Admin Customization
-------------------

Custom Admin Widget Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Customize how the widget appears in Django admin:

.. code-block:: python

    # admin.py
    from django.contrib import admin
    from django import forms
    from django_remix_icon.widgets import IconSelectWidget

    class CustomIconWidget(IconSelectWidget):
        def __init__(self, attrs=None):
            default_attrs = {
                'class': 'custom-admin-icon-widget',
                'data-placeholder': 'Choose an icon...',
            }
            if attrs:
                default_attrs.update(attrs)
            super().__init__(default_attrs)

    class MyModelForm(forms.ModelForm):
        class Meta:
            model = MyModel
            fields = '__all__'
            widgets = {
                'icon': CustomIconWidget(),
            }

    @admin.register(MyModel)
    class MyModelAdmin(admin.ModelAdmin):
        form = MyModelForm

Inline Customization
~~~~~~~~~~~~~~~~~~~~~

Customize how the widget appears in inline admin forms:

.. code-block:: python

    class MyInlineForm(forms.ModelForm):
        class Meta:
            model = MyInlineModel
            fields = '__all__'
            widgets = {
                'icon': IconSelectWidget(attrs={
                    'class': 'inline-icon-widget',
                    'style': 'width: 200px;'
                }),
            }

    class MyInline(admin.TabularInline):
        model = MyInlineModel
        form = MyInlineForm
        extra = 1

JavaScript Customization
------------------------

Extending Widget JavaScript
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add custom JavaScript functionality to the widget:

.. code-block:: javascript

    // static/js/custom_icon_widget.js
    (function() {
        'use strict';

        // Wait for the base widget to initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Extend existing functionality
            if (window.DjangoRemixIcon) {
                const originalInit = window.DjangoRemixIcon.initializeWidget;

                window.DjangoRemixIcon.initializeWidget = function(widget) {
                    // Call original initialization
                    originalInit(widget);

                    // Add custom functionality
                    addCustomFeatures(widget);
                };
            }
        });

        function addCustomFeatures(widget) {
            const searchInput = widget.querySelector('.icon-search-input');
            if (searchInput) {
                // Add custom keyboard shortcuts
                searchInput.addEventListener('keydown', function(e) {
                    if (e.ctrlKey && e.key === 'k') {
                        e.preventDefault();
                        this.focus();
                        this.select();
                    }
                });

                // Add custom search behavior
                searchInput.addEventListener('input', debounce(function() {
                    // Custom search logic
                    console.log('Custom search for:', this.value);
                }, 300));
            }
        }

        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    })();

Custom Icon Categories
~~~~~~~~~~~~~~~~~~~~~~

Create a system for categorizing icons:

.. code-block:: javascript

    // static/js/icon_categories.js
    const ICON_CATEGORIES = {
        'navigation': [
            'ri-home-line', 'ri-arrow-left-line', 'ri-arrow-right-line',
            'ri-menu-line', 'ri-more-line'
        ],
        'actions': [
            'ri-add-line', 'ri-edit-line', 'ri-delete-bin-line',
            'ri-save-line', 'ri-download-line'
        ],
        'communication': [
            'ri-mail-line', 'ri-phone-line', 'ri-message-line',
            'ri-chat-1-line'
        ],
        'media': [
            'ri-image-line', 'ri-video-line', 'ri-music-line',
            'ri-camera-line'
        ]
    };

    function getIconsByCategory(category) {
        return ICON_CATEGORIES[category] || [];
    }

    function getCategoryForIcon(icon) {
        for (const [category, icons] of Object.entries(ICON_CATEGORIES)) {
            if (icons.includes(icon)) {
                return category;
            }
        }
        return 'other';
    }

URL Configuration Customization
-------------------------------

Custom URL Patterns
~~~~~~~~~~~~~~~~~~~~

Customize the URL patterns for the package views:

.. code-block:: python

    # urls.py
    from django.urls import path
    from django_remix_icon import views

    # Custom URL configuration
    app_name = 'custom_remix_icon'

    urlpatterns = [
        path('icon-search/', views.IconSearchView.as_view(), name='icon_search'),
        path('icon-list/', views.icon_list_view, name='icon_list'),
        # Add custom endpoints
        path('icon-categories/', custom_category_view, name='icon_categories'),
    ]

    # In your main urls.py
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('custom-icons/', include('myapp.urls')),
    ]

Performance Optimization
------------------------

Caching Icon Data
~~~~~~~~~~~~~~~~~

Implement custom caching for better performance:

.. code-block:: python

    # utils.py
    from django.core.cache import cache
    from django_remix_icon.remix_icons import get_icon_names

    def get_cached_icons():
        """Get icons with caching"""
        icons = cache.get('remix_icons_list')
        if icons is None:
            icons = get_icon_names()
            cache.set('remix_icons_list', icons, 3600)  # Cache for 1 hour
        return icons

Custom Search Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement more sophisticated search:

.. code-block:: python

    # views.py
    from django.http import JsonResponse
    from django.views.generic import View
    from django.utils.decorators import method_decorator
    from django.views.decorators.csrf import csrf_exempt
    import re

    @method_decorator(csrf_exempt, name='dispatch')
    class AdvancedIconSearchView(View):
        def get(self, request):
            query = request.GET.get('q', '').lower().strip()
            limit = int(request.GET.get('limit', 20))

            if not query:
                return JsonResponse({'results': [], 'total': 0})

            icons = get_cached_icons()

            # Advanced search with scoring
            results = []
            for icon in icons:
                score = self.calculate_relevance_score(icon, query)
                if score > 0:
                    results.append({
                        'icon': icon,
                        'score': score,
                        'value': icon,
                        'label': icon.replace('ri-', '').replace('-', ' ').title()
                    })

            # Sort by relevance score
            results.sort(key=lambda x: x['score'], reverse=True)
            results = results[:limit]

            return JsonResponse({
                'results': [r for r in results],
                'total': len(results)
            })

        def calculate_relevance_score(self, icon, query):
            icon_lower = icon.lower()

            # Exact match
            if query in icon_lower:
                if icon_lower.startswith(query):
                    return 100  # Starts with query
                elif query in icon_lower.replace('ri-', ''):
                    return 80   # Contains query in main part
                else:
                    return 60   # Contains query anywhere

            # Fuzzy matching
            query_words = query.split()
            icon_words = icon_lower.replace('ri-', '').split('-')

            matches = sum(1 for qw in query_words for iw in icon_words if qw in iw)
            if matches > 0:
                return 40 + (matches * 10)

            return 0

Integration Examples
-------------------

Bootstrap Integration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: html

    <!-- Bootstrap-styled icon buttons -->
    <div class="btn-group" role="group">
        <button type="button" class="btn btn-outline-primary">
            {% remix_icon 'ri-home-line' %} Home
        </button>
        <button type="button" class="btn btn-outline-primary">
            {% remix_icon 'ri-user-line' %} Profile
        </button>
        <button type="button" class="btn btn-outline-primary">
            {% remix_icon 'ri-settings-line' %} Settings
        </button>
    </div>

Tailwind CSS Integration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: html

    <!-- Tailwind-styled icon navigation -->
    <nav class="flex space-x-4">
        <a href="#" class="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50">
            {% remix_icon 'ri-dashboard-line' class='w-5 h-5' %}
            <span>Dashboard</span>
        </a>
        <a href="#" class="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50">
            {% remix_icon 'ri-team-line' class='w-5 h-5' %}
            <span>Team</span>
        </a>
    </nav>

Next Steps
----------

- :doc:`api/fields` - Complete API reference
- :doc:`api/widgets` - Widget API documentation
- :doc:`api/templatetags` - Template tags API reference
