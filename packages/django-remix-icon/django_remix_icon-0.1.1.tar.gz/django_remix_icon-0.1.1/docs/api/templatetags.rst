Template Tags API Reference
============================

This page provides complete API documentation for Django RemixIcon template tags.

.. automodule:: django_remix_icon.templatetags.remix_icon_tags
   :members:
   :undoc-members:
   :show-inheritance:

Loading Template Tags
---------------------

Before using any template tag, load the tags in your template:

.. code-block:: html

    {% load remix_icon_tags %}

Template Tags
-------------

remix_icon
~~~~~~~~~~

.. autofunction:: django_remix_icon.templatetags.remix_icon_tags.remix_icon

**Function Signature:**

.. code-block:: python

    def remix_icon(icon_name, **kwargs):
        """
        Render a RemixIcon with optional attributes.

        Args:
            icon_name (str): The RemixIcon name (e.g., 'ri-home-line')
            **kwargs: Additional HTML attributes

        Returns:
            SafeString: HTML <i> tag with the icon
        """

**Parameters:**

- ``icon_name`` (str): Required. The RemixIcon class name (e.g., 'ri-home-line')
- ``**kwargs``: Optional HTML attributes for the ``<i>`` element

**Special Attributes:**

- ``class`` (str): Additional CSS classes (combined with icon class)
- ``size`` (str|int): Font size (converted to CSS font-size property)
- ``style`` (str): Inline CSS styles

**Returns:**

``SafeString`` containing an HTML ``<i>`` element.

**Examples:**

.. code-block:: html

    <!-- Basic usage -->
    {% remix_icon 'ri-home-line' %}
    <!-- Output: <i class="ri-home-line"></i> -->

    <!-- With CSS class -->
    {% remix_icon 'ri-heart-fill' class='text-red-500' %}
    <!-- Output: <i class="ri-heart-fill text-red-500"></i> -->

    <!-- With size -->
    {% remix_icon 'ri-star-line' size='24' %}
    <!-- Output: <i class="ri-star-line" style="font-size: 24px;"></i> -->

    <!-- With multiple attributes -->
    {% remix_icon 'ri-settings-line' class='icon-btn' title='Settings' data-action='open-settings' %}
    <!-- Output: <i class="ri-settings-line icon-btn" title="Settings" data-action="open-settings"></i> -->

**Error Handling:**

If an invalid icon name is provided:

.. code-block:: html

    {% remix_icon 'invalid-icon' %}
    <!-- Output: <i class="ri-question-line" title="Invalid icon: invalid-icon"></i> -->

remix_icon_css
~~~~~~~~~~~~~~

.. autofunction:: django_remix_icon.templatetags.remix_icon_tags.remix_icon_css

**Function Signature:**

.. code-block:: python

    def remix_icon_css():
        """
        Include RemixIcon CSS from CDN.

        Returns:
            SafeString: HTML link tag for RemixIcon CSS
        """

**Parameters:**

None.

**Returns:**

``SafeString`` containing an HTML ``<link>`` element.

**Usage:**

.. code-block:: html

    {% remix_icon_css %}
    <!-- Output: <link href="https://cdn.jsdelivr.net/npm/remixicon@4.7.0/fonts/remixicon.css" rel="stylesheet"> -->

**Best Practices:**

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
        <!-- Your content -->
    </body>
    </html>

remix_icon_version
~~~~~~~~~~~~~~~~~~

.. autofunction:: django_remix_icon.templatetags.remix_icon_tags.remix_icon_version

**Function Signature:**

.. code-block:: python

    def remix_icon_version():
        """
        Get the RemixIcon version being used.

        Returns:
            str: Version string
        """

**Parameters:**

None.

**Returns:**

``str`` containing the RemixIcon version number.

**Usage:**

.. code-block:: html

    <p>RemixIcon version: {% remix_icon_version %}</p>
    <!-- Output: RemixIcon version: 4.7.0 -->

remix_icon_with_text
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: django_remix_icon.templatetags.remix_icon_tags.remix_icon_with_text

**Function Signature:**

