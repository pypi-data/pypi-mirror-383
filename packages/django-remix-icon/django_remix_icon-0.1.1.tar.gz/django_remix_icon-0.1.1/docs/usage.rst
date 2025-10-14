Detailed Usage
==============

This section provides comprehensive information about using Django RemixIcon in your projects.

IconField Reference
-------------------

The ``IconField`` is the core component of Django RemixIcon. It's a custom Django model field that stores RemixIcon names.

Basic Usage
~~~~~~~~~~~

.. code-block:: python

    from django.db import models
    from django_remix_icon.fields import IconField

    class MyModel(models.Model):
        icon = IconField()

Field Parameters
~~~~~~~~~~~~~~~~

The ``IconField`` accepts all standard Django ``CharField`` parameters, plus some custom ones:

.. code-block:: python

    class MyModel(models.Model):
        # Basic field with defaults
        icon = IconField()

        # Optional field
        optional_icon = IconField(blank=True, null=True)

        # With custom max_length (default is 100)
        icon_with_length = IconField(max_length=150)

        # With help text
        icon_with_help = IconField(
            help_text="Select an icon to represent this item"
        )

        # With default value
        icon_with_default = IconField(default='ri-star-line')

Default Values
~~~~~~~~~~~~~~

- ``max_length``: 100 characters
- ``blank``: True
- ``null``: True

Validation
~~~~~~~~~~

The field automatically validates that the stored value is a valid RemixIcon name:

.. code-block:: python

    from django.core.exceptions import ValidationError

    # This will raise ValidationError if 'invalid-icon' is not a valid RemixIcon
    instance = MyModel(icon='invalid-icon')
    instance.full_clean()  # Raises ValidationError

Admin Integration
-----------------

The IconField automatically provides a custom admin widget with autocomplete functionality.

Basic Admin Usage
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.contrib import admin
    from .models import MyModel

    @admin.register(MyModel)
    class MyModelAdmin(admin.ModelAdmin):
        list_display = ('name', 'icon')
        # The icon field will automatically use the custom widget

Custom Admin Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can customize the admin interface further:

.. code-block:: python

    @admin.register(MyModel)
    class MyModelAdmin(admin.ModelAdmin):
        list_display = ('name', 'get_icon_preview')

        def get_icon_preview(self, obj):
            if obj.icon:
                return format_html(
                    '<i class="{}" style="font-size: 16px;"></i> {}',
                    obj.icon, obj.icon
                )
            return "No icon"
        get_icon_preview.short_description = "Icon"

Inline Models
~~~~~~~~~~~~~

The IconField works seamlessly with Django admin inline models:

.. code-block:: python

    class ChildModel(models.Model):
        parent = models.ForeignKey(ParentModel, on_delete=models.CASCADE)
        name = models.CharField(max_length=100)
        icon = IconField()

    class ChildModelInline(admin.TabularInline):
        model = ChildModel
        extra = 1

    @admin.register(ParentModel)
    class ParentModelAdmin(admin.ModelAdmin):
        inlines = [ChildModelInline]

Widget Features
---------------

The admin widget provides several features:

Autocomplete Search
~~~~~~~~~~~~~~~~~~~

- Type to search through available icons
- Search matches icon names and categories
- Results are filtered and sorted by relevance

Icon Preview
~~~~~~~~~~~~

- Live preview of selected icon
- Shows both the icon symbol and name
- Updates automatically when selection changes

Keyboard Navigation
~~~~~~~~~~~~~~~~~~~

- Use arrow keys to navigate search results
- Press Enter to select highlighted icon
- Press Escape to close search results

Working with Icon Data
----------------------

Accessing Icon Information
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # In your models
    class MenuItem(models.Model):
        name = models.CharField(max_length=100)
        icon = IconField()

        def get_icon_display_name(self):
            """Get human-readable icon name"""
            if self.icon:
                return self.icon.replace('ri-', '').replace('-', ' ').title()
            return None

    # In views
    def my_view(request):
        item = MenuItem.objects.get(pk=1)
        icon_name = item.icon
        display_name = item.get_icon_display_name()

Querying Models with Icons
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Filter by icon
    items_with_home_icon = MenuItem.objects.filter(icon='ri-home-line')

    # Filter by icon pattern
    items_with_user_icons = MenuItem.objects.filter(icon__startswith='ri-user')

    # Exclude items without icons
    items_with_icons = MenuItem.objects.exclude(icon__isnull=True)
    items_with_icons = MenuItem.objects.exclude(icon='')

