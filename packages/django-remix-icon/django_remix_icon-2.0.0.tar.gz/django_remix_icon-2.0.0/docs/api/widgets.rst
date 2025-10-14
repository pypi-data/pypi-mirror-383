Widgets API Reference
=====================

This page documents the form widgets provided by Django RemixIcon.

.. automodule:: django_remix_icon.widgets
   :members:
   :undoc-members:
   :show-inheritance:

IconSelectWidget
----------------

.. autoclass:: django_remix_icon.widgets.IconSelectWidget
   :members:
   :undoc-members:
   :show-inheritance:

   **Description:**

   The main widget for selecting RemixIcons with autocomplete and preview functionality.
   This widget provides a rich user interface for selecting icons in Django admin and forms.

   **Features:**

   - Autocomplete search functionality
   - Live icon preview
   - Keyboard navigation support
   - Integration with Django admin
   - Works with inline models

   **Media:**

   The widget includes the following static files:

   - CSS: ``django_remix_icon/css/icon_select.css``
   - JavaScript: ``django_remix_icon/js/icon_select.js``

   **Usage:**

   .. code-block:: python

       from django import forms
       from django_remix_icon.widgets import IconSelectWidget

       class MyForm(forms.Form):
           icon = forms.CharField(widget=IconSelectWidget())

IconPreviewWidget
-----------------

.. autoclass:: django_remix_icon.widgets.IconPreviewWidget
   :members:
   :undoc-members:
   :show-inheritance:

   **Description:**

   A simpler widget that shows icon preview without autocomplete functionality.
   Useful for read-only displays or simple forms where autocomplete is not needed.

   **Features:**

   - Simple icon preview
   - Lightweight (less JavaScript)
   - Good for read-only or simple forms

   **Media:**

   The widget includes:

   - CSS: ``django_remix_icon/css/icon_preview.css``

   **Usage:**

   .. code-block:: python

       from django import forms
       from django_remix_icon.widgets import IconPreviewWidget

       class SimpleForm(forms.Form):
           icon = forms.CharField(widget=IconPreviewWidget())

Widget Usage Examples
--------------------

Basic Widget Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django import forms
    from django_remix_icon.widgets import IconSelectWidget

    class MyForm(forms.Form):
        name = forms.CharField(max_length=100)
        icon = forms.CharField(widget=IconSelectWidget())

Custom Widget Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class CustomForm(forms.Form):
        icon = forms.CharField(
            widget=IconSelectWidget(attrs={
                'class': 'my-custom-class',
                'data-placeholder': 'Choose an icon...',
                'style': 'width: 300px;'
            })
        )

ModelForm Widget Override
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django import forms
    from django_remix_icon.widgets import IconSelectWidget
    from .models import MyModel

    class MyModelForm(forms.ModelForm):
        class Meta:
            model = MyModel
            fields = ['name', 'icon', 'description']
            widgets = {
                'icon': IconSelectWidget(attrs={
                    'class': 'admin-icon-widget'
                })
            }

Admin Widget Integration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.contrib import admin
    from django import forms
    from django_remix_icon.widgets import IconSelectWidget
    from .models import Category

    class CategoryForm(forms.ModelForm):
        class Meta:
            model = Category
            fields = '__all__'
            widgets = {
                'icon': IconSelectWidget(attrs={
                    'class': 'category-icon-widget'
                })
            }

    @admin.register(Category)
    class CategoryAdmin(admin.ModelAdmin):
        form = CategoryForm

Inline Widget Usage
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class MenuItemInline(admin.TabularInline):
        model = MenuItem
        fields = ('name', 'icon', 'url', 'order')
        extra = 1

        def formfield_for_dbfield(self, db_field, request, **kwargs):
            if db_field.name == 'icon':
                kwargs['widget'] = IconSelectWidget(attrs={
                    'class': 'inline-icon-widget',
                    'style': 'width: 200px;'
                })
            return super().formfield_for_dbfield(db_field, request, **kwargs)

Widget Customization
--------------------

Custom CSS Classes
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    widget = IconSelectWidget(attrs={
        'class': 'my-icon-widget custom-style'
    })

Custom Data Attributes
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    widget = IconSelectWidget(attrs={
        'data-search-url': '/custom/icon/search/',
        'data-limit': '50',
        'data-placeholder': 'Select your icon...'
    })

Custom Styling
~~~~~~~~~~~~~~

.. code-block:: css

    /* Custom CSS for widget styling */
    .my-icon-widget {
        max-width: 400px;
    }

    .my-icon-widget .icon-search-input {
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
    }

    .my-icon-widget .icon-preview {
        background-color: #f8f9fa;
        border-radius: 6px;
        padding: 12px;
    }

Widget Templates
----------------

Default Template Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``IconSelectWidget`` uses the template ``django_remix_icon/icon_select_widget.html``:

.. code-block:: html

    {% load remix_icon_tags %}
    <div class="remix-icon-widget-container">
        <div class="icon-search-wrapper">
            <input type="text" class="icon-search-input" placeholder="Search RemixIcons..." autocomplete="off">
            <div class="icon-search-results"></div>
        </div>
        {{ widget }}
        <div class="icon-preview-wrapper">
            {% if widget.value %}
                <div class="current-icon-preview">
                    {% remix_icon widget.value %}
                    <span class="icon-name">{{ widget.value }}</span>
                </div>
            {% else %}
                <div class="current-icon-preview" style="display: none;">
                    <i class=""></i>
                    <span class="icon-name"></span>
                </div>
            {% endif %}
        </div>
    </div>

Custom Template Override
~~~~~~~~~~~~~~~~~~~~~~~~

You can override the widget template by creating your own:

.. code-block:: python

    class CustomIconWidget(IconSelectWidget):
        template_name = 'myapp/custom_icon_widget.html'

.. code-block:: html

    <!-- templates/myapp/custom_icon_widget.html -->
    {% load remix_icon_tags %}
    <div class="custom-icon-widget">
        <label for="{{ widget.attrs.id }}">Choose Icon:</label>
        <div class="icon-selector">
            <input type="text" class="icon-search-input" placeholder="Type to search..." autocomplete="off">
            <div class="icon-search-results"></div>
        </div>
        {{ widget }}
        {% if widget.value %}
            <div class="selected-icon">
                {% remix_icon widget.value size='24' %}
                <span>{{ widget.value }}</span>
            </div>
        {% endif %}
    </div>

JavaScript API
--------------

Widget Initialization
~~~~~~~~~~~~~~~~~~~~~

The widget JavaScript automatically initializes when the DOM is ready:

.. code-block:: javascript

    // Automatic initialization
    document.addEventListener('DOMContentLoaded', function() {
        DjangoRemixIcon.initializeIconWidgets();
    });

Manual Initialization
~~~~~~~~~~~~~~~~~~~~~

You can manually initialize widgets:

.. code-block:: javascript

    // Initialize specific widget
    const widget = document.querySelector('.remix-icon-widget');
    DjangoRemixIcon.initializeWidget(widget);

    // Initialize all widgets
    DjangoRemixIcon.initializeIconWidgets();

Custom Event Handling
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: javascript

    // Listen for icon selection events
    document.addEventListener('iconSelected', function(event) {
        const { iconName, widget } = event.detail;
        console.log('Icon selected:', iconName);
    });

Widget Configuration
--------------------

Search URL Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

The widget uses AJAX to search for icons. Configure the search URL:

.. code-block:: python

    # In your widget
    widget = IconSelectWidget(attrs={
        'data-icon-search-url': reverse('django_remix_icon:icon_search')
    })

Search Parameters
~~~~~~~~~~~~~~~~~

The search endpoint accepts these parameters:

- ``q``: Search query string
- ``limit``: Maximum number of results (default: 20)

.. code-block:: javascript

    // Example AJAX request
    fetch('/admin/remix-icon/search/?q=home&limit=10')
        .then(response => response.json())
        .then(data => {
            console.log(data.results);
        });

Widget States
-------------

The widget manages several states:

Loading State
~~~~~~~~~~~~~

.. code-block:: css

    .icon-search-results .loading {
        padding: 15px;
        text-align: center;
        color: #6c757d;
    }

No Results State
~~~~~~~~~~~~~~~~

.. code-block:: css

    .icon-search-results .no-results {
        padding: 15px;
        text-align: center;
        color: #6c757d;
    }

Selected State
~~~~~~~~~~~~~~

.. code-block:: css

    .icon-search-result.selected {
        background-color: #007cba;
        color: white;
    }

Accessibility
-------------

Keyboard Navigation
~~~~~~~~~~~~~~~~~~~

The widget supports full keyboard navigation:

- **Arrow Keys**: Navigate through search results
- **Enter**: Select highlighted icon
- **Escape**: Close search results
- **Tab**: Move focus to next element

ARIA Attributes
~~~~~~~~~~~~~~~

The widget includes appropriate ARIA attributes for screen readers:

.. code-block:: html

    <input type="text"
           class="icon-search-input"
           role="combobox"
           aria-expanded="false"
           aria-autocomplete="list"
           aria-haspopup="listbox">

Performance Considerations
-------------------------

Debounced Search
~~~~~~~~~~~~~~~~

The search input is debounced to prevent excessive API calls:

.. code-block:: javascript

    // 150ms debounce on search input
    searchInput.addEventListener('input', debounce(performSearch, 150));

Result Caching
~~~~~~~~~~~~~~

Search results can be cached to improve performance:

.. code-block:: javascript

    // Simple result caching
    const searchCache = new Map();

    function cachedSearch(query) {
        if (searchCache.has(query)) {
            return Promise.resolve(searchCache.get(query));
        }
        return fetch(`/search/?q=${query}`)
            .then(response => response.json())
            .then(data => {
                searchCache.set(query, data);
                return data;
            });
    }

Browser Compatibility
---------------------

The widget JavaScript is compatible with:

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

For older browsers, you may need polyfills for:

- ``fetch()``
- ``Promise``
- ``Map``
- Arrow functions
