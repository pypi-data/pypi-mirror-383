Template Tags
=============

Django RemixIcon provides several template tags for rendering icons in your templates.

Loading Template Tags
---------------------

Before using any template tags, you must load them in your template:

.. code-block:: html

    {% load remix_icon_tags %}

remix_icon
----------

The main template tag for rendering RemixIcons.

**Syntax:**

.. code-block:: html

    {% remix_icon icon_name [attribute=value ...] %}

**Parameters:**

- ``icon_name``: The RemixIcon name (e.g., 'ri-home-line') or a variable containing the icon name
- ``attribute=value``: Optional HTML attributes for the icon element

**Examples:**

.. code-block:: html

    <!-- Basic usage -->
    {% remix_icon 'ri-home-line' %}

    <!-- Using a variable -->
    {% remix_icon menu_item.icon %}

    <!-- With CSS class -->
    {% remix_icon 'ri-heart-fill' class='text-red-500' %}

    <!-- With size -->
    {% remix_icon 'ri-star-line' size='24' %}

    <!-- With multiple attributes -->
    {% remix_icon 'ri-settings-line' class='icon-button' size='20' title='Settings' %}

    <!-- With inline styles -->
    {% remix_icon 'ri-download-line' style='color: blue; font-size: 18px;' %}

**Size Attribute:**

The ``size`` attribute is special - it automatically converts to a ``font-size`` CSS property:

.. code-block:: html

    {% remix_icon 'ri-home-line' size='16' %}
    <!-- Renders as: <i class="ri-home-line" style="font-size: 16px;"></i> -->

    {% remix_icon 'ri-home-line' size='1.5em' %}
    <!-- Renders as: <i class="ri-home-line" style="font-size: 1.5em;"></i> -->

**Invalid Icons:**

If an invalid icon name is provided, a question mark icon is rendered instead:

.. code-block:: html

    {% remix_icon 'invalid-icon' %}
    <!-- Renders as: <i class="ri-question-line" title="Invalid icon: invalid-icon"></i> -->

remix_icon_css
--------------

Includes the RemixIcon CSS from CDN.

**Syntax:**

.. code-block:: html

    {% remix_icon_css %}

**Usage:**

Include this tag once in your base template's ``<head>`` section:

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head>
        <title>My Site</title>
        {% load remix_icon_tags %}
        {% remix_icon_css %}
    </head>
    <body>
        <!-- Your content with icons -->
    </body>
    </html>

**Renders as:**

.. code-block:: html

    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.7.0/fonts/remixicon.css" rel="stylesheet">

remix_icon_version
------------------

Returns the RemixIcon version being used by the package.

**Syntax:**

.. code-block:: html

    {% remix_icon_version %}

**Example:**

.. code-block:: html

    <p>Using RemixIcon version: {% remix_icon_version %}</p>
    <!-- Outputs: Using RemixIcon version: 4.7.0 -->

is_remix_icon (Filter)
----------------------

A template filter that checks if a value is a valid RemixIcon name.

**Syntax:**

.. code-block:: html

    {{ icon_name|is_remix_icon }}

**Examples:**

.. code-block:: html

    {% if menu_item.icon|is_remix_icon %}
        {% remix_icon menu_item.icon %}
        {{ menu_item.name }}
    {% else %}
        <span class="no-icon">{{ menu_item.name }}</span>
    {% endif %}

    <!-- In a loop with conditional rendering -->
    {% for item in items %}
        <div class="item">
            {% if item.icon|is_remix_icon %}
                {% remix_icon item.icon class='item-icon' %}
            {% endif %}
            <span class="item-name">{{ item.name }}</span>
        </div>
    {% endfor %}

remix_icon_with_text
--------------------

An inclusion tag that renders an icon with accompanying text in a consistent format.

**Syntax:**

.. code-block:: html

    {% remix_icon_with_text icon_name text [attribute=value ...] %}

**Parameters:**

- ``icon_name``: The RemixIcon name
- ``text``: Text to display alongside the icon
- ``attributes``: Optional HTML attributes for the container span

**Examples:**

.. code-block:: html

    <!-- Basic usage -->
    {% remix_icon_with_text 'ri-home-line' 'Home' %}

    <!-- With model data -->
    {% remix_icon_with_text menu_item.icon menu_item.name %}

    <!-- With custom CSS class -->
    {% remix_icon_with_text 'ri-download-line' 'Download' class='btn btn-primary' %}

    <!-- With click handler -->
    {% remix_icon_with_text 'ri-settings-line' 'Settings' onclick='openSettings()' %}

**Renders as:**

.. code-block:: html

    <span class="btn btn-primary">
        <i class="ri-download-line"></i>
        <span class="icon-text">Download</span>
    </span>

**Custom Template:**

The tag uses the template ``django_remix_icon/icon_with_text.html``. You can override this template to customize the rendering:

