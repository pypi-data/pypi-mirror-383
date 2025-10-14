Fields API Reference
====================

This page documents the model and form fields provided by Django RemixIcon.

.. automodule:: django_remix_icon.fields
   :members:
   :undoc-members:
   :show-inheritance:

IconField
---------

.. autoclass:: django_remix_icon.fields.IconField
   :members:
   :undoc-members:
   :show-inheritance:

   **Description:**

   A Django model field for storing RemixIcon names. This field extends Django's ``CharField``
   and provides automatic validation and a custom admin widget.

   **Parameters:**

   All parameters from Django's ``CharField`` are supported, plus:

   - ``max_length`` (int, default=100): Maximum length for the icon name
   - ``blank`` (bool, default=True): Allow empty values in forms
   - ``null`` (bool, default=True): Allow NULL values in database

   **Usage:**

   .. code-block:: python

       from django.db import models
       from django_remix_icon.fields import IconField

       class MyModel(models.Model):
           name = models.CharField(max_length=100)
           icon = IconField()
           optional_icon = IconField(blank=True, null=True)

IconFormField
-------------

.. autoclass:: django_remix_icon.fields.IconFormField
   :members:
   :undoc-members:
   :show-inheritance:

   **Description:**

   A Django form field for selecting RemixIcons with autocomplete functionality.
   This field extends Django's ``ChoiceField`` and is automatically used by ``IconField``.

   **Parameters:**

   All parameters from Django's ``ChoiceField`` are supported:

   - ``choices`` (list): Automatically populated with RemixIcon choices
   - ``widget`` (Widget): Defaults to ``IconSelectWidget``

   **Usage:**

   .. code-block:: python

       from django import forms
       from django_remix_icon.fields import IconFormField

       class MyForm(forms.Form):
           icon = IconFormField()

Examples
--------

Basic Model Usage
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django.db import models
    from django_remix_icon.fields import IconField

    class Category(models.Model):
        name = models.CharField(max_length=100)
        icon = IconField()
        description = models.TextField(blank=True)

        def __str__(self):
            return self.name

Required Icon Field
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class MenuItem(models.Model):
        title = models.CharField(max_length=100)
        icon = IconField(blank=False, null=False)  # Required field

Optional Icon Field
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class Page(models.Model):
        title = models.CharField(max_length=200)
        icon = IconField(blank=True, null=True)  # Optional field

Icon Field with Help Text
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class Service(models.Model):
        name = models.CharField(max_length=100)
        icon = IconField(
            help_text="Choose an icon that represents this service"
        )

Icon Field with Default Value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class Status(models.Model):
        name = models.CharField(max_length=50)
        icon = IconField(default='ri-circle-line')

Custom Form Usage
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from django import forms
    from django_remix_icon.fields import IconFormField

    class CustomForm(forms.Form):
        title = forms.CharField(max_length=100)
        icon = IconFormField(required=False)
        description = forms.TextField()

    class ModelForm(forms.ModelForm):
        class Meta:
            model = MyModel
            fields = ['name', 'icon', 'description']
            # IconField automatically uses IconFormField

Field Validation
----------------

The ``IconField`` automatically validates that the stored value is a valid RemixIcon name:

.. code-block:: python

    from django.core.exceptions import ValidationError
    from myapp.models import Category

    # Valid usage
    category = Category(name="Home", icon="ri-home-line")
    category.full_clean()  # No error

    # Invalid usage
    category = Category(name="Invalid", icon="invalid-icon-name")
    try:
        category.full_clean()
    except ValidationError as e:
        print(e)  # Will show validation error

Database Storage
----------------

Icon names are stored as strings in the database:

.. code-block:: sql

    -- Example database schema
    CREATE TABLE myapp_category (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        icon VARCHAR(100)  -- RemixIcon name stored here
    );

    -- Example data
    INSERT INTO myapp_category (name, icon) VALUES
    ('Home', 'ri-home-line'),
    ('Settings', 'ri-settings-line'),
    ('User Profile', 'ri-user-line');

Querying Icon Fields
--------------------

You can query models with icon fields like any other CharField:

.. code-block:: python

    # Filter by specific icon
    home_items = Category.objects.filter(icon='ri-home-line')

    # Filter by icon pattern
    user_items = Category.objects.filter(icon__startswith='ri-user')

    # Exclude items without icons
    items_with_icons = Category.objects.exclude(icon__isnull=True)
    items_with_icons = Category.objects.exclude(icon='')

    # Search in icon names
    heart_items = Category.objects.filter(icon__icontains='heart')

Migration Considerations
-----------------------

When adding IconField to existing models:

.. code-block:: python

    # Generated migration
    from django.db import migrations
    from django_remix_icon.fields import IconField

    class Migration(migrations.Migration):
        dependencies = [
            ('myapp', '0001_initial'),
        ]

        operations = [
            migrations.AddField(
                model_name='category',
                name='icon',
                field=IconField(blank=True, null=True),
            ),
        ]

Setting default values for existing records:

.. code-block:: python

    # Data migration to set default icons
    from django.db import migrations

    def set_default_icons(apps, schema_editor):
        Category = apps.get_model('myapp', 'Category')
        for category in Category.objects.all():
            if not category.icon:
                category.icon = 'ri-bookmark-line'  # Default icon
                category.save()

    class Migration(migrations.Migration):
        dependencies = [
            ('myapp', '0002_add_icon_field'),
        ]

        operations = [
            migrations.RunPython(set_default_icons),
        ]