.. code-block:: python

    def remix_icon_with_text(icon_name, text, **kwargs):
        """
        Render an icon with accompanying text.

        Args:
            icon_name (str): The RemixIcon name
            text (str): Text to display alongside the icon
            **kwargs: Additional HTML attributes for the container

        Returns:
            dict: Template context for rendering
        """

**Parameters:**

- ``icon_name`` (str): Required. The RemixIcon class name
- ``text`` (str): Required. Text to display with the icon
- ``**kwargs``: Optional HTML attributes for the container element

**Returns:**

Rendered template context using ``django_remix_icon/icon_with_text.html``.

**Usage:**

.. code-block:: html

    {% remix_icon_with_text 'ri-home-line' 'Home' %}
    {% remix_icon_with_text menu_item.icon menu_item.name class='nav-item' %}

**Template Context:**

The inclusion tag provides these context variables:

- ``icon_name``: The icon name
- ``text``: The text to display
- ``attrs``: Dictionary of HTML attributes
- ``is_valid_icon``: Boolean indicating if the icon is valid

**Default Template:**

.. code-block:: html

    <!-- django_remix_icon/icon_with_text.html -->
    {% load remix_icon_tags %}
    <span{% for key, value in attrs.items %} {{ key }}="{{ value }}"{% endfor %}>
        {% if is_valid_icon %}
            {% remix_icon icon_name %}
        {% else %}
            <i class="ri-question-line" title="Invalid icon: {{ icon_name }}"></i>
        {% endif %}
        {% if text %}
            <span class="icon-text">{{ text }}</span>
        {% endif %}
    </span>

remix_icon_list
~~~~~~~~~~~~~~~

.. autofunction:: django_remix_icon.templatetags.remix_icon_tags.remix_icon_list

**Function Signature:**

.. code-block:: python

    def remix_icon_list(category=None, limit=None):
        """
        Get a list of RemixIcon names, optionally filtered by category.

        Args:
            category (str, optional): Filter icons by category
            limit (int, optional): Limit number of icons returned

        Returns:
            list: List of icon names
        """

**Parameters:**

- ``category`` (str, optional): Filter icons containing this string
- ``limit`` (int, optional): Maximum number of icons to return

**Returns:**

``list`` of icon name strings.

**Usage:**

.. code-block:: html

    <!-- Get all icons -->
    {% remix_icon_list as all_icons %}

    <!-- Get user-related icons -->
    {% remix_icon_list category='user' as user_icons %}

    <!-- Get limited icons -->
    {% remix_icon_list limit=20 as featured_icons %}

    <!-- Combine filters -->
    {% remix_icon_list category='home' limit=5 as home_icons %}

**Examples:**

.. code-block:: html

    <!-- Icon picker -->
    {% remix_icon_list category='user' limit=10 as user_icons %}
    <div class="icon-picker">
        {% for icon in user_icons %}
            <button data-icon="{{ icon }}">
                {% remix_icon icon %}
                <small>{{ icon }}</small>
            </button>
        {% endfor %}
    </div>

    <!-- Icon count -->
    {% remix_icon_list as all_icons %}
    <p>{{ all_icons|length }} icons available</p>

Template Filters
----------------

is_remix_icon
~~~~~~~~~~~~~

.. autofunction:: django_remix_icon.templatetags.remix_icon_tags.is_remix_icon

**Function Signature:**

.. code-block:: python

    def is_remix_icon(icon_name):
        """
        Check if a string is a valid RemixIcon name.

        Args:
            icon_name (str): The icon name to check

        Returns:
            bool: True if valid RemixIcon name, False otherwise
        """

**Parameters:**

- ``icon_name`` (str): The string to validate

**Returns:**

``bool`` indicating if the icon name is valid.

**Usage:**

.. code-block:: html

    {% if menu_item.icon|is_remix_icon %}
        {% remix_icon menu_item.icon %}
        {{ menu_item.name }}
    {% else %}
        <span class="no-icon">{{ menu_item.name }}</span>
    {% endif %}

**Examples:**

