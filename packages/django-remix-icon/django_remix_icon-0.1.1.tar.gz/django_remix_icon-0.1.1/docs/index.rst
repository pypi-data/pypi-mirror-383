Django RemixIcon
================

A simple Django package for integrating RemixIcon with Django admin and templates.

Django RemixIcon provides seamless integration of the popular RemixIcon library into Django projects, with special focus on Django admin functionality. It includes a custom model field, admin widget with autocomplete, and template tags for easy icon rendering.

Key Features
------------

* **IconField**: Custom Django model field for storing RemixIcon names
* **Admin Integration**: Autocomplete widget with icon preview in Django admin
* **Template Tags**: Simple template tags for rendering icons in templates
* **Inline Support**: Works seamlessly with Django admin inline models
* **Performance**: Efficient autocomplete with search functionality
* **Simple**: Minimal configuration required

Quick Example
-------------

.. code-block:: python

    # models.py
    from django.db import models
    from django_remix_icon.fields import IconField

    class MenuItem(models.Model):
        name = models.CharField(max_length=100)
        icon = IconField()

.. code-block:: html

    <!-- template.html -->
    {% load remix_icon_tags %}

    {% remix_icon_css %}

    <div class="menu-item">
        {% remix_icon menu_item.icon %}
        {{ menu_item.name }}
    </div>

Installation
============

Install the package via pip:

.. code-block:: bash

    pip install django-remix-icon

Add to your Django settings:

.. code-block:: python

    INSTALLED_APPS = [
        # ... your other apps
        'django_remix_icon',
    ]

Include the package URLs in your project's URL configuration:

.. code-block:: python

    # urls.py
    from django.urls import path, include

    urlpatterns = [
        # ... your other URLs
        path('remix-icon/', include('django_remix_icon.urls')),
    ]

Contents
========

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   usage
   template_tags
   customization

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/fields
   api/widgets
   api/templatetags

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   changelog
   contributing
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