.. code-block:: html

    <!-- templates/django_remix_icon/icon_with_text.html -->
    {% load remix_icon_tags %}
    <span{% for key, value in attrs.items %} {{ key }}="{{ value }}"{% endfor %}>
        {% if is_valid_icon %}
            {% remix_icon icon_name %}
        {% endif %}
        {% if text %}
            <span class="icon-text">{{ text }}</span>
        {% endif %}
    </span>

remix_icon_list
---------------

Returns a list of RemixIcon names, optionally filtered by category.

**Syntax:**

.. code-block:: html

    {% remix_icon_list [category=category_name] [limit=number] as variable_name %}

**Parameters:**

- ``category``: Optional category filter (searches icon names for the category string)
- ``limit``: Optional limit on number of icons returned
- ``as variable_name``: Assigns the result to a template variable

**Examples:**

.. code-block:: html

    <!-- Get all icons -->
    {% remix_icon_list as all_icons %}
    <p>Total icons available: {{ all_icons|length }}</p>

    <!-- Get user-related icons -->
    {% remix_icon_list category='user' as user_icons %}
    <div class="icon-picker">
        {% for icon in user_icons %}
            <button data-icon="{{ icon }}">
                {% remix_icon icon %}
            </button>
        {% endfor %}
    </div>

    <!-- Get limited number of icons -->
    {% remix_icon_list limit=20 as featured_icons %}

    <!-- Combine category and limit -->
    {% remix_icon_list category='home' limit=5 as home_icons %}

Common Patterns
---------------

Icon Buttons
~~~~~~~~~~~~

.. code-block:: html

    <button class="icon-btn" onclick="saveDocument()">
        {% remix_icon 'ri-save-line' size='16' %}
        Save
    </button>

Navigation Menu
~~~~~~~~~~~~~~~

.. code-block:: html

    <nav class="main-nav">
        {% for item in menu_items %}
            <a href="{{ item.url }}" class="nav-item">
                {% if item.icon|is_remix_icon %}
                    {% remix_icon item.icon class='nav-icon' %}
                {% endif %}
                <span class="nav-text">{{ item.name }}</span>
            </a>
        {% endfor %}
    </nav>

Icon Grid
~~~~~~~~~

.. code-block:: html

    <div class="icon-grid">
        {% remix_icon_list category='business' limit=12 as business_icons %}
        {% for icon in business_icons %}
            <div class="icon-card">
                {% remix_icon icon size='32' %}
                <small>{{ icon }}</small>
            </div>
        {% endfor %}
    </div>

Status Indicators
~~~~~~~~~~~~~~~~~

.. code-block:: html

    <div class="status-list">
        {% for task in tasks %}
            <div class="task-item">
                {% if task.completed %}
                    {% remix_icon 'ri-check-circle-fill' class='text-green-500' %}
                {% elif task.in_progress %}
                    {% remix_icon 'ri-time-line' class='text-blue-500' %}
                {% else %}
                    {% remix_icon 'ri-circle-line' class='text-gray-400' %}
                {% endif %}
                <span>{{ task.name }}</span>
            </div>
        {% endfor %}
    </div>

Dynamic Icon Selection
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: html

    <!-- JavaScript-powered icon selector -->
    <div class="icon-selector">
        <input type="hidden" name="selected_icon" id="selected-icon">
        <div class="selected-icon">
            {% remix_icon 'ri-image-line' id='preview-icon' size='24' %}
        </div>
        <div class="icon-options">
            {% remix_icon_list category='media' limit=20 as media_icons %}
            {% for icon in media_icons %}
                <button type="button" onclick="selectIcon('{{ icon }}')" class="icon-option">
                    {% remix_icon icon size='20' %}
                </button>
            {% endfor %}
        </div>
    </div>

    <script>
    function selectIcon(iconName) {
        document.getElementById('selected-icon').value = iconName;
        document.getElementById('preview-icon').className = iconName;
    }
    </script>

CSS Styling Tips
----------------

Basic Icon Styling
~~~~~~~~~~~~~~~~~~

.. code-block:: css

    /* Set default icon size */
    .remix-icon {
        font-size: 16px;
    }

    /* Icon buttons */
    .icon-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border: 1px solid #ddd;
        background: white;
        border-radius: 4px;
        cursor: pointer;
    }

    .icon-btn:hover {
        background: #f5f5f5;
    }

Responsive Icons
~~~~~~~~~~~~~~~~

.. code-block:: css

    /* Responsive icon sizes */
    .nav-icon {
        font-size: 18px;
    }

    @media (max-width: 768px) {
        .nav-icon {
            font-size: 16px;
        }
    }

Icon Colors
~~~~~~~~~~~

.. code-block:: css

    /* Status colors */
    .icon-success { color: #28a745; }
    .icon-warning { color: #ffc107; }
    .icon-danger { color: #dc3545; }
    .icon-info { color: #17a2b8; }

    /* Theme colors */
    .icon-primary { color: #007bff; }
    .icon-secondary { color: #6c757d; }

Next Steps
----------

- :doc:`customization` - Learn how to customize widget appearance
- :doc:`api/templatetags` - Complete API reference for template tags