.. code-block:: html

    <!-- Conditional rendering -->
    {% for item in items %}
        <li class="menu-item">
            {% if item.icon|is_remix_icon %}
                {% remix_icon item.icon class='menu-icon' %}
            {% endif %}
            <span>{{ item.name }}</span>
        </li>
    {% endfor %}

    <!-- With default fallback -->
    {% for post in posts %}
        <article>
            <h2>
                {% if post.category.icon|is_remix_icon %}
                    {% remix_icon post.category.icon %}
                {% else %}
                    {% remix_icon 'ri-article-line' %}
                {% endif %}
                {{ post.title }}
            </h2>
        </article>
    {% endfor %}

Usage Patterns
--------------

Basic Icon Rendering
~~~~~~~~~~~~~~~~~~~~

.. code-block:: html

    <!-- Simple icon -->
    {% remix_icon 'ri-home-line' %}

    <!-- Icon with model field -->
    {% remix_icon user.profile.icon %}

    <!-- Icon with size -->
    {% remix_icon 'ri-star-fill' size='20' %}

Icon Buttons
~~~~~~~~~~~~

.. code-block:: html

    <button type="button" class="btn btn-primary">
        {% remix_icon 'ri-save-line' size='16' %}
        Save Changes
    </button>

Navigation Menus
~~~~~~~~~~~~~~~~

.. code-block:: html

    <nav>
        {% for item in navigation_items %}
            <a href="{{ item.url }}" class="nav-link">
                {% if item.icon|is_remix_icon %}
                    {% remix_icon item.icon class='nav-icon' %}
                {% endif %}
                {{ item.title }}
            </a>
        {% endfor %}
    </nav>

Status Indicators
~~~~~~~~~~~~~~~~~

.. code-block:: html

    <div class="status-indicator">
        {% if task.completed %}
            {% remix_icon 'ri-check-circle-fill' class='text-success' %}
        {% elif task.in_progress %}
            {% remix_icon 'ri-loader-line' class='text-info spinning' %}
        {% else %}
            {% remix_icon 'ri-circle-line' class='text-muted' %}
        {% endif %}
        {{ task.status_text }}
    </div>

Icon Grids
~~~~~~~~~~~

.. code-block:: html

    <div class="icon-grid">
        {% remix_icon_list category='business' limit=12 as business_icons %}
        {% for icon in business_icons %}
            <div class="icon-item">
                {% remix_icon icon size='32' %}
                <small>{{ icon|slice:"3:" }}</small>
            </div>
        {% endfor %}
    </div>

Form Buttons
~~~~~~~~~~~~

.. code-block:: html

    <form method="post">
        {% csrf_token %}
        {{ form }}
        <div class="form-actions">
            <button type="submit" name="action" value="save">
                {% remix_icon 'ri-save-line' %} Save
            </button>
            <button type="submit" name="action" value="save_continue">
                {% remix_icon 'ri-save-2-line' %} Save & Continue
            </button>
            <a href="{% url 'cancel' %}" class="btn btn-secondary">
                {% remix_icon 'ri-close-line' %} Cancel
            </a>
        </div>
    </form>

Advanced Examples
-----------------

Dynamic Icon Selection
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: html

    <!-- JavaScript-powered icon selector -->
    <div class="dynamic-icon-selector">
        <input type="hidden" name="selected_icon" id="icon-input">
        <div class="current-selection">
            <span id="selected-icon">
                {% remix_icon 'ri-image-line' %}
            </span>
            <span id="selected-name">ri-image-line</span>
        </div>

        <div class="icon-categories">
            {% for category in icon_categories %}
                <div class="category" data-category="{{ category }}">
                    <h4>{{ category|title }}</h4>
                    {% remix_icon_list category=category limit=20 as category_icons %}
                    <div class="icons">
                        {% for icon in category_icons %}
                            <button type="button" class="icon-option" data-icon="{{ icon }}">
                                {% remix_icon icon %}
                            </button>
                        {% endfor %}
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>

    <script>
    document.querySelectorAll('.icon-option').forEach(button => {
        button.addEventListener('click', function() {
            const iconName = this.dataset.icon;
            document.getElementById('icon-input').value = iconName;
            document.getElementById('selected-icon').innerHTML = `<i class="${iconName}"></i>`;
            document.getElementById('selected-name').textContent = iconName;
        });
    });
    </script>