Form Integration
----------------

Using IconField in Custom Forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django import forms
    from django_remix_icon.fields import IconFormField

    class MyForm(forms.Form):
        name = forms.CharField(max_length=100)
        icon = IconFormField()

    # Or with ModelForm
    class MyModelForm(forms.ModelForm):
        class Meta:
            model = MyModel
            fields = ['name', 'icon']
            # The IconField automatically uses IconFormField

Custom Widget Options
~~~~~~~~~~~~~~~~~~~~~

You can customize the widget behavior:

.. code-block:: python

    from django_remix_icon.widgets import IconSelectWidget, IconPreviewWidget

    class MyForm(forms.Form):
        # Use the full widget (default)
        icon = forms.CharField(widget=IconSelectWidget())

        # Use simple preview widget (no autocomplete)
        simple_icon = forms.CharField(widget=IconPreviewWidget())

Performance Considerations
--------------------------

Caching Icon Lists
~~~~~~~~~~~~~~~~~~

The package caches the list of available icons for better performance. If you need to clear the cache:

.. code-block:: python

    from django_remix_icon.remix_icons import get_icon_names

    # The icon list is loaded once and cached
    icons = get_icon_names()

Database Optimization
~~~~~~~~~~~~~~~~~~~~~

Icon field values are stored as strings, so standard string field optimizations apply:

.. code-block:: python

    # Add database index for frequent queries
    class MenuItem(models.Model):
        icon = IconField(db_index=True)

    # Use select_related for foreign keys
    items = MenuItem.objects.select_related().all()

Security Considerations
-----------------------

Input Validation
~~~~~~~~~~~~~~~~

The field automatically validates input against the list of valid RemixIcon names:

.. code-block:: python

    # Safe - only valid icons can be stored
    item = MenuItem(icon='ri-home-line')  # Valid
    item = MenuItem(icon='<script>alert("xss")</script>')  # Will be rejected

XSS Protection
~~~~~~~~~~~~~~

When rendering icons in templates, the template tags are XSS-safe:

.. code-block:: html

    <!-- Safe - the template tag escapes invalid input -->
    {% remix_icon user_input_icon %}

Troubleshooting Common Issues
-----------------------------

Icon Not Displaying
~~~~~~~~~~~~~~~~~~~~

1. Ensure RemixIcon CSS is loaded:

.. code-block:: html

    {% load remix_icon_tags %}
    {% remix_icon_css %}

2. Check that the icon name is valid:

.. code-block:: python

    from django_remix_icon.remix_icons import get_icon_names

    valid_icons = get_icon_names()
    if 'ri-my-icon' not in valid_icons:
        print("Icon not found")

Autocomplete Not Working
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Ensure URLs are properly configured:

.. code-block:: python

    # urls.py
    path('remix-icon/', include('django_remix_icon.urls')),

2. Check JavaScript console for errors
3. Verify CSRF configuration for AJAX requests

Widget Styling Issues
~~~~~~~~~~~~~~~~~~~~~

The widget includes CSS for proper styling, but you may need to adjust for your theme:

.. code-block:: css

    /* Custom CSS to override widget styles */
    .remix-icon-widget .icon-search-input {
        width: 100% !important;
    }

Migration Issues
~~~~~~~~~~~~~~~~

When adding IconField to existing models:

.. code-block:: python

    # Migration will be created automatically
    python manage.py makemigrations

    # For existing data, you may want to set defaults
    class Migration(migrations.Migration):
        operations = [
            migrations.AddField(
                model_name='mymodel',
                name='icon',
                field=IconField(default='ri-star-line'),
            ),
        ]

Best Practices
--------------

1. **Always use null=True, blank=True** for optional icon fields
2. **Provide sensible defaults** for required icon fields
3. **Use descriptive help_text** in admin forms
4. **Test autocomplete functionality** in your deployment environment
5. **Include RemixIcon CSS** in your base templates
6. **Consider caching** for high-traffic applications

Next Steps
----------

- :doc:`template_tags` - Learn about all available template tags
- :doc:`customization` - Customize the widget appearance and behavior
- :doc:`api/fields` - Complete API reference for the IconField