Conditional Icon Display
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: html

    {% for notification in notifications %}
        <div class="notification notification-{{ notification.type }}">
            {% if notification.type == 'success' %}
                {% remix_icon 'ri-check-circle-line' class='text-success' %}
            {% elif notification.type == 'warning' %}
                {% remix_icon 'ri-alert-line' class='text-warning' %}
            {% elif notification.type == 'error' %}
                {% remix_icon 'ri-error-warning-line' class='text-danger' %}
            {% else %}
                {% remix_icon 'ri-information-line' class='text-info' %}
            {% endif %}

            <div class="notification-content">
                <h5>{{ notification.title }}</h5>
                <p>{{ notification.message }}</p>
            </div>
        </div>
    {% endfor %}

Icon with Loading States
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: html

    <button type="submit" class="btn btn-primary" id="save-btn">
        <span class="btn-icon">
            {% remix_icon 'ri-save-line' %}
        </span>
        <span class="btn-text">Save</span>
    </button>

    <script>
    document.getElementById('save-btn').addEventListener('click', function() {
        // Show loading state
        this.querySelector('.btn-icon').innerHTML = '<i class="ri-loader-line spinning"></i>';
        this.querySelector('.btn-text').textContent = 'Saving...';
        this.disabled = true;
    });
    </script>

Performance Considerations
-------------------------

Template Caching
~~~~~~~~~~~~~~~~~

For better performance with large icon lists:

.. code-block:: html

    {% load cache %}
    {% cache 3600 icon_grid %}
        {% remix_icon_list as all_icons %}
        <div class="icon-grid">
            {% for icon in all_icons %}
                {% remix_icon icon %}
            {% endfor %}
        </div>
    {% endcache %}

Lazy Loading
~~~~~~~~~~~~

For pages with many icons:

.. code-block:: html

    <div class="icon-container" data-icons='[{% for icon in icons %}"{{ icon }}"{% if not forloop.last %},{% endif %}{% endfor %}]'>
        <!-- Icons loaded via JavaScript -->
    </div>

    <script>
    // Load icons progressively
    const container = document.querySelector('.icon-container');
    const icons = JSON.parse(container.dataset.icons);

    icons.forEach((icon, index) => {
        setTimeout(() => {
            const iconEl = document.createElement('i');
            iconEl.className = icon;
            container.appendChild(iconEl);
        }, index * 10);
    });
    </script>

Error Handling
--------------

The template tags handle various error conditions gracefully:

**Invalid Icon Names:**

.. code-block:: html

    {% remix_icon 'invalid-icon' %}
    <!-- Renders: <i class="ri-question-line" title="Invalid icon: invalid-icon"></i> -->

**Empty Values:**

.. code-block:: html

    {% remix_icon '' %}
    <!-- Renders: (empty string) -->

    {% remix_icon None %}
    <!-- Renders: (empty string) -->

**Missing Variables:**

.. code-block:: html

    {% remix_icon undefined_variable %}
    <!-- Django template error or empty string depending on settings -->

Best Practices
--------------

1. **Always load RemixIcon CSS:**

.. code-block:: html

    {% load remix_icon_tags %}
    {% remix_icon_css %}

2. **Use conditional rendering for optional icons:**

.. code-block:: html

    {% if item.icon|is_remix_icon %}
        {% remix_icon item.icon %}
    {% endif %}

3. **Provide fallback icons:**

.. code-block:: html

    {% remix_icon item.icon|default:'ri-circle-line' %}

4. **Use semantic HTML with icons:**

.. code-block:: html

    <button type="submit">
        {% remix_icon 'ri-save-line' %}
        <span class="sr-only">Save</span>
    </button>

5. **Cache icon lists for better performance:**

.. code-block:: html

    {% load cache %}
    {% cache 3600 navigation_icons %}
        <!-- Navigation with icons -->
    {% endcache %}
